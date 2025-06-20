# Name: tetse_event_dispatcher.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: tetse_event_dispatcher.py
# Version: 0.1.0
# Created: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: (Phase 6C.3A )
# Status: Production-ready

# Location: /home/parcoadmin/parco_fastapi/app/routes

import asyncio
import logging
import json
import paho.mqtt.client as mqtt

# =============================================================================
# TETSE Event Dispatcher (Phase 6C.3A)
# =============================================================================

# Global Event Queue
EVENT_QUEUE = asyncio.Queue()

# MQTT Settings
MQTT_BROKER = "192.168.210.226"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "tetse/events"

# Logger setup
logger = logging.getLogger("TETSE_DISPATCHER")
logger.setLevel(logging.DEBUG)

# MQTT client (shared across workers)
mqtt_client = mqtt.Client()

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    logger.info("TETSE Dispatcher connected to MQTT broker.")
except Exception as e:
    logger.error(f"Failed to connect to MQTT broker: {str(e)}")


async def enqueue_event(subject_id: str, rule_name: str, result: dict):
    event = {
        "subject": subject_id,
        "rule": rule_name,
        "status": result["status"],
        "details": result.get("details", {})
    }
    await EVENT_QUEUE.put(event)
    logger.debug(f"Enqueued event: {event}")


async def event_worker():
    while True:
        event = await EVENT_QUEUE.get()
        try:
            await process_event(event)
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
        EVENT_QUEUE.task_done()


async def process_event(event: dict):
    subject_id = event["subject"]
    rule_name = event["rule"]
    topic = f"{MQTT_TOPIC_PREFIX}/{subject_id}/{rule_name}"
    payload = json.dumps(event)
    mqtt_client.publish(topic, payload, qos=0)
    logger.info(f"Dispatched event to MQTT: {topic}")


async def start_dispatcher(num_workers: int = 2):
    for _ in range(num_workers):
        asyncio.create_task(event_worker())
    logger.info(f"TETSE Dispatcher started with {num_workers} workers.")
