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