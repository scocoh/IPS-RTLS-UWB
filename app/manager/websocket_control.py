# Name: websocket_control.py
# Version: 0.1.51
# Created: 250512
# Modified: 250519
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS Control WebSocket server on port 8001
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/websocket_control.py
# Version: 0.1.51 - Replaced RotatingFileHandler with LineLimitedFileHandler for 999-line limit, bumped from 0.1.50
# Previous: Fixed GISData forwarding, added heartbeat_id, enhanced subscription logging, bumped from 0.1.49
# Previous: Fixed log directory to /home/parcoadmin/parco_fastapi/app/logs, added error handling for log file creation, bumped from 0.1.48
# Previous: Added explicit log directory creation, permission checks, enhanced GISData logging with subscription details, bumped from 0.1.47
# Previous: Added logging for GISData message forwarding, bumped from 0.1.46
# Previous: Added EndStream message before disconnecting due to heartbeat timeout, bumped from 0.1.45
# Previous: Fixed heartbeat feedback loop by removing server response to client heartbeats, added timeout for manager responsiveness, bumped from 0.1.44
# Previous: Added explicit flush() calls after key log messages to ensure log writing, removed invalid buffering=1, bumped from 0.1.43
# Previous: Added debug logging for heartbeat rate-limiting to diagnose feedback loop issue, bumped from 0.1.42
# Previous: Added rate-limiting for heartbeat responses to prevent feedback loop, bumped from 0.1.41
# Previous: Added file logging with rotation, bumped from 0.1.40
# Previous: Fixed rapid heartbeat loop by adding error handling and ensuring 60-second interval, bumped from 0.1.39
# Previous: Send PortRedirect to all clients after BeginStream, bumped from 0.1.38
# Previous: Send PortRedirect to simulator clients, bumped from 0.1.37
# Previous: Moved manager.start() to lifespan for heartbeat functionality (0.1.37)
# Previous: Added debug logging to start() method (0.1.36)
# Previous: Fixed zone_id handling in WebSocket handler (0.1.35)
# Note: This server handles control messages for ParcoRTLS, using Control type (i_typ_res=10).

import asyncio
import logging
import os
import stat
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import json
from datetime import datetime
from .manager import Manager
from .sdk_client import SDKClient
from .models import HeartBeat, Response, ResponseType, Request, Tag
from .enums import RequestType, eMode
from .constants import REQUEST_TYPE_MAP, NEW_REQUEST_TYPES
from .line_limited_logging import LineLimitedFileHandler
from collections import deque

# Log directory and file
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "websocket_control.log")

# Ensure log directory exists with correct permissions
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    os.chmod(LOG_DIR, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)  # 775
except Exception as e:
    print(f"Failed to create log directory {LOG_DIR}: {str(e)}")
    raise

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# StreamHandler for console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

