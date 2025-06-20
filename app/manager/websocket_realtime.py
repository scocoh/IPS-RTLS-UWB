# Name: websocket_realtime.py
# Version: 0.1.60
# Created: 250512
# Modified: 250616
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS RealTime WebSocket server on port 8002 with TETSE live evaluation, output processing, and dispatcher bootstrap
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/websocket_realtime.py
# Version: 0.1.60 - Phase 11.9.3 Circular Isolation Recovery
# Previous: 0.1.59 - Phase 11.4 Phase 2 Add reload_rules callable
# Previous: 0.1.58 - Phase 11.3.1
# Previous: 0.1.57 - Phase 6D Dispatcher Bootstrap Inserted
# Previous: 0.1.56 - Phase 6C.2 TETSE Output Processing Inserted
# Previous: 0.1.55 - Phase 6B.2 TETSE Live Rule Evaluation Inserted
# Previous: 0.1.54 - Integrated HeartbeatManager, removed _PENDING_HEARTBEATS and _LAST_HEARTBEAT
# Previous: Increased initial heartbeat timeout to 60s for manual clients, enhanced wscat logging, bumped from 0.1.52
# Previous: Aligned log path with /home/parcoadmin/parco_fastapi/app/logs, added console logging, extended initial heartbeat timeout to 10s, enhanced logging, bumped from 0.1.51
# Previous: Relaxed heartbeat_id validation for legacy clients, retained 5-second timeout and no server responses, enhanced logging, bumped from 0.1.50
# Previous: Removed server heartbeat responses, enforced 5-second response timeout, validated timestamp-based heartbeat_id, enhanced logging to align with VB.NET behavior, bumped from 0.1.49

import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import json
from datetime import datetime
from .manager import Manager
from .sdk_client import SDKClient
from .models import HeartBeat, Response, ResponseType, Request, Tag
from .enums import RequestType
from .constants import REQUEST_TYPE_MAP
from .heartbeat_manager import HeartbeatManager
import os
from logging.handlers import RotatingFileHandler
from routes.subject_registry import update_subject_zone
from routes.tetse_rule_engine import evaluate_house_exclusion_rule
from routes.tetse_reload import reload_rules, ACTIVE_TETSE_RULES
from routes.tetse_output_handler import process_tetse_result
from routes.tetse_event_dispatcher import start_dispatcher

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "websocket_realtime.log"),
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

logger.handlers = [console_handler, file_handler]
logger.propagate = False

logger.info("Starting WebSocket RealTime server on port 8002")
file_handler.flush()

# Hardcoded tag-to-subject map for Phase 6B (replaceable later)
TAG_TO_SUBJECT = {
    "23001": "Eddy"
}

ENABLE_MULTI_PORT = True
STREAM_TYPE = "RealTime"
RESOURCE_TYPE = 1
MAINT_CONN_STRING = os.getenv("MAINT_CONN_STRING", "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint")
HEARTBEAT_INTERVAL = 30.0  # Heartbeat every 30 seconds

# Preload TETSE rules at startup
async def initialize_tetse_rules():
    try:
        await reload_rules()
        logger.info(f"TETSE: Loaded {len(ACTIVE_TETSE_RULES)} rules for live evaluation")
    except Exception as e:
        logger.error(f"Failed to initialize TETSE rules: {str(e)}")

asyncio.create_task(initialize_tetse_rules())

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan: Initializing DB pool")
    file_handler.flush()
    try:
        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            logger.debug("DB pool created successfully")
            file_handler.flush()
            async with pool.acquire() as conn:
                # Load TETSE rules on startup
                await reload_rules()
                logger.info(f"TETSE: Loaded {len(ACTIVE_TETSE_RULES)} rules for live evaluation")
                file_handler.flush()

                managers = await conn.fetch("SELECT X_NM_RES, i_typ_res FROM tlkresources WHERE i_typ_res = $1", RESOURCE_TYPE)
                logger.debug(f"Queried tlkresources, found {len(managers)} managers for i_typ_res={RESOURCE_TYPE}")
                file_handler.flush()
                for manager in managers:
                    logger.info(f"Manager {manager['x_nm_res']} (type {manager['i_typ_res']}) ready")
                    file_handler.flush()
                    manager_name = manager['x_nm_res']
                    if manager_name not in _MANAGER_INSTANCES:
                        manager_instance = Manager(manager_name, zone_id=None)
                        _MANAGER_INSTANCES[manager_name] = manager_instance
                        logger.debug(f"Starting manager {manager_name}")
                        file_handler.flush()
                        await manager_instance.start()
                        logger.debug(f"Manager {manager_name} started successfully")
                        file_handler.flush()
                        # Start TETSE Dispatcher Workers
                        asyncio.create_task(start_dispatcher(num_workers=2))
                        logger.info("TETSE Dispatcher workers started.")
        yield
    except Exception as e:
        logger.error(f"Lifespan error: {str(e)}")
        file_handler.flush()
        raise
    logger.info("Application shutdown")
    file_handler.flush()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.210.226:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
