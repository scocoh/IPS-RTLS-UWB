# Name: tetse_output_handler.py
# Version: 0.1.1
# Created: 971201
# Modified: 250704
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: tetse_output_handler.py
# Version: 0.1.1
# Created: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: (Phase 6C.3B )
# Status: Production-ready

# Location: /home/parcoadmin/parco_fastapi/app/routes

# Import centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host

import logging
import asyncio
import json
import paho.mqtt.client as mqtt
from routes.tetse_event_dispatcher import enqueue_event

# =============================================================================
# TETSE Output Handler - Phase 6C.3B
# =============================================================================

# MQTT Settings (adjust if needed)
MQTT_BROKER = get_server_host()
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "tetse/events"

# Setup local logger for output tracking
logger = logging.getLogger("TETSE_OUTPUT")
logger.setLevel(logging.DEBUG)

# Initialize MQTT Client (non-blocking)
mqtt_client = mqtt.Client()

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    logger.info("MQTT client connected successfully.")
except Exception as e:
    logger.error(f"Failed to connect to MQTT broker: {str(e)}")

async def process_tetse_result(subject_id: str, rule: dict, result: dict):
    """
    Updated version: Send all triggered outputs into dispatcher queue.
    """
    try:
        if result.get("triggered"):
            logger.info(f"TRIGGERED: Subject={subject_id} Rule={rule['name']} Result={result}")
            await enqueue_event(subject_id, rule["name"], result)
        else:
            logger.debug(f"No trigger for Subject={subject_id} Rule={rule['name']}")
    except Exception as e:
        logger.error(f"Error processing TETSE result: {str(e)}")