# LineLimitedFileHandler for file
try:
    file_handler = LineLimitedFileHandler(
        LOG_FILE,
        max_lines=999,
        backup_count=4
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
    logger.handlers = []
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    logger.debug(f"Log directory {LOG_DIR} and file {LOG_FILE} initialized")
    file_handler.flush()
except Exception as e:
    logger.error(f"Failed to initialize file handler for {LOG_FILE}: {str(e)}")
    raise

# Feature flags
ENABLE_MULTI_PORT = True

# Stream type for this server
STREAM_TYPE = "Control"
RESOURCE_TYPE = 10  # Control

# Database connection string
MAINT_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint"

# Rate-limiting for heartbeat messages
HEARTBEAT_RESPONSE_RATE_LIMIT = 10
HEARTBEAT_TIMEOUT = 5.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan: Initializing DB pool")
    file_handler.flush()
    try:
        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            logger.debug("DB pool created successfully")
            file_handler.flush()
            async with pool.acquire() as conn:
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
_HEARTBEAT_RESPONSE_TIMESTAMPS = {}
_SERVER_HEARTBEAT_TRACKER = {}  # {client_id: {'ts': timestamp, 'last_sent': time}}

@app.websocket("/ws/{manager_name}")
async def websocket_endpoint_control(websocket: WebSocket, manager_name: str):
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {websocket.client.host}:{websocket.client.port}")
    file_handler.flush()
    async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
        async with pool.acquire() as conn:
            manager_info = await conn.fetchrow(
                "SELECT i_typ_res FROM tlkresources WHERE X_NM_RES = $1 AND i_typ_res = $2",
                manager_name, RESOURCE_TYPE)
            if not manager_info:
                logger.error(f"Manager {manager_name} not found or invalid type")
                file_handler.flush()
                await websocket.close(code=1008, reason="Manager not found")
                return
    sdk_client = None
    client_id = None
    is_disconnected = False
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name}")
        file_handler.flush()
        if manager_name not in _MANAGER_INSTANCES:
            manager = Manager(manager_name, zone_id=None)
            _MANAGER_INSTANCES[manager_name] = manager
        else:
            manager = _MANAGER_INSTANCES[manager_name]
        client_id = f"{websocket.client.host}:{websocket.client.port}"
        sdk_client = SDKClient(websocket, client_id)
        sdk_client.parent = manager
        manager.sdk_clients[client_id] = sdk_client
        sdk_client.start_q_timer()

        if manager_name not in _WEBSOCKET_CLIENTS:
            _WEBSOCKET_CLIENTS[manager_name] = []
        _WEBSOCKET_CLIENTS[manager_name].append(sdk_client)

        _HEARTBEAT_RESPONSE_TIMESTAMPS[client_id] = deque(maxlen=HEARTBEAT_RESPONSE_RATE_LIMIT)
        _SERVER_HEARTBEAT_TRACKER[client_id] = {'ts': None, 'last_sent': None}
        logger.debug(f"Initialized heartbeat rate-limiting for client {client_id} with maxlen={HEARTBEAT_RESPONSE_RATE_LIMIT}")
        file_handler.flush()

        while True:
            try:
                if _SERVER_HEARTBEAT_TRACKER[client_id]['last_sent'] is not None:
                    current_time = asyncio.get_event_loop().time()
                    time_since_last_heartbeat = current_time - _SERVER_HEARTBEAT_TRACKER[client_id]['last_sent']
                    if time_since_last_heartbeat > HEARTBEAT_TIMEOUT:
                        logger.error(f"Client {client_id} failed to respond to heartbeat within {HEARTBEAT_TIMEOUT} seconds, disconnecting")
                        file_handler.flush()
                        end_stream = Response(
                            response_type=ResponseType.EndStream,
                            req_id="",
                            message=f"Failed to respond to heartbeat within {HEARTBEAT_TIMEOUT} seconds"
                        )
                        await websocket.send_text(end_stream.to_json())
                        logger.info(f"Sent EndStream to client {client_id}: {end_stream.to_json()}")
                        file_handler.flush()
                        sdk_client.is_closing = True
                        await websocket.close(code=1008, reason="Manager not responding to heartbeats")
                        break

                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message from client {client_id}: {data}")
                file_handler.flush()
                json_data = json.loads(data)
                msg_type = json_data.get("type", "")

                if msg_type == "HeartBeat":
                    current_time = asyncio.get_event_loop().time()
                    timestamps = _HEARTBEAT_RESPONSE_TIMESTAMPS[client_id]
                    timestamps.append(current_time)
                    if len(timestamps) == HEARTBEAT_RESPONSE_RATE_LIMIT:
                        time_window = current_time - timestamps[0]
                        logger.debug(f"Rate-limiting check: {HEARTBEAT_RESPONSE_RATE_LIMIT} messages in {time_window:.2f} seconds")
                        file_handler.flush()
                        if time_window < 1.0:
                            logger.warning(f"Heartbeat rate exceeded {HEARTBEAT_RESPONSE_RATE_LIMIT} messages per second for client {client_id}, disconnecting")
                            file_handler.flush()
                            end_stream = Response(
                                response_type=ResponseType.EndStream,
                                req_id="",
                                message=f"Heartbeat rate exceeded {HEARTBEAT_RESPONSE_RATE_LIMIT} messages per second"
                            )
                            await websocket.send_text(end_stream.to_json())
                            logger.info(f"Sent EndStream to client {client_id}: {end_stream.to_json()}")
                            file_handler.flush()
                            sdk_client.is_closing = True
                            await websocket.close(code=1008, reason=f"Heartbeat rate exceeded {HEARTBEAT_RESPONSE_RATE_LIMIT} messages per second")
                            break

                    try:
                        hb = HeartBeat(ticks=json_data["ts"])
                        sdk_client.heartbeat = hb.ticks
                        if (_SERVER_HEARTBEAT_TRACKER[client_id]['ts'] is not None and
                            json_data["ts"] == _SERVER_HEARTBEAT_TRACKER[client_id]['ts']):
                            logger.debug(f"Client {client_id} responded to server heartbeat, resetting timeout")
                            file_handler.flush()
                            _SERVER_HEARTBEAT_TRACKER[client_id]['ts'] = None
                            _SERVER_HEARTBEAT_TRACKER[client_id]['last_sent'] = None
                        else:
                            logger.debug(f"Processed HeartBeat for client {client_id}, ts: {hb.ticks}")
                            file_handler.flush()
                    except Exception as e:
                        logger.error(f"Failed to process HeartBeat from client {client_id}: {str(e)}")
                        file_handler.flush()
                        sdk_client.is_closing = True
                        break
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
                        logger.debug(f"Sent error response to client {client_id}: {resp.to_json()}")
                        file_handler.flush()
                        continue

                    req = Request(
                        req_type=req_type,
                        req_id=req_id,
                        tags=[Tag(id=tag["id"], send_payload_data=tag["data"] == "true")
                              for tag in json_data.get("params", [])]
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
                        logger.info(f"Client {client_id} subscribed to tags: {[t.id for t in req.tags]}, zone_id: {json_data.get('zone_id')}")
                        file_handler.flush()
                        if not resp.message:
                            port_redirect = {
                                "type": "PortRedirect",
                                "port": 8002,
                                "stream_type": "RealTime",
                                "manager_name": "RealTimeManager",
                                "heartbeat_id": str(int(datetime.now().timestamp() * 1000))
                            }
                            await websocket.send_text(json.dumps(port_redirect))
                            logger.info(f"Sent PortRedirect to client {client_id}: {port_redirect}")
                            file_handler.flush()
                        if resp.message:
                            await manager.close_client(sdk_client)
                            break
                    elif req.req_type == RequestType.EndStream:
                        await websocket.send_text(resp.to_json())
                        await manager.close_client(sdk_client)
                        break
                    else:
                        resp.message = "Request not supported in Control stream."
                        await websocket.send_text(resp.to_json())

                elif msg_type == "GISData":
                    logger.debug(f"Ignoring GISData message from client {client_id}: {json_data}")
                    file_handler.flush()
                    continue

                else:
                    logger.warning(f"Unknown message type from client {client_id}: {msg_type}")
                    file_handler.flush()

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for /ws/{manager_name}")
                file_handler.flush()
                is_disconnected = True
                await sdk_client.close()
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler: {str(e)}")
                file_handler.flush()
                sdk_client.is_closing = True
                break
    finally:
        if sdk_client and not is_disconnected:
            await sdk_client.close()
        if client_id in _SERVER_HEARTBEAT_TRACKER:
            del _SERVER_HEARTBEAT_TRACKER[client_id]
        if client_id in _HEARTBEAT_RESPONSE_TIMESTAMPS:
            del _HEARTBEAT_RESPONSE_TIMESTAMPS[client_id]
        if manager_name in _WEBSOCKET_CLIENTS and sdk_client in _WEBSOCKET_CLIENTS[manager_name]:
            _WEBSOCKET_CLIENTS[manager_name].remove(sdk_client)
        logger.info(f"Cleaned up client {client_id} for /ws/{manager_name}")
        file_handler.flush()