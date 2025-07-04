# Name: websocket_averaged.py
# Version: 0.1.6
# Created: 250513
# Modified: 250704
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS AveragedData WebSocket server on port 8004
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/websocket_averaged.py
# Version: 0.1.6 - IP centralization and syntax fixes, bumped from 0.1.5
# Previous: Moved manager.start() to lifespan to enable heartbeat loop, bumped from 0.1.4
# Previous: Updated logging to YYMMDD HHMMSS, bumped from 0.1.3
# Previous: Initial implementation for AveragedData stream

import asyncio
import logging
import sys
import os
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

# Import centralized configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

# Configure logging with YYMMDD HHMMSS timestamps
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%y%m%d %H%M%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Feature flags
ENABLE_MULTI_PORT = True

# Stream type for this server
STREAM_TYPE = "AveragedData"
RESOURCE_TYPE = 13  # Averaged Data FS

# Database connection string
db_configs = get_db_configs_sync()
maint_config = db_configs['maint']
MAINT_CONN_STRING = f"postgresql://{maint_config['user']}:{maint_config['password']}@{maint_config['host']}:{maint_config['port']}/{maint_config['database']}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan: Initializing DB pool")
    try:
        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            logger.debug("DB pool created successfully")
            async with pool.acquire() as conn:
                managers = await conn.fetch("SELECT X_NM_RES, i_typ_res FROM tlkresources WHERE i_typ_res = $1", RESOURCE_TYPE)
                logger.debug(f"Queried tlkresources, found {len(managers)} managers for i_typ_res={RESOURCE_TYPE}")
                for manager in managers:
                    logger.info(f"Manager {manager['x_nm_res']} (type {manager['i_typ_res']}) ready")
                    manager_name = manager['x_nm_res']
                    if manager_name not in _MANAGER_INSTANCES:
                        manager_instance = Manager(manager_name, zone_id=0)
                        _MANAGER_INSTANCES[manager_name] = manager_instance
                        logger.debug(f"Starting manager {manager_name}")
                        await manager_instance.start()
                        logger.debug(f"Manager {manager_name} started successfully")
        yield
    except Exception as e:
        logger.error(f"Lifespan error: {str(e)}")
        raise
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

# Get server host for CORS
server_host = get_server_host()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{server_host}:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
logger.debug(f"CORS middleware added with allow_origins: http://{server_host}:3000")

_MANAGER_INSTANCES = {}
_WEBSOCKET_CLIENTS = {}

@app.websocket("/ws/{manager_name}")
async def websocket_endpoint_averaged(websocket: WebSocket, manager_name: str):
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else 0
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {client_host}:{client_port}")
    async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
        async with pool.acquire() as conn:
            manager_info = await conn.fetchrow(
                "SELECT i_typ_res FROM tlkresources WHERE X_NM_RES = $1 AND i_typ_res = $2", 
                manager_name, RESOURCE_TYPE)
            if not manager_info:
                logger.error(f"Manager {manager_name} not found or invalid type")
                await websocket.close(code=1008, reason="Manager not found")
                return
    sdk_client = None
    client_id = None
    is_disconnected = False
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name}")
        if manager_name not in _MANAGER_INSTANCES:
            manager = Manager(manager_name, zone_id=0)
            _MANAGER_INSTANCES[manager_name] = manager
        else:
            manager = _MANAGER_INSTANCES[manager_name]
        client_id = f"{client_host}:{client_port}"
        sdk_client = SDKClient(websocket, client_id)
        # Type: ignore needed due to parent attribute typing
        sdk_client.parent = manager  # type: ignore
        manager.sdk_clients[client_id] = sdk_client
        sdk_client.start_q_timer()

        if manager_name not in _WEBSOCKET_CLIENTS:
            _WEBSOCKET_CLIENTS[manager_name] = []
        _WEBSOCKET_CLIENTS[manager_name].append(sdk_client)

        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message from client {client_id}: {data}")
                json_data = json.loads(data)
                msg_type = json_data.get("type", "")

                if msg_type == "HeartBeat":
                    hb = HeartBeat(ticks=json_data["ts"])
                    sdk_client.heartbeat = hb.ticks
                    await websocket.send_text(json.dumps({"type": "HeartBeat", "ts": hb.ticks}))
                    logger.debug(f"Processed HeartBeat for client {client_id}, ts: {hb.ticks}")
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
                        if resp.message:
                            await manager.close_client(sdk_client)
                            break
                    elif req.req_type == RequestType.EndStream:
                        await websocket.send_text(resp.to_json())
                        await manager.close_client(sdk_client)
                        break
                    else:
                        resp.message = "Request not supported in AveragedData stream."
                        await websocket.send_text(resp.to_json())

                else:
                    logger.warning(f"Unknown message type from client {client_id}: {msg_type}")

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for /ws/{manager_name}")
                is_disconnected = True
                await sdk_client.close()
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler: {str(e)}")
                break
    finally:
        if sdk_client and not is_disconnected:
            await sdk_client.close()
        if client_id and manager.sdk_clients and client_id in manager.sdk_clients:
            del manager.sdk_clients[client_id]
        if manager_name in _WEBSOCKET_CLIENTS and sdk_client in _WEBSOCKET_CLIENTS[manager_name]:
            _WEBSOCKET_CLIENTS[manager_name].remove(sdk_client)