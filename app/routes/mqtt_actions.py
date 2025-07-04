# Name: mqtt_actions.py
# Version: 0.1.1
# Created: 250601
# Modified: 250704
# Creator: ParcoAdmin
# Location: /home/parcoadmin/parco_fastapi/app/routes/mqtt_actions.py
# Role: MQTT Integration for TETSE Actions
# Status: Active
# Dependent: TRUE

# Import centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host

import paho.mqtt.client as mqtt
import logging
from manager.line_limited_logging import LineLimitedFileHandler

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("manager.mqtt_actions")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
file_handler = LineLimitedFileHandler(
    os.path.join(LOG_DIR, "mqtt_actions.log"),
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
logger.handlers = [console_handler, file_handler]
logger.propagate = False

class MQTTClient:
    def __init__(self, broker=None, port=1883, username=None, password=None):
        if broker is None:
            broker = get_server_host()
        self.client = mqtt.Client()
        if username and password:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.broker = broker
        self.port = port

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to MQTT broker with code {rc}")

    def on_publish(self, client, userdata, mid):
        logger.debug(f"Message {mid} published")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            logger.info("MQTT client connected")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            raise

    def publish(self, topic: str, payload: str):
        try:
            result = self.client.publish(topic, payload)
            logger.info(f"Published to {topic}: {payload}")
            return result
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {str(e)}")
            raise

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")