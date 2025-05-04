# Name: test_db_connection.py
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

# test_db_connection.py
from db_connection_pac import get_db_connection, release_db_connection
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

conn = get_db_connection()
if conn:
    logger.info("Database connection established successfully.")
    release_db_connection(conn)
else:
    logger.error("Failed to establish database connection.")