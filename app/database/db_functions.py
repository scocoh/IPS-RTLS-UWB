# Name: db_functions.py
# Version: 0.1.1
# Created: 971201
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend - Updated to use database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app/database
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/database/db_functions.py
Version: 250702 db_functions.py Version 0P.7B.27 (Updated to use database-driven configuration instead of hardcoded IP addresses)

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
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config_helper import config_helper

# Configure logging
logger = logging.getLogger(__name__)

# Custom exception for database errors
class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Cache for database configurations
_cached_db_configs = None

def get_db_configs_async():
    """Get database configurations from helper (with caching)"""
    global _cached_db_configs
    if _cached_db_configs is None:
        _cached_db_configs = config_helper.get_database_configs()
        host = _cached_db_configs['maint']['host']
        logger.info(f"Database configurations loaded: host={host}")
    return _cached_db_configs

# Backward compatibility: Keep DB_CONFIGS_ASYNC for existing code
# This will use fallback values initially
DB_CONFIGS_ASYNC = get_db_configs_async()

async def get_pg_connection(db_type: str = "maint") -> Optional[asyncpg.Pool]:
    """Establish an async database connection pool with optimized settings, increased max_size, and enhanced retry logic for connection issues."""
    
    # Get current database configurations
    db_configs = get_db_configs_async()
    
    if db_type not in db_configs:
        logger.error(f"Database type '{db_type}' not found in configurations")
        return None
    
    config = db_configs[db_type]
    
    try:
        logger.debug(f"Creating connection pool for {db_type} at {config['host']}:{config['port']}")
        
        pool = await asyncpg.create_pool(
            database=config["database"],
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
            min_size=2,
            max_size=20,
            timeout=30,
            command_timeout=60,
            server_settings={
                'application_name': f'ParcoRTLS_{db_type}',
                'tcp_keepalives_idle': '600',
                'tcp_keepalives_interval': '30',
                'tcp_keepalives_count': '3'
            }
        )
        
        # Test the connection
        async with pool.acquire() as connection:
            await connection.execute("SELECT 1")
        
        logger.info(f"✅ Database pool created successfully for {db_type} at {config['host']}")
        return pool
        
    except Exception as e:
        logger.error(f"❌ Error creating async database pool for {db_type}: {e}")
        logger.debug(f"Failed connection details: {config['host']}:{config['port']}/{config['database']}")
        return None

async def execute_query(query: str, *args, db_type: str = "maint", pool: Optional[asyncpg.Pool] = None) -> List[Dict]:
    """
    Execute a database query with enhanced error handling and logging.
    Returns a list of dictionaries representing the query results.
    
    Args:
        query: SQL query to execute
        *args: Query parameters
        db_type: Database type (maint, data, hist_r, hist_p, hist_o)
        pool: Optional existing connection pool
        
    Returns:
        List of dictionaries with query results
    """
    if pool is None:
        pool = await get_pg_connection(db_type)
        if not pool:
            raise DatabaseError(f"Could not establish connection to {db_type} database")
    
    try:
        async with pool.acquire() as connection:
            logger.debug(f"Executing query on {db_type}: {query[:100]}...")
            rows = await connection.fetch(query, *args)
            
            # Convert to list of dictionaries
            result = [dict(row) for row in rows]
            logger.debug(f"Query returned {len(result)} rows")
            return result
            
    except asyncpg.PostgresError as e:
        error_msg = f"PostgreSQL error in {db_type}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error in {db_type}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg)

async def execute_scalar(query: str, *args, db_type: str = "maint", pool: Optional[asyncpg.Pool] = None) -> any: # type: ignore
    """
    Execute a query and return a single scalar value.
    
    Args:
        query: SQL query to execute
        *args: Query parameters
        db_type: Database type
        pool: Optional existing connection pool
        
    Returns:
        Single scalar value or None
    """
    if pool is None:
        pool = await get_pg_connection(db_type)
        if not pool:
            raise DatabaseError(f"Could not establish connection to {db_type} database")
    
    try:
        async with pool.acquire() as connection:
            logger.debug(f"Executing scalar query on {db_type}: {query[:100]}...")
            result = await connection.fetchval(query, *args)
            logger.debug(f"Scalar query returned: {result}")
            return result
            
    except asyncpg.PostgresError as e:
        error_msg = f"PostgreSQL error in {db_type}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error in {db_type}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg)

def refresh_db_configs():
    """Clear cached database configurations to force reload"""
    global _cached_db_configs, DB_CONFIGS_ASYNC
    _cached_db_configs = None
    DB_CONFIGS_ASYNC = get_db_configs_async()
    logger.info("Database configurations cache cleared")

def get_connection_string(db_type: str = "maint") -> str:
    """
    Get connection string for a specific database type
    
    Args:
        db_type: Database type (maint, data, hist_r, hist_p, hist_o)
        
    Returns:
        PostgreSQL connection string
    """
    db_configs = get_db_configs_async()
    if db_type not in db_configs:
        raise ValueError(f"Database type '{db_type}' not found in configurations")
    
    config = db_configs[db_type]
    return (f"postgresql://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}")

# Backward compatibility functions
async def get_maint_connection() -> Optional[asyncpg.Pool]:
    """Get connection pool for maintenance database"""
    return await get_pg_connection("maint")

async def get_data_connection() -> Optional[asyncpg.Pool]:
    """Get connection pool for data database"""
    return await get_pg_connection("data")

async def get_hist_r_connection() -> Optional[asyncpg.Pool]:
    """Get connection pool for historical R database"""
    return await get_pg_connection("hist_r")

async def get_hist_p_connection() -> Optional[asyncpg.Pool]:
    """Get connection pool for historical P database"""
    return await get_pg_connection("hist_p")

async def get_hist_o_connection() -> Optional[asyncpg.Pool]:
    """Get connection pool for historical O database"""
    return await get_pg_connection("hist_o")