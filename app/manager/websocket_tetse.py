# Name: websocket_tetse.py
# Version: 0.1.8
# Created: 250526
# Modified: 250704
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: WebSocket Server on port 8998 to forward events from main app to TETSE WebSocket server - Updated with centralized IP configuration
# Location: /home/parcoadmin/parco_fastapi/app/manager/websocket_tetse.py
# Role: WebSocket Interface for TETSE Event Forwarding
# Status: Active
# Dependent: TRUE
#
# Version: 0.1.8 - Updated to use centralized IP configuration and fixed syntax errors, bumped from 0.1.7
# Version: 0.1.7 - Enhanced with HTTP endpoint for position events and TETSE rule evaluation, bumped from 0.1.6
# Version: 0.1.6 - Increased response timeout, added detailed logging, bumped from 0.1.5
# Version: 0.1.5 - Handle non-JSON responses from TETSE server, bumped from 0.1.4
# Version: 0.1.4 - Added heartbeat filtering in response forwarding, bumped from 0.1.3
# Version: 0.1.3 - Fixed response forwarding in forward_event_handler, added debug logging, bumped from 0.1.2
# Version: 0.1.2 - Integrated HeartbeatManager, removed manual rate-limiting, bumped from 0.1.1
# Version: 0.1.1 - Added heartbeat rate-limiting, EndStream forwarding, and LineLimitedFileHandler, bumped from 0.1.0
# Version: 0.1.0 - Initial implementation of WebSocket server on port 8998 for event forwarding

import logging
import os
import asyncio
import json
import sys
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from manager.line_limited_logging import LineLimitedFileHandler
from .heartbeat_manager import HeartbeatManager
from routes.device_registry import get_subject_for_tag
from routes import tetse_reload
from routes.tetse_rule_engine import evaluate_rule
from routes.tetse_output_handler import process_tetse_result
from pydantic import BaseModel
from typing import Optional

# Import centralized configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("manager.websocket_tetse")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

