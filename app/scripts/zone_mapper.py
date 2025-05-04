# Name: zone_mapper.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/scripts
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Version: 250227 zone_mapper.py Version 0P.1B.25

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import logging
import psycopg2
from psycopg2 import Error
import os
import paho.mqtt.publish as mqtt_publish
import json

# ✅ Hardcode database credentials
DB_CONFIG = {
    'dbname': 'ParcoRTLSMaint',
    'user': 'parcoadmin',
    'password': 'parcoMCSE04106!',
    'host': '192.168.210.226',
    'port': '5432'
}

# Logging configuration
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, mode=0o755)
LOG_FILE = os.path.join(LOG_DIR, "zone_mapper.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

VERSION = "0P.1B.25"

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

def send_mqtt_message(message):
    """Send message via MQTT"""
    try:
        mqtt_publish.single(
            "parco/zone_mapper",
            json.dumps(message),
            hostname="192.168.210.226",
            port=1883
        )
        logger.info(f"MQTT message sent: {json.dumps(message)}")
    except Exception as e:
        logger.error(f"Failed to send MQTT message: {e}")

def map_zones():
    logger.info(f"Starting zone_mapper.py Version: {VERSION}")
    send_mqtt_message({"version": VERSION, "status": "Zone Mapper Service Started"})
    logger.info("Starting zone mapping process with test log...")

    conn = get_db_connection()
    if not conn:
        logger.error("Database connection failed. Exiting.")
        return

    try:
        cur = conn.cursor()

        # Fetch unassociated zones (Campus L1 zones with null i_map)
        logger.debug("Executing query to fetch unassociated zones:")
        cur.execute("""
            SELECT z.i_zn, z.x_nm_zn, z.i_map
            FROM zones z
            WHERE z.i_typ_zn = 1 AND (z.i_map IS NULL OR z.i_map NOT IN (
                SELECT i_map FROM maps WHERE img_data IS NOT NULL
            ));
        """)
        unassociated_zones = cur.fetchall()
        logger.debug(f"Fetched unassociated zones: {unassociated_zones}")

        # Fetch maps with image data
        logger.debug("Executing query to fetch maps with images:")
        cur.execute("""
            SELECT i_map FROM maps WHERE img_data IS NOT NULL;
        """)
        maps_with_images = {row[0] for row in cur.fetchall()}
        logger.debug(f"Maps with images: {maps_with_images}")

        updated_count = 0
        for zone_id, zone_name, current_map in unassociated_zones:
            # Use the first available map with image data (e.g., map 24)
            target_map = 24  # Hardcode to map ID 24 (Boom2502271142) since it’s the only map with image data
            if target_map in maps_with_images:
                logger.debug(f"Processing zone {zone_id} ({zone_name}) with map {target_map}")
                cur.execute("""
                    UPDATE zones
                    SET i_map = %s
                    WHERE i_zn = %s;
                """, (target_map, zone_id))
                conn.commit()
                updated_count += 1
                logger.info(f"Associated zone {zone_id} ({zone_name}) with map {target_map}")
            else:
                logger.warning(f"Map {target_map} has no image data. Skipping association for zone {zone_id} ({zone_name}).")

        logger.info(f"Updated/Inserted {updated_count} map associations successfully.")
        send_mqtt_message({"version": VERSION, "status": f"Updated/Inserted {updated_count} zones"})

    except Error as e:
        logger.error(f"Database error during zone mapping: {str(e)}")
        conn.rollback()
    finally:
        release_db_connection(conn)

    logger.info("Zone mapping process completed.")
    send_mqtt_message({"version": VERSION, "status": "Zone mapping process completed"})

if __name__ == "__main__":
    map_zones()