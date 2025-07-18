# Name: websocket_subscription.py
# Version: 0.1.2
# Created: 250516
# Modified: 250716
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & AI Assistant
# Description: Python script for ParcoRTLS Subscription WebSocket server on port 8005 - Added heartbeat integration for port monitoring
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/websocket_subscription.py
# Version: 0.1.2 - Added heartbeat integration for port monitoring, bumped from 0.1.1
# Version: 0.1.1 - Updated with centralized IP configuration and syntax fixes, bumped from 0.1.0
# Version: 0.1.0 - Initial implementation for Subscription stream on port 8005
# Note: This server handles subscription-based data streaming for ParcoRTLS, using R and T Raw Sub (i_typ_res=7).

import asyncio
import logging
import sys
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextual import asynccontextmanager # type: ignore
import asyncpg
import json
from datetime import datetime
from .manager import Manager
from .sdk_client import SDKClient
from .models import HeartBeat, Response, ResponseType, Request, Tag
from .enums import RequestType, eMode
from .constants import REQUEST_TYPE_MAP, NEW_REQUEST_TYPES
from .heartbeat_manager import HeartbeatManager

# Import heartbeat integration
from .heartbeat_integration import heartbeat_integration

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
STREAM_TYPE = "Subscription"
RESOURCE_TYPE = 7  # R and T Raw Sub

# Heartbeat configuration
HEARTBEAT_INTERVAL = 30

# Get centralized configuration
server_host = get_server_host()
db_configs = get_db_configs_sync()
maint_config = db_configs['maint']

# Database connection string
MAINT_CONN_STRING = f"postgresql://{maint_config['user']}:{maint_config['password']}@{server_host}:{maint_config['port']}/{maint_config['database']}"

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
                        
                        # Register manager with heartbeat integration
                        heartbeat_integration.register_manager(manager_name, manager_instance)
                        logger.debug(f"Registered manager {manager_name} with heartbeat integration")
                        
        yield
    except Exception as e:
        logger.error(f"Lifespan error: {str(e)}")
        raise
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan) # type: ignore

