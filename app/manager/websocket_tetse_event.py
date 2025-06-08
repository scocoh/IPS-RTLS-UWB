# Name: websocket_tetse_event.py
# Version: 0.1.22
# Created: 250525
# Modified: 250601
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: TETSE EventStream WebSocket Server (port 9000)
# Location: /home/parcoadmin/parco_fastapi/app/manager/websocket_tetse_event.py
# Role: WebSocket Interface for TETSE
# Status: Active
# Dependent: TRUE
#
# Version: 0.1.22 - Fixed bug in event broadcast where 'dict' object had no attribute 'entity'; now uses event['entity_id'], bumped from 0.1.21
# Version: 0.1.21 - Added in remarks removed by AI in TETSE section
# Version: 0.1.20 - Added AI summary generation via ask_openai during event broadcasting in /broadcast_event_ws
# Version: 0.1.18 - Fixed ts parsing to datetime for usp_event_log_add, bumped from 0.1.17
# Version: 0.1.17 - Added event logging to event_log via usp_event_log_add with asyncpg pool, bumped from 0.1.16
# Version: 0.1.16 - Integrated HeartbeatManager, removed manual rate-limiting, bumped from 0.1.15
# Version: 0.1.15 - Added missing imports for json and websockets to fix Pylance errors, bumped from 0.1.14
# Version: 0.1.14 - Added heartbeat rate-limiting, EndStream handling, and LineLimitedFileHandler, bumped from 0.1.13
# Version: 0.1.13 - Added WebSocket endpoint to receive events from port 8998, bumped from 0.1.12
# Version: 0.1.12 - Added HTTP endpoint to receive and broadcast events, bumped from 0.1.11
# Version: 0.1.11 - Added more debug logging for TETSE_MANAGER instance, bumped from 0.1.10
# Version: 0.1.10 - Added debug logging for client registration, bumped from 0.1.9
# Version: 0.1.9 - Reverted to using TETSE_MANAGER instance to fix TypeError in add_client, bumped from 0.1.8
# Version: 0.1.8 - Use Manager.clients directly for client registration, bumped from 0.1.7
# Version: 0.1.7 - Made TETSE_MANAGER accessible for event.py to fix broadcasting, bumped from 0.1.6
# Version: 0.1.6 - Replaced receive loop with sleep to prevent disconnection, added ping, bumped from 0.1.5
# Version: 0.1.5 - Added Manager instance to fix TypeError in add_client, bumped from 0.1.4
# Version: 0.1.4 - Rewritten to use FastAPI and run as a module to fix import issues, bumped from 0.1.3
# Version: 0.1.3 - Fixed relative import issue by adjusting sys.path, bumped from 0.1.2
# Version: 0.1.2 - Added debug logging for startup issues, bumped from 0.1.1
# Version: 0.1.1 - Changed to LineLimitedFileHandler for logging consistency with manager.py, bumped from 0.1.0
# Version: 0.1.0 - Initial implementation of TETSE WebSocket server

import logging
import os
import asyncio
import json
import websockets
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from manager.line_limited_logging import LineLimitedFileHandler
from manager.manager import Manager
from pydantic import BaseModel
from .heartbeat_manager import HeartbeatManager
from datetime import datetime, timezone
from routes.llm_bridge import ask_openai
from routes.openai_trigger_api import construct_prompt

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("manager.websocket_tetse_event")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

