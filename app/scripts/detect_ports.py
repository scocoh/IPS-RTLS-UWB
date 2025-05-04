# Name: detect_ports.py
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

"""# VERSION 250316 /home/parcoadmin/parco_fastapi/app/scripts/detect_ports.py 0P.10B.01
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
import paho.mqtt.publish as publish
from process_mapper import get_service_name
from concurrent.futures import ThreadPoolExecutor

# MQTT Configuration
MQTT_BROKER = "192.168.210.226"  # Change if different
MQTT_TOPIC = "homeassistant/sensor/rtls_ports"

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

def get_open_ports(host="192.168.210.226", port_range=(5000, 9000)):
    """Scans ports and finds open ones."""
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
        payload = json.dumps({"services": open_ports})
        logging.info(f"Publishing to MQTT: {payload}")
        publish.single(MQTT_TOPIC, payload, hostname=MQTT_BROKER)
        logging.info("✅ MQTT Publish Successful")
    except Exception as e:
        logging.error(f"❌ ERROR: Failed to publish to MQTT -> {e}")

if __name__ == "__main__":
    detected_ports = get_open_ports()
    publish_to_mqtt(detected_ports)
