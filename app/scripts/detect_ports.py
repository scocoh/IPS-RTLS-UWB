# Name: detect_ports.py
# Version: 0.1.1
# Created: 971201
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend - Updated to use database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app/scripts
# Role: Backend
# Status: Active
# Dependent: TRUE

"""# VERSION 250702 /home/parcoadmin/parco_fastapi/app/scripts/detect_ports.py 0P.10B.02
#  
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""
import socket
import json
import logging
import asyncio
import sys
import os
import paho.mqtt.publish as publish
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config_helper import config_helper
from process_mapper import get_service_name

# Cache for server configuration
_cached_server_config = None

async def get_server_config():
    """Get server configuration from database"""
    global _cached_server_config
    if _cached_server_config is None:
        _cached_server_config = await config_helper.get_server_config()
        logging.info(f"Server configuration loaded: host={_cached_server_config.get('host', 'unknown')}")
    return _cached_server_config

def get_server_host():
    """Get server host synchronously (with fallback)"""
    global _cached_server_config
    if _cached_server_config:
        return _cached_server_config.get('host', '192.168.210.226')
    # Fallback if config not loaded yet
    return '192.168.210.226'

def get_mqtt_broker():
    """Get MQTT broker host - typically same as server host"""
    return get_server_host()

# Logging Configuration (with Log Rotation)
log_file = "/var/log/detect_ports.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def is_port_open(host, port):
    """Check if a port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

async def get_open_ports(host=None, port_range=(5000, 9000)):
    """Scans ports and finds open ones."""
    if host is None:
        server_config = await get_server_config()
        host = server_config.get('host', '192.168.210.226')
    
    logging.info(f"Scanning ports on host: {host}")
    open_ports = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = {port: executor.submit(is_port_open, host, port) for port in range(port_range[0], port_range[1])}

    for port, future in results.items():
        if future.result():
            service = get_service_name(port)
            logging.info(f"Detected service for port {port} -> {service}")
            open_ports[port] = service

    return open_ports

def publish_to_mqtt(open_ports):
    """Publishes detected ports to MQTT."""
    try:
        mqtt_broker = get_mqtt_broker()
        mqtt_topic = "homeassistant/sensor/rtls_ports"
        
        payload = json.dumps({"services": open_ports})
        logging.info(f"Publishing to MQTT broker {mqtt_broker}: {payload}")
        publish.single(mqtt_topic, payload, hostname=mqtt_broker)
        logging.info("✅ MQTT Publish Successful")
    except Exception as e:
        logging.error(f"❌ ERROR: Failed to publish to MQTT -> {e}")

async def main():
    """Main async function to run port detection"""
    try:
        # Load server configuration from database
        await get_server_config()
        
        # Detect open ports
        detected_ports = await get_open_ports()
        
        # Publish to MQTT
        publish_to_mqtt(detected_ports)
        
        logging.info(f"Port detection completed. Found {len(detected_ports)} open ports.")
        
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        # Fallback to static configuration
        logging.info("Falling back to static configuration")
        detected_ports = await get_open_ports("192.168.210.226")
        publish_to_mqtt(detected_ports)

if __name__ == "__main__":
    asyncio.run(main())