file_handler = LineLimitedFileHandler(
    os.path.join(LOG_DIR, "websocket_tetse_event.log"),
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

logger.handlers = [console_handler, file_handler]
logger.propagate = False

logger.info("Starting WebSocket TETSE Event server on port 9000")
file_handler.flush()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.210.226:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
logger.debug("CORS middleware added with allow_origins: http://192.168.210.226:3000")
file_handler.flush()

# Create a Manager instance for TETSE events
TETSE_MANAGER = Manager("TETSE", zone_id=None)
logger.debug(f"Initialized TETSE_MANAGER instance: {id(TETSE_MANAGER)}")
file_handler.flush()

# Database connection string
MAINT_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSData"

class EventBroadcast(BaseModel):
    entity_id: str
    event_data: dict

@app.post("/broadcast_event")
async def broadcast_event(event: EventBroadcast):
    """
    HTTP endpoint to receive events from the main app and broadcast them to WebSocket clients.
    """
    try:
        logger.info(f"Received event to broadcast for entity {event.entity_id}: {event.event_data}")
        await TETSE_MANAGER.broadcast_event_instance(event.entity_id, event.event_data)
        return {"status": "Event broadcasted successfully"}
    except Exception as e:
        logger.error(f"Failed to broadcast event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/broadcast_event_ws")
async def broadcast_event_ws(websocket: WebSocket):
    """
    WebSocket endpoint to receive events from the forwarding server on port 8998 and broadcast them to clients.
    """
    client_host = websocket.client.host
    client_port = websocket.client.port
    client_id = f"{client_host}:{client_port}"
    logger.info(f"WebSocket connection attempt for /broadcast_event_ws from {client_id}")
    file_handler.flush()

    heartbeat_manager = HeartbeatManager(websocket, client_id=client_id, interval=30, timeout=5)
    heartbeat_task = asyncio.create_task(heartbeat_loop(heartbeat_manager))

    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for {client_id}")
        file_handler.flush()

        try:
            while True:
                data = await websocket.receive_json()
                logger.debug(f"Received event data from {client_id}: {data}")
                file_handler.flush()

                if data.get("type") == "HeartBeat":
                    result = heartbeat_manager.validate_response(data)
                    if result is False:
                        await websocket.send_json({"type": "EndStream", "reason": "Too many invalid heartbeats"})
                        await websocket.close()
                        break
                    elif result is True and heartbeat_manager.too_frequent():
                        await websocket.send_json({"type": "Warning", "reason": "Heartbeat too frequent"})
                    continue

                if data.get("type") == "request" and data.get("request") == "EndStream":
                    logger.info(f"Received EndStream from {client_id}: {data}")
                    await TETSE_MANAGER.broadcast_event_instance(data.get("entity_id", ""), data)
                    response = {
                        "type": "response",
                        "request": "EndStream",
                        "reqid": data.get("reqid", "")
                    }
                    await websocket.send_json(response)
                    logger.info(f"Sent EndStream response to {client_id}: {response}")
                    break

                entity_id = data.get("entity_id")
                event_data = data.get("event_data")
                if entity_id and event_data:
                    # Resolved event_type_id
                    # --- BEGIN AI SUMMARY GENERATION [Added in 0.1.20] ---
                    ai_summary = "[AI summary unavailable]"
                    try:
                        entity_id_safe = data.get("entity_id", "UNKNOWN_ENTITY")
                        prompt = construct_prompt(event_data)
                        ai_summary = await ask_openai(prompt)
                        event_data["ai_summary"] = ai_summary
                        logger.info(f"AI Summary generated for entity {entity_id_safe}: {ai_summary}")
                    except Exception as ai_error:
                        logger.warning(f"AI Summary generation failed for entity {entity_id_safe}: {str(ai_error)}")
                        event_data["ai_summary"] = ai_summary
                    # --- END AI SUMMARY GENERATION ---

                    event_type_name = event_data.get("event_type", "Unknown")
                    async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
                        async with pool.acquire() as conn:
                            result = await conn.fetchval("SELECT id FROM tlk_event_type WHERE name = $1", event_type_name)
                            event_type_id = result if result else 5 #TestEvent
                            if not result:
                                logger.warning(f"No event_type_id for {event_type_name}, using default ID: {event_type_id}")
                            
                            # Set defaults
                            reason_id = event_data.get("reason_id", 4)
                            value = event_data.get("value")
                            if isinstance(value, str):
                                try:
                                    value = float(value) if value else 1.0
                                except ValueError:
                                    value = 1.0
                            elif value is None:
                                value = 1.0
                            unit = event_data.get("unit", "percent")
                            ts_str = event_data.get("timestamp")
                            ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00')) if ts_str else datetime.now(timezone.utc)

                            # Log to event_log
                            result = await conn.fetchval(
                                "SELECT usp_event_log_add($1, $2, $3, $4, $5, $6)",
                                entity_id, event_type_id, reason_id, value, unit, ts
                            )
                            if result:
                                logger.debug(f"Logged event for entity {entity_id} via usp_event_log_add: {result}")
                            else:
                                logger.error(f"Failed to log event for entity {entity_id}")

                    # Broadcast Event
                    await TETSE_MANAGER.broadcast_event_instance(entity_id, event_data)
                    logger.debug(f"Broadcasted event for entity {entity_id}: {event_data}")
                    file_handler.flush()
                    await websocket.send_text("Event broadcasted and logged successfully")
                else:
                    logger.error(f"Invalid event data received: {data}")
                    await websocket.send_text("Invalid event data")

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
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                logger.info(f"Received response to EndStream from {client_id}: {data}")
                file_handler.flush()
            except Exception as e:
                logger.error(f"Failed to send/receive EndStream for {client_id}: {str(e)}")
                file_handler.flush()
            await websocket.close()
            logger.info(f"Closed WebSocket connection for {client_id}")
            file_handler.flush()

@app.websocket("/ws/tetse_event/{entity_id}")
async def tetse_event_handler(websocket: WebSocket, entity_id: str):
    """
    Handle WebSocket connections for TETSE event streams.
    Path format: /ws/tetse_event/{entity_id}
    """
    client_host = websocket.client.host
    client_port = websocket.client.port
    client_id = f"{client_host}:{client_port}"
    client_type = "client"
    logger.info(f"WebSocket connection attempt for /ws/tetse_event/{entity_id} from {client_id} ({client_type})")
    file_handler.flush()

    heartbeat_manager = HeartbeatManager(websocket, client_id=client_id, interval=30, timeout=5)
    heartbeat_task = asyncio.create_task(heartbeat_loop(heartbeat_manager))

    try:
        if not entity_id:
            logger.error("No entity_id provided in path")
            await websocket.close(code=1002, reason="Missing entity_id")
            return

        topic = f"ws_event_{entity_id}"
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for {topic} from {client_id} ({client_type})")
        file_handler.flush()

        logger.debug(f"Using TETSE_MANAGER instance: {id(TETSE_MANAGER)}")
        await TETSE_MANAGER.add_client(topic, websocket)
        logger.debug(f"After adding client, TETSE_MANAGER.clients: {TETSE_MANAGER.clients}")
        file_handler.flush()

        try:
            while True:
                await websocket.send_json({"type": "ping"})
                logger.debug(f"Sent ping to {client_id} ({client_type}) on topic {topic}")
                file_handler.flush()
                await asyncio.sleep(30)

                try:
                    message = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                    logger.debug(f"Received message from {client_id} on topic {topic}: {message}")
                    if message.get("type") == "HeartBeat":
                        result = heartbeat_manager.validate_response(message)
                        if result is False:
                            await websocket.send_json({"type": "EndStream", "reason": "Too many invalid heartbeats"})
                            await websocket.close()
                            break
                        elif result is True and heartbeat_manager.too_frequent():
                            await websocket.send_json({"type": "Warning", "reason": "Heartbeat too frequent"})
                    elif message.get("type") == "request" and message.get("request") == "EndStream":
                        logger.info(f"Received EndStream from {client_id}: {message}")
                        response = {
                            "type": "response",
                            "request": "EndStream",
                            "reqid": message.get("reqid", "")
                        }
                        await websocket.send_json(response)
                        logger.info(f"Sent EndStream response to {client_id}: {response}")
                        break
                except asyncio.TimeoutError:
                    pass

        except WebSocketDisconnect:
            logger.info(f"Client disconnected from {topic} ({client_id}, {client_type})")
            await TETSE_MANAGER.remove_client(topic, websocket)
            logger.debug(f"After removing client, TETSE_MANAGER.clients: {TETSE_MANAGER.clients}")
            file_handler.flush()
        except Exception as e:
            logger.error(f"Error on {topic} for client {client_id} ({client_type}): {str(e)}")
            await TETSE_MANAGER.remove_client(topic, websocket)
            logger.debug(f"After removing client due to error, TETSE_MANAGER.clients: {TETSE_MANAGER.clients}")
            file_handler.flush()
            await websocket.close(code=1000, reason="Server error")

    except Exception as e:
        logger.error(f"Handler error for path /ws/tetse_event/{entity_id} from {client_id} ({client_type}): {str(e)}")
        await websocket.close(code=1000, reason="Server error")
    finally:
        heartbeat_task.cancel()
        if websocket.state == websockets.State.OPEN:
            await websocket.close()
            logger.info(f"Closed WebSocket connection for {client_id}")
            file_handler.flush()

async def heartbeat_loop(hbm):
    while True:
        await hbm.send_heartbeat()
        await hbm.check_timeout()
        await asyncio.sleep(30)