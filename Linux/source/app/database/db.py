"""
database/db.py
Version: 0.1.5 (Enhanced debug logging for execute_raw_query)
Database connection management for ParcoRTLS FastAPI application.
"""

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
    # [Existing code unchanged]
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
            # [Existing retry logic unchanged]
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
            # [Existing retry logic unchanged]
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
        from app import app
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
            # Fallback to raw query for SELECT operations (assuming SELECT-like behavior)
            if procedure_name.startswith("usp_") and "select" in procedure_name.lower():
                table_name = procedure_name.replace("usp_", "").replace("_select", "").lower()
                if table_name == "device_select_by_id":
                    table_name = "devices"
                    query = f"SELECT * FROM public.{table_name} WHERE x_id_dev = $1"
                    logger.debug(f"Falling back to raw query: {query} with args: {args}")
                    rows = await connection.fetch(query, *args[0])  # Use only the first arg for device_id
                    logger.debug(f"Raw query result: {rows}")
                    if rows:
                        return [dict(row) for row in rows]
                    return None
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

    Args:
        db_type (str): The database type (e.g., "maint", "data").
        query (str): The raw SQL query to execute.
        *args: Variable arguments to pass to the query.
        pool (Optional[asyncpg.Pool]): An optional connection pool; if None, uses app.state.async_db_pools.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the query results.

    Raises:
        HTTPException: If the query fails or the database is unavailable.
    """
    if pool is None:
        from app import app
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
            logger.debug(f"Raw query result (before dict conversion): {rows}")
            logger.debug(f"Raw query result (after dict conversion): {[dict(row) for row in rows]}")
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
    from app import app
    if hasattr(app.state, "async_db_pools"):
        for db_type, pool in app.state.async_db_pools.items():
            if pool:
                await pool.close()
                logger.info(f"Closed connection pool for {db_type}")