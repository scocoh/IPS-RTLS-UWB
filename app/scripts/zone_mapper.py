# Name: zone_mapper.py
# Version: 0.1.1
# Created: 971201
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & AI Assistant
# Description: Python script for ParcoRTLS backend - Updated to use database-driven configuration
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
import sys
import asyncio

# Add import for db_config_helper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config_helper import config_helper

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

VERSION = "0P.1B.26"  # Bumped version for database-driven configuration

# Global for caching database config
_db_config = None
_mqtt_host = None

async def get_db_config():
    """Get database configuration from tlkresources table"""
    global _db_config
    if _db_config is None:
        try:
            server_config = await config_helper.get_server_config()
            host = server_config.get('host', '192.168.210.226')
            _db_config = {
                'dbname': 'ParcoRTLSMaint',
                'user': 'parcoadmin',
                'password': 'parcoMCSE04106!',
                'host': host,
                'port': '5432'
            }
            logger.info(f"Database configuration loaded for host: {host}")
        except Exception as e:
            logger.warning(f"Failed to load config from database, using fallback: {e}")
            _db_config = {
                'dbname': 'ParcoRTLSMaint',
                'user': 'parcoadmin',
                'password': 'parcoMCSE04106!',
                'host': '192.168.210.226',
                'port': '5432'
            }
    return _db_config

async def get_mqtt_host():
    """Get MQTT host from database configuration"""
    global _mqtt_host
    if _mqtt_host is None:
        try:
            server_config = await config_helper.get_server_config()
            _mqtt_host = server_config.get('host', '192.168.210.226')
            logger.info(f"MQTT host configured: {_mqtt_host}")
        except Exception as e:
            logger.warning(f"Failed to get MQTT host from database, using fallback: {e}")
            _mqtt_host = '192.168.210.226'
    return _mqtt_host

def get_db_connection(db_config):
    """Establish a new database connection with provided credentials"""
    try:
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

async def send_mqtt_message(message):
    """Send message via MQTT"""
    try:
        mqtt_host = await get_mqtt_host()
        mqtt_publish.single(
            "parco/zone_mapper",
            json.dumps(message),
            hostname=mqtt_host,
            port=1883
        )
        logger.info(f"MQTT message sent to {mqtt_host}: {json.dumps(message)}")
    except Exception as e:
        logger.error(f"Failed to send MQTT message: {e}")

async def map_zones():
    logger.info(f"Starting zone_mapper.py Version: {VERSION}")
    await send_mqtt_message({"version": VERSION, "status": "Zone Mapper Service Started"})
    logger.info("Starting zone mapping process with test log...")

    db_config = await get_db_config()
    conn = get_db_connection(db_config)
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
            target_map = 24  # Hardcode to map ID 24 (Boom2502271142) since it's the only map with image data
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
        await send_mqtt_message({"version": VERSION, "status": f"Updated/Inserted {updated_count} zones"})

    except Error as e:
        logger.error(f"Database error during zone mapping: {str(e)}")
        conn.rollback()
    finally:
        release_db_connection(conn)

    logger.info("Zone mapping process completed.")
    await send_mqtt_message({"version": VERSION, "status": "Zone mapping process completed"})

def main():
    """Main entry point for running as script"""
    asyncio.run(map_zones())

if __name__ == "__main__":
    main()