file_handler = LineLimitedFileHandler(
    os.path.join(LOG_DIR, "websocket_tetse.log"),
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

logger.handlers = [console_handler, file_handler]
logger.propagate = False

logger.info("Starting WebSocket TETSE Forwarding server on port 8998 - Enhanced for position events")
file_handler.flush()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
logger.debug("CORS middleware added with allow_origins: *")
file_handler.flush()

class EventBroadcast(BaseModel):
    entity_id: str
    event_data: dict

@app.post("/broadcast_event")
async def broadcast_event_http(event: EventBroadcast):
    """
    HTTP endpoint to receive events from RealTime WebSocket and process them for TETSE.
    This is the clean event bridge that separates RTLS from TETSE logic.
    """
    try:
        logger.info(f"Received event from RTLS bridge for entity {event.entity_id}")
        
        # Extract position data from event
        event_data = event.event_data
        if event_data.get("event_type") == "position_update":
            tag_id = event_data.get("tag_id")
            zone_id = event_data.get("zone_id")
            
            logger.debug(f"🔄 TETSE BRIDGE: Processing position update for tag_id={tag_id}, zone_id={zone_id}")
            
            # TETSE rule evaluation (moved from RealTime WebSocket)
            try:
                # Ensure tag_id is a string before passing to get_subject_for_tag
                if tag_id is not None and isinstance(tag_id, (str, int)):
                    tag_id_str = str(tag_id)
                    subject_id = get_subject_for_tag(tag_id_str)
                    logger.debug(f"🔄 TETSE BRIDGE: tag_id={tag_id_str}, subject_id={subject_id}")
                    
                    if subject_id:
                        logger.debug(f"🔄 TETSE BRIDGE: Found subject {subject_id}, checking rules for zone {zone_id}")
                        
                        matching_rules = [r for r in tetse_reload.ACTIVE_TETSE_RULES if r["subject_id"] == subject_id]
                        logger.debug(f"🔄 TETSE BRIDGE: Found {len(matching_rules)} matching rules for subject {subject_id}")
                        
                        for rule in matching_rules:
                            logger.debug(f"🔄 TETSE BRIDGE: Evaluating rule {rule.get('name', 'unnamed')} for subject {subject_id}")
                            # FIXED: Ensure zone_id is an integer before passing to evaluate_rule
                            if zone_id is not None and isinstance(zone_id, (str, int)):
                                zone_id_int = int(zone_id)
                                result = await evaluate_rule(rule, current_zone_id=zone_id_int)
                                logger.debug(f"🔄 TETSE BRIDGE: Rule evaluation result: {result}")
                                logger.info(f"TETSE Bridge Eval: Subject={subject_id} Rule={rule['name']} Result={result}")
                                await process_tetse_result(subject_id, rule, result)
                            else:
                                logger.warning(f"🔄 TETSE BRIDGE: Invalid zone_id: {zone_id}")
                    else:
                        logger.debug(f"🔄 TETSE BRIDGE: No subject mapping found for tag {tag_id_str}")
                else:
                    logger.warning(f"🔄 TETSE BRIDGE: Invalid tag_id: {tag_id}")
                    
            except Exception as e:
                logger.error(f"🔄 TETSE BRIDGE: Exception in TETSE evaluation: {str(e)}")
        
        # Forward to TETSE WebSocket server (existing logic)
        server_host = get_server_host()
        tetse_url = f"ws://{server_host}:9000/broadcast_event_ws"
        async with websockets.connect(tetse_url, timeout=5.0) as tetse_ws:
            await tetse_ws.send(json.dumps({
                "entity_id": event.entity_id,
                "event_data": event.event_data
            }))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(tetse_ws.recv(), timeout=5.0)
                logger.debug(f"TETSE server response: {response}")
                return {"status": "success", "tetse_response": response}
            except asyncio.TimeoutError:
                logger.warning("TETSE server response timeout")
                return {"status": "success", "note": "TETSE processing initiated"}
                
    except Exception as e:
        logger.error(f"Failed to process event: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.websocket("/ws/forward_event")
async def forward_event_handler(websocket: WebSocket):
    """
    WebSocket endpoint to receive events from the main app and forward them to the TETSE WebSocket server on port 9000.
    """
    # Fixed: Handle optional client attribute safely
    client_host = getattr(websocket.client, 'host', 'unknown') if websocket.client else 'unknown'
    client_port = getattr(websocket.client, 'port', 0) if websocket.client else 0
    client_id = f"{client_host}:{client_port}"
    logger.info(f"WebSocket connection attempt for /ws/forward_event from {client_id}")
    file_handler.flush()

    # Initialize HeartbeatManager
    heartbeat_manager = HeartbeatManager(websocket, client_id=client_id, interval=30, timeout=5)
    heartbeat_task = asyncio.create_task(heartbeat_loop(heartbeat_manager))

    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for {client_id}")
        file_handler.flush()

        # Connect to the TETSE WebSocket server on port 9000
        server_host = get_server_host()
        tetse_url = f"ws://{server_host}:9000/broadcast_event_ws"
        async with websockets.connect(tetse_url) as tetse_ws:
            logger.info(f"Connected to TETSE WebSocket server on port 9000 from {client_id}")
            file_handler.flush()

            try:
                while True:
                    # Receive event data from the main app
                    data = await websocket.receive_json()
                    logger.debug(f"Received event data from {client_id}: {data}")
                    file_handler.flush()

                    # Handle heartbeat messages
                    if data.get("type") == "HeartBeat":
                        result = heartbeat_manager.validate_response(data)
                        if result is False:
                            await websocket.send_json({"type": "EndStream", "reason": "Too many invalid heartbeats"})
                            await websocket.close()
                            break
                        elif result is True and heartbeat_manager.too_frequent():
                            await websocket.send_json({"type": "Warning", "reason": "Heartbeat too frequent"})
                        continue

                    # Forward the event data to the TETSE WebSocket server
                    logger.debug(f"Sending event data to TETSE WebSocket server for {client_id}")
                    await tetse_ws.send(json.dumps(data))
                    logger.debug(f"Forwarded event data to TETSE WebSocket server: {data}")
                    file_handler.flush()

                    # Receive confirmation from the TETSE WebSocket server
                    try:
                        while True:
                            response = await asyncio.wait_for(tetse_ws.recv(), timeout=10.0)
                            try:
                                response_data = json.loads(response)
                                if response_data.get("type") == "HeartBeat":
                                    logger.debug(f"Ignored heartbeat from TETSE WebSocket server: {response}")
                                    continue
                            except json.JSONDecodeError:
                                # Non-JSON response (e.g., plain string)
                                logger.debug(f"Received non-JSON response from TETSE WebSocket server: {response}")
                                file_handler.flush()

                                # Send the response back to the main app
                                # Fixed: Ensure response is a string before sending
                                response_str = response if isinstance(response, str) else str(response)
                                await websocket.send_text(response_str)
                                logger.debug(f"Sent response to {client_id}: {response_str}")
                                file_handler.flush()
                                break

                            logger.debug(f"Received JSON response from TETSE WebSocket server: {response}")
                            file_handler.flush()

                            # Send the response back to the main app
                            # Fixed: Ensure response is a string before sending
                            response_str = response if isinstance(response, str) else str(response)
                            await websocket.send_text(response_str)
                            logger.debug(f"Sent response to {client_id}: {response_str}")
                            file_handler.flush()
                            break
                    except asyncio.TimeoutError:
                        logger.warning(f"No valid response received from TETSE WebSocket server for {client_id}")
                        await websocket.send_text("No response from TETSE server")
                        file_handler.flush()

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for {client_id}")
                file_handler.flush()
            except Exception as e:
                logger.error(f"Error in WebSocket connection for {client_id}: {str(e)}")
                file_handler.flush()
                raise

    except Exception as e:
        logger.error(f"Connection error for {client_id}: {str(e)}")
        await websocket.close(code=1000, reason="Server error")
    finally:
        heartbeat_task.cancel()
        if websocket.state == websockets.State.OPEN:
            end_stream = {
                "type": "request",
                "request": "EndStream",
                "reqid": ""
            }
            try:
                await websocket.send_json(end_stream)
                logger.info(f"Sent EndStream to {client_id}: {end_stream}")
                file_handler.flush()
                # Fixed: Use receive_text() for WebSocket instead of recv()
                message = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
                data = json.loads(message)
                logger.info(f"Received response to EndStream from {client_id}: {data}")
                file_handler.flush()
            except Exception as e:
                logger.error(f"Failed to send/receive EndStream for {client_id}: {str(e)}")
                file_handler.flush()
            await websocket.close()
            logger.info(f"Closed WebSocket connection for {client_id}")
            file_handler.flush()

async def heartbeat_loop(hbm):
    while True:
        await hbm.send_heartbeat()
        await hbm.check_timeout()
        await asyncio.sleep(30)