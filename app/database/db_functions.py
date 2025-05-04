# Name: db_functions.py
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

"""
/home/parcoadmin/parco_fastapi/app/database/db_functions.py
Version: 250226 db_functions.py Version 0P.7B.26 (Massive Stored Procedure Integration, Async Enhancements, Type Handling for ParcoRTLSMaint/HistR/Data, Fixed History/Location/Text Data, Connection Pool Tuning, Empty Database Handling, Asyncio Import Fix, Removed HTTPException Dependency, Enhanced Connection Pooling)

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24, Michael Farnsworth, and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import asyncpg
import logging
import asyncio
from datetime import datetime
from typing import Optional, Union, List, Dict

# Configure logging
logger = logging.getLogger(__name__)

# Custom exception for database errors
class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# PostgreSQL Database Configuration
DB_CONFIGS_ASYNC = {
    "maint": {
        "database": "ParcoRTLSMaint",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "data": {
        "database": "ParcoRTLSData",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_r": {
        "database": "ParcoRTLSHistR",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_p": {
        "database": "ParcoRTLSHistP",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_o": {
        "database": "ParcoRTLSHistO",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    }
}

async def get_pg_connection(db_type: str = "maint") -> Optional[asyncpg.Pool]:
    """Establish an async database connection pool with optimized settings, increased max_size, and enhanced retry logic for connection issues."""
    max_retries = 10  # Increased retries to handle "too many clients already" more robustly
    retry_delay = 5  # Increased delay to allow database to recover
    for attempt in range(max_retries):
        try:
            pool = await asyncpg.create_pool(
                **DB_CONFIGS_ASYNC[db_type],
                max_size=20,  # Reduced to prevent overwhelming PostgreSQL, adjust based on server capacity
                min_size=2,
                timeout=30
            )
            # Test the connection by executing a simple query
            async with pool.acquire() as connection:
                await connection.execute("SELECT 1")
            return pool
        except asyncpg.TooManyConnectionsError as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to connect to {db_type}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached for {db_type}: {str(e)}")
                if db_type in ["data", "hist_r", "hist_p", "hist_o"]:
                    logger.warning(f"Database {db_type} connection failed due to too many clients, falling back to maintenance-only mode.")
                    return None  # Return None to indicate connection failure, handled by caller
                raise DatabaseError(f"Failed to connect to {db_type} after retries: too many clients", 503)
        except asyncpg.PostgresError as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to connect to {db_type}: {str(e)}")
            if "database does not exist" in str(e) or "no such database" in str(e):
                logger.warning(f"Database {db_type} may be empty or missing. Falling back to maintenance-only mode.")
                return None  # Return None to indicate empty database, handled by caller
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached for {db_type}: {str(e)}")
                raise DatabaseError(f"Failed to connect to {db_type} after retries", 503)
    raise DatabaseError(f"Failed to connect to {db_type}", 503)

async def call_stored_procedure(db_type: str, procedure_name: str, *args) -> Union[List[Dict], Dict, None]:
    """Call a stored procedure and return results with type-specific handling, handling empty or inaccessible databases."""
    pool = await get_pg_connection(db_type)
    if not pool:
        if db_type in ["data", "hist_r", "hist_p", "hist_o"]:
            logger.warning(f"Database {db_type} is empty, inaccessible, or has too many clients, falling back to maintenance-only mode.")
            if procedure_name in ["usp_textdata_add", "usp_textdata_all_by_device", "usp_position_insert", "usp_location_by_id", "usp_history_by_id"]:
                raise DatabaseError(f"Database {db_type} is empty or unavailable for {procedure_name}", 503)
        raise DatabaseError(f"Failed to connect to {db_type}", 503)

    async with pool.acquire() as connection:
        try:
            # Handle specific procedure signatures with type casting
            if procedure_name == "usp_zone_select_by_id":
                query = "SELECT * FROM usp_zone_select_by_id($1::integer);"
            elif procedure_name == "usp_device_select_by_id":
                query = "SELECT * FROM usp_device_select_by_id($1::character varying);"
            elif procedure_name == "usp_device_select_all":
                query = "SELECT * FROM usp_device_select_all();"
            elif procedure_name == "usp_device_select_by_type":
                query = "SELECT * FROM usp_device_select_by_type($1::integer);"
            elif procedure_name == "usp_device_add":
                query = "SELECT * FROM usp_device_add($1::character varying, $2::integer, $3::character varying, $4::timestamp without time zone);"
            elif procedure_name == "usp_device_delete":
                query = "SELECT * FROM usp_device_delete($1::character varying);"
            elif procedure_name == "usp_device_edit":
                query = "SELECT * FROM usp_device_edit($1::character varying, $2::integer, $3::character varying, $4::timestamp without time zone);"
            elif procedure_name == "usp_assign_dev_add":
                query = "SELECT * FROM usp_assign_dev_add($1::character varying, $2::character varying, $3::integer, $4::timestamp without time zone, $5::timestamp without time zone);"
            elif procedure_name == "usp_zone_select_all":
                query = "SELECT * FROM usp_zone_select_all();"
            elif procedure_name == "usp_trigger_select_by_id":
                query = "SELECT * FROM usp_trigger_select_by_id($1::integer);"
            elif procedure_name == "usp_trigger_edit":
                query = "SELECT * FROM usp_trigger_edit($1::integer, $2::character varying, $3::integer, $4::boolean);"
            elif procedure_name == "usp_location_by_id":
                query = "SELECT * FROM usp_location_by_id($1::character varying);"
            elif procedure_name == "usp_position_insert":
                query = "SELECT * FROM usp_position_insert($1::character varying, $2::timestamp without time zone, $3::timestamp without time zone, $4::real, $5::real, $6::real);"
            elif procedure_name == "usp_history_by_id":
                query = "SELECT * FROM usp_history_by_id($1::character varying, $2::timestamp without time zone, $3::timestamp without time zone);"
            elif procedure_name == "usp_textdata_add":
                query = "SELECT * FROM usp_textdata_add($1::character varying, $2::character varying, $3::timestamp without time zone);"
            elif procedure_name == "usp_textdata_all_by_device":
                query = "SELECT * FROM usp_textdata_all_by_device($1::character varying);"
            else:
                query = f"SELECT * FROM {procedure_name}({', '.join(['$' + str(i+1) + '::text' for i in range(len(args))])});"

            rows = await connection.fetch(query, *args)
            if rows:
                return [dict(row) for row in rows]
            value = await connection.fetchval(query, *args)
            if value is not None:
                return value
            return {"message": "Procedure executed successfully"}
        except asyncpg.PostgresError as e:
            logger.error(f"Error calling stored procedure {procedure_name} in {db_type}: {str(e)}")
            if "function does not exist" in str(e) or "no such function" in str(e):
                raise DatabaseError(f"Stored procedure {procedure_name} not found in {db_type}", 501)
            raise DatabaseError(f"Database error for {procedure_name} in {db_type}: {str(e)}", 500)