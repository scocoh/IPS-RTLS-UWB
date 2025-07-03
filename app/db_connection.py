# Name: db_connection.py
# Version: 0.1.1
# Created: 971201
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend - Updated to use database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
db_connection.py - Database connection module for ParcoRTLS
Version: 250702 db_connection.py Version 0P.6B.1G
ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import psycopg2
import logging
from db_config_helper import config_helper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for database configuration
_cached_db_config = None

def get_db_config():
    """Get database configuration from helper (with caching)"""
    global _cached_db_config
    if _cached_db_config is None:
        db_configs = config_helper.get_database_configs()
        _cached_db_config = {
            'dbname': db_configs['maint']['database'],
            'user': db_configs['maint']['user'],
            'password': db_configs['maint']['password'],
            'host': db_configs['maint']['host'],
            'port': str(db_configs['maint']['port'])
        }
        logger.info(f"Database configuration loaded: host={_cached_db_config['host']}")
    return _cached_db_config

# Backward compatibility: Keep DB_CONFIG for existing code that might reference it
# This will use fallback values initially
DB_CONFIG = get_db_config()

def get_db_connection():
    """Establish a new database connection using database-driven configuration"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        logger.info("Database connection established successfully.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def release_db_connection(conn):
    """Safely close database connection"""
    try:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")

def refresh_db_config():
    """Clear cached database configuration to force reload"""
    global _cached_db_config
    _cached_db_config = None
    logger.info("Database configuration cache cleared")