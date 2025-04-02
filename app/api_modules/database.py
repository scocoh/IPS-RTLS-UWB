"""
Version: 250227 db_connection.py Version 0P.1D.01

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import psycopg2
import logging

# ✅ Configure Logging
logging.basicConfig(filename="/home/parcoadmin/parco_fastapi/app/api_modules/db_connection.log", 
                    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Database Connection Config
DB_CONFIG = {
    'dbname': 'ParcoRTLSMaint',
    'user': 'parcoadmin',
    'password': 'parcoMCSE04106!',
    'host': '192.168.210.226',
    'port': '5432'
}

def get_db_connection():
    """Establish a new database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("Database connection established successfully.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        return None

def release_db_connection(conn):
    """Safely close database connection"""
    try:
        if conn:
            conn.close()
            logging.info("Database connection closed.")
    except Exception as e:
        logging.error(f"Error closing database connection: {e}")