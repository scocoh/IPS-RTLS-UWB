# Name: db_connection_pac.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
db_connection.py - Database connection module for ParcoRTLS
Version: 250227 db_connection.py Version 0P.6B.1F
ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import psycopg2
import logging

# ✅ Hardcode database credentials
DB_CONFIG = {
    'dbname': 'ParcoRTLSMaint',
    'user': 'parcoadmin',
    'password': 'parcoMCSE04106!',
    'host': '192.168.210.226',
    'port': '5432'
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Establish a new database connection with hardcoded credentials"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
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