# Get CORS origins from centralized config
cors_origins = [f"http://{server_host}:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
logger.debug(f"CORS middleware added with allow_origins: {cors_origins[0]}")

_MANAGER_INSTANCES = {}
_WEBSOCKET_CLIENTS = {}

@app.websocket("/ws/{manager_name}")
async def websocket_endpoint_subscription(websocket: WebSocket, manager_name: str):
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else 0
    client_id = f"{client_host}:{client_port}"
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {client_id}")
    
    # Initialize HeartbeatManager
    heartbeat_manager = HeartbeatManager(websocket, client_id=client_id, interval=HEARTBEAT_INTERVAL, timeout=5)
    
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
    is_disconnected = False
    manager = None
    heartbeat_task = None
    
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name} from {client_id}")
        
        if manager_name not in _MANAGER_INSTANCES:
            manager = Manager(manager_name, zone_id=0)
            _MANAGER_INSTANCES[manager_name] = manager
            
            # Register fallback manager with heartbeat integration
            heartbeat_integration.register_manager(manager_name, manager)
            logger.debug(f"Registered fallback manager {manager_name} with heartbeat integration")
        else:
            manager = _MANAGER_INSTANCES[manager_name]
            
        sdk_client = SDKClient(websocket, client_id)
        
        # Set parent relationship using setattr to bypass type checking
        setattr(sdk_client, 'parent', manager)
        
        manager.sdk_clients[client_id] = sdk_client
        sdk_client.start_q_timer()

        if manager_name not in _WEBSOCKET_CLIENTS:
            _WEBSOCKET_CLIENTS[manager_name] = []
        _WEBSOCKET_CLIENTS[manager_name].append(sdk_client)

        # Log client connection for outbound port monitoring
        logger.info(f"SCALING: Subscription port 8005 client count: {len(_WEBSOCKET_CLIENTS[manager_name])} (outbound client {client_id} connected)")

        # Start heartbeat loop
        heartbeat_task = asyncio.create_task(heartbeat_loop(heartbeat_manager))

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=HEARTBEAT_INTERVAL)
                logger.debug(f"Received WebSocket message from client {client_id}: {data}")
                json_data = json.loads(data)
                msg_type = json_data.get("type", "")
                sdk_client.last_message_type = msg_type

                if msg_type == "HeartBeat":
                    # Validate heartbeat with HeartbeatManager
                    heartbeat_result = heartbeat_manager.validate_response(json_data)
                    if heartbeat_result is False:
                        await websocket.send_json({
                            "type": "EndStream",
                            "reason": "Too many invalid heartbeats"
                        })
                        logger.info(f"Sent EndStream to Subscription client {client_id}: Too many invalid heartbeats")
                        sdk_client.is_closing = True
                        break
                    elif heartbeat_result is True:
                        if heartbeat_manager.too_frequent():
                            await websocket.send_json({
                                "type": "Warning",
                                "reason": "Heartbeat too frequent"
                            })
                            logger.debug(f"Sent warning to Subscription client {client_id}: Heartbeat too frequent")
                    # Handle legacy heartbeats
                    elif heartbeat_result is None:
                        hb = HeartBeat(ticks=json_data["ts"])
                        sdk_client.heartbeat = hb.ticks
                        await websocket.send_text(json.dumps({"type": "HeartBeat", "ts": hb.ticks}))
                        logger.debug(f"Processed legacy HeartBeat for client {client_id}, ts: {hb.ticks}")
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
                    
                    # Set request_msg using setattr to bypass type checking
                    setattr(sdk_client, 'request_msg', req)
                    
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
                        logger.info(f"Subscription client {client_id} subscribed to tags: {[t.id for t in req.tags]}")
                        if resp.message:
                            await manager.close_client(sdk_client)
                            break
                    elif req.req_type == RequestType.EndStream:
                        await websocket.send_text(resp.to_json())
                        logger.info(f"Sent EndStream response to Subscription client {client_id}")
                        await manager.close_client(sdk_client)
                        break
                    else:
                        resp.message = "Request not supported in Subscription stream."
                        await websocket.send_text(resp.to_json())
                        logger.debug(f"Sent error response to client {client_id}: {resp.to_json()}")

                else:
                    logger.warning(f"Unknown message type from client {client_id}: {msg_type}")

            except asyncio.TimeoutError:
                # Timeout allows periodic heartbeat checks
                continue
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for /ws/{manager_name}")
                is_disconnected = True
                if sdk_client:
                    await sdk_client.close()
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler: {str(e)}")
                break
    finally:
        if sdk_client and not is_disconnected:
            await sdk_client.close()
        if manager and hasattr(manager, 'sdk_clients') and client_id in manager.sdk_clients:
            del manager.sdk_clients[client_id]
        if manager_name in _WEBSOCKET_CLIENTS and sdk_client and sdk_client in _WEBSOCKET_CLIENTS[manager_name]:
            _WEBSOCKET_CLIENTS[manager_name].remove(sdk_client)
        if heartbeat_task:
            heartbeat_task.cancel()
            
        # Log client disconnection for outbound port monitoring
        remaining_clients = len(_WEBSOCKET_CLIENTS.get(manager_name, []))
        logger.info(f"SCALING: Subscription port 8005 client count: {remaining_clients} (outbound client {client_id} disconnected)")
        
        logger.info(f"Cleaned up Subscription client {client_id} for /ws/{manager_name}")

async def heartbeat_loop(heartbeat_manager: HeartbeatManager):
    """Heartbeat loop for Subscription clients"""
    while heartbeat_manager.is_connected():
        await heartbeat_manager.send_heartbeat()
        await heartbeat_manager.check_timeout()
        await asyncio.sleep(HEARTBEAT_INTERVAL)