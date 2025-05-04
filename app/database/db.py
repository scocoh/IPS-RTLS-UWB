# Name: db.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/database
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/database/db.py
# Version: 0.1.7 - Fixed circular import by moving app import inside functions
import asyncpg
import asyncio
from fastapi import HTTPException
import logging
from typing import Any, Optional, List, Dict, Union
from config import DB_CONFIGS_ASYNC

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def get_async_db_pool(db_type: str = "maint") -> Optional[asyncpg.Pool]:
    max_retries = 10
    retry_delay = 5
    for attempt in range(max_retries):
        try:
            pool = await asyncpg.create_pool(
                **DB_CONFIGS_ASYNC[db_type],
                max_size=20,
                min_size=2,
                timeout=30,
                command_timeout=60
            )
            async with pool.acquire() as connection:
                await connection.execute("SELECT 1")
            logger.info(f"Successfully created connection pool for {db_type}")
            return pool
        except asyncpg.TooManyConnectionsError as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to connect to {db_type}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached for {db_type}: {str(e)}")
                if db_type in ["data", "hist_r", "hist_p", "hist_o"]:
                    logger.warning(f"Database {db_type} connection failed due to too many clients, falling back to maintenance-only mode.")
                    return None
                raise HTTPException(status_code=503, detail=f"Failed to connect to {db_type} after retries: too many clients")
        except asyncpg.PostgresError as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to connect to {db_type}: {str(e)}")
            if "database does not exist" in str(e) or "no such database" in str(e):
                logger.warning(f"Database {db_type} may be empty or missing. Falling back to maintenance-only mode.")
                return None
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached for {db_type}: {str(e)}")
                raise HTTPException(status_code=503, detail=f"Failed to connect to {db_type} after retries: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to {db_type}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise HTTPException(status_code=503, detail=f"Unexpected error connecting to {db_type}: {str(e)}")
    raise HTTPException(status_code=503, detail=f"Failed to connect to {db_type}")

async def call_stored_procedure(db_type: str, procedure_name: str, *args, pool: Optional[asyncpg.Pool] = None) -> Union[List[Dict[str, Any]], Any]:
    """Call a stored procedure and return its results, with fallback for missing procedures."""
    if pool is None:
        from app import app  # Moved import inside function to avoid circular import
        pool = app.state.async_db_pools.get(db_type)
        if not pool:
            logger.warning(f"No connection pool available for {db_type}. Attempting to create one.")
            pool = await get_async_db_pool(db_type)
            if not pool:
                raise HTTPException(status_code=503, detail=f"Database {db_type} is unavailable")
            app.state.async_db_pools[db_type] = pool

    async with pool.acquire() as connection:
        try:
            placeholders = ", ".join([f"${i+1}" for i in range(len(args))])
            query = f"SELECT * FROM {procedure_name}({placeholders})"
            logger.debug(f"Executing query: {query} with args: {args}")
            rows = await connection.fetch(query, *args)
            logger.debug(f"Query result: {rows}")
            if rows:
                return [dict(row) for row in rows]
            value = await connection.fetchval(query, *args)
            if value is not None:
                return value
            return {"message": f"Procedure {procedure_name} executed successfully"}
        except asyncpg.UndefinedFunctionError as e:
            error_msg = f"Stored procedure {procedure_name} does not exist in {db_type}: {str(e)}"
            logger.warning(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        except asyncpg.PostgresError as e:
            error_msg = f"Error calling {procedure_name} in {db_type}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, 500)
        except Exception as e:
            error_msg = f"Unexpected error calling {procedure_name} in {db_type}: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

async def execute_raw_query(db_type: str, query: str, *args, pool: Optional[asyncpg.Pool] = None) -> List[Dict[str, Any]]:
    """
    Execute a raw SQL query and return the results.
    Logs are now sanitized to avoid logging binary (bytea) fields.
    """
    if pool is None:
        from app import app  # Moved import inside function to avoid circular import
        pool = app.state.async_db_pools.get(db_type)
        if not pool:
            logger.warning(f"No connection pool available for {db_type}. Attempting to create one.")
            pool = await get_async_db_pool(db_type)
            if not pool:
                raise HTTPException(status_code=503, detail=f"Database {db_type} is unavailable")
            app.state.async_db_pools[db_type] = pool

    async with pool.acquire() as connection:
        try:
            logger.debug(f"Executing raw query: {query} with args: {args}")
            rows = await connection.fetch(query, *args)

            # 🔐 Sanitize binary results before logging
            def sanitize(row):
                return {
                    k: (f"<{len(v)} bytes>" if isinstance(v, (bytes, bytearray)) else v)
                    for k, v in dict(row).items()
                }

            safe_preview = [sanitize(row) for row in rows]
            logger.debug(f"Raw query result (sanitized): {safe_preview}")

            return [dict(row) for row in rows]
        except asyncpg.PostgresError as e:
            error_msg = f"Error executing raw query in {db_type}: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error executing raw query in {db_type}: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

async def close_db_pools():
    from app import app  # Moved import inside function to avoid circular import
    if hasattr(app.state, "async_db_pools"):
        for db_type, pool in app.state.async_db_pools.items():
            if pool:
                await pool.close()
                logger.info(f"Closed connection pool for {db_type}")