logger.debug("CORS middleware added with allow_origins: http://192.168.210.226:3000")
file_handler.flush()

_MANAGER_INSTANCES = {}
_WEBSOCKET_CLIENTS = {}

@app.websocket("/ws/{manager_name}")
async def websocket_endpoint_realtime(websocket: WebSocket, manager_name: str):
    client_host = websocket.client.host
    client_port = websocket.client.port
    client_id = f"{client_host}:{client_port}"
    # Detect wscat clients (simplified heuristic, adjust if needed)
    is_wscat = "wscat" in websocket.headers.get("user-agent", "").lower() or client_port > 40000
    client_type = "wscat" if is_wscat else "client"
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {client_id} ({client_type})")
    file_handler.flush()

    # Initialize HeartbeatManager
    heartbeat_manager = HeartbeatManager(websocket, client_id=client_id, interval=HEARTBEAT_INTERVAL, timeout=5)

    try:
        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            async with pool.acquire() as conn:
                manager_info = await conn.fetchrow(
                    "SELECT i_typ_res FROM tlkresources WHERE X_NM_RES = $1 AND i_typ_res = $2",
                    manager_name, RESOURCE_TYPE
                )
                if not manager_info:
                    logger.warning(f"Manager {manager_name} not found, creating default instance")
                    file_handler.flush()
                    if manager_name not in _MANAGER_INSTANCES:
                        manager = Manager(manager_name, zone_id=None)
                        _MANAGER_INSTANCES[manager_name] = manager
                        await manager.start()
    except Exception as e:
        logger.error(f"Database query failed for manager {manager_name}: {str(e)}")
        file_handler.flush()
        await websocket.close(code=1008, reason="Database error")
        return

    sdk_client = None
    is_disconnected = False
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name} from {client_id} ({client_type})")
        file_handler.flush()
        manager = _MANAGER_INSTANCES.get(manager_name)
        if not manager:
            logger.error(f"Manager {manager_name} not initialized")
            file_handler.flush()
            await websocket.close(code=1008, reason="Manager not initialized")
            return
        sdk_client = SDKClient(websocket, client_id)
        sdk_client.parent = manager
        manager.sdk_clients[client_id] = sdk_client
        sdk_client.start_q_timer()

        if manager_name not in _WEBSOCKET_CLIENTS:
            _WEBSOCKET_CLIENTS[manager_name] = []
        _WEBSOCKET_CLIENTS[manager_name].append(sdk_client)
        logger.debug(f"Added client {client_id} ({client_type}) to _WEBSOCKET_CLIENTS for {manager_name}. Total clients: {len(_WEBSOCKET_CLIENTS[manager_name])}")
        file_handler.flush()

        # Start heartbeat loop
        heartbeat_task = asyncio.create_task(heartbeat_loop(heartbeat_manager))

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=HEARTBEAT_INTERVAL)
                logger.debug(f"Received WebSocket message from client {client_id} ({client_type}): {data}")
                file_handler.flush()
                json_data = json.loads(data)
                msg_type = json_data.get("type", "")

                if msg_type == "HeartBeat":
                    # Validate heartbeat with HeartbeatManager
                    heartbeat_result = heartbeat_manager.validate_response(json_data)
                    if heartbeat_result is False:
                        await websocket.send_json({
                            "type": "EndStream",
                            "reason": "Too many invalid heartbeats"
                        })
                        logger.info(f"Sent EndStream to client {client_id} ({client_type}): Too many invalid heartbeats")
                        file_handler.flush()
                        sdk_client.is_closing = True
                        break
                    elif heartbeat_result is True:
                        if heartbeat_manager.too_frequent():
                            await websocket.send_json({
                                "type": "Warning",
                                "reason": "Heartbeat too frequent"
                            })
                            logger.debug(f"Sent warning to client {client_id} ({client_type}): Heartbeat too frequent")
                            file_handler.flush()
                    # Log legacy heartbeats (no heartbeat_id)
                    if heartbeat_result is None and json_data.get("heartbeat_id") is None:
                        logger.warning(f"Ignored legacy HeartBeat TS: {json_data.get('ts', 'none')} from client {client_id} ({client_type}), no heartbeat_id")
                        file_handler.flush()
                    continue

                elif msg_type == "GISData":
                    tag_id = json_data.get("ID")
                    zone_id = json_data.get("zone_id")
                    sim_message = {
                        "gis": {
                            "id": tag_id,
                            "x": json_data.get("X", 0.0),
                            "y": json_data.get("Y", 0.0),
                            "z": json_data.get("Z", 0.0)
                        },
                        "zone_id": zone_id
                    }
                    await manager.process_sim_message(sim_message)
                    # TETSE real-time hook
                    subject_id = TAG_TO_SUBJECT.get(tag_id)
                    if subject_id:
                        await update_subject_zone(subject_id, zone_id)
                        matching_rules = [r for r in ACTIVE_TETSE_RULES if r["subject_id"] == subject_id]
                        for rule in matching_rules:
                            result = await evaluate_house_exclusion_rule(rule)
                            logger.info(f"TETSE Live Eval: Subject={subject_id} Rule={rule['name']} Result={result}")
                            await process_tetse_result(subject_id, rule, result)
                    logger.debug(f"Processing GISData for tag {tag_id} in zone {zone_id} from client {client_id} ({client_type})")
                    file_handler.flush()
                    for ws_client in _WEBSOCKET_CLIENTS.get(manager_name, []):
                        if ws_client != sdk_client and ws_client.request_msg:
                            for tag in ws_client.request_msg.tags:
                                client_zone_id = str(zone_id) if zone_id is not None else None
                                message_zone_id = str(zone_id) if zone_id is not None else None
                                if tag.id == tag_id and client_zone_id == message_zone_id:
                                    await ws_client.websocket.send_text(data)
                                    logger.debug(f"Forwarded GISData to client {ws_client.client_id} for tag {tag.id}, zone {message_zone_id}")
                                    file_handler.flush()
                                else:
                                    logger.debug(f"Skipped forwarding GISData to client {ws_client.client_id}: tag {tag.id} vs {tag_id}, zone {client_zone_id} vs {message_zone_id}")
                                    file_handler.flush()
                    continue

                elif msg_type == "request":
                    request_type = json_data.get("request", "")
                    req_id = json_data.get("reqid", "")

                    req_type = REQUEST_TYPE_MAP.get(request_type)
                    if not req_type:
                        resp = Response(
                            response_type=ResponseType.Unknown,
                            req_id=req_id,
                            message=f"Invalid request type: {request_type}"
                        )
                        await websocket.send_text(resp.to_json())
                        logger.debug(f"Sent error response to client {client_id} ({client_type}): {resp.to_json()}")
                        file_handler.flush()
                        continue

                    req = Request(
                        req_type=req_type,
                        req_id=req_id,
                        tags=[Tag(id=tag["id"], send_payload_data=tag["data"] == "true")
                              for tag in json_data.get("params", [])],
                        zone_id=json_data.get("zone_id")
                    )
                    sdk_client.request_msg = req
                    resp = Response(response_type=ResponseType(req.req_type.value), req_id=req_id)

                    if req.req_type == RequestType.BeginStream:
                        if not req.tags:
                            resp.message = "Begin stream requests must contain at least one tag."
                        else:
                            for t in req.tags:
                                sdk_client.add_tag(t.id, t)
                        sdk_client.sent_begin_msg = True
                        sdk_client.sent_req = True
                        await websocket.send_text(resp.to_json())
                        logger.info(f"Client {client_id} ({client_type}) subscribed to tags: {[t.id for t in req.tags]}, zone_id: {json_data.get('zone_id')}")
                        file_handler.flush()
                        if resp.message:
                            await manager.close_client(sdk_client)
                            break
                    elif req.req_type == RequestType.EndStream:
                        await websocket.send_text(resp.to_json())
                        logger.info(f"Sent EndStream response to client {client_id} ({client_type}): {resp.to_json()}")
                        file_handler.flush()
                        await manager.close_client(sdk_client)
                        break
                    else:
                        resp.message = "Request not supported in RealTime stream."
                        await websocket.send_text(resp.to_json())
                        logger.debug(f"Sent error response to client {client_id} ({client_type}): {resp.to_json()}")
                        file_handler.flush()

                else:
                    logger.warning(f"Unknown message type from client {client_id} ({client_type}): {msg_type}")
                    file_handler.flush()

            except asyncio.TimeoutError:
                # Timeout allows periodic heartbeat checks
                continue
            except WebSocketDisconnect as e:
                logger.info(f"WebSocket disconnected for /ws/{manager_name} from {client_id} ({client_type}): {str(e)}")
                file_handler.flush()
                is_disconnected = True
                await sdk_client.close()
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler for client {client_id} ({client_type}): {str(e)}")
                file_handler.flush()
                sdk_client.is_closing = True
                break
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket endpoint for client {client_id} ({client_type}): {str(e)}")
        file_handler.flush()
    finally:
        if sdk_client and not is_disconnected:
            await sdk_client.close()
        if client_id in manager.sdk_clients:
            del manager.sdk_clients[client_id]
        if manager_name in _WEBSOCKET_CLIENTS and sdk_client in _WEBSOCKET_CLIENTS[manager_name]:
            _WEBSOCKET_CLIENTS[manager_name].remove(sdk_client)
        heartbeat_task.cancel()
        logger.info(f"Cleaned up client {client_id} ({client_type}) for /ws/{manager_name}")
        file_handler.flush()

async def heartbeat_loop(heartbeat_manager: HeartbeatManager):
    while heartbeat_manager.is_connected():
        await heartbeat_manager.send_heartbeat()
        await heartbeat_manager.check_timeout()
        await asyncio.sleep(HEARTBEAT_INTERVAL)