# Name: websocket_control.py
# Version: 0.1.6
# Created: 250513
# Modified: 250717
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & TC & AI Assistant
# Description: Python script for ParcoRTLS Control WebSocket server on port 8001 - Added GISData forwarding to RealTime Manager - Added heartbeat integration for port monitoring and scaling - Added PortRedirect support for simulator v0.1.23 - Updated to use centralized configuration - Added message type tracking for heartbeat filtering
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncio
import logging
import os
import stat
import sys
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import json
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config_helper import config_helper
from config import get_server_host

from .manager import Manager
from .sdk_client import SDKClient
from .models import HeartBeat, Response, ResponseType, Request, Tag
from .enums import RequestType, eMode
from .constants import REQUEST_TYPE_MAP, NEW_REQUEST_TYPES
from .line_limited_logging import LineLimitedFileHandler
from .heartbeat_manager import HeartbeatManager

# Import heartbeat integration
from .heartbeat_integration import heartbeat_integration

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

# Default redirect port for RealTime stream
DEFAULT_REALTIME_PORT = 8002

# Cache for connection string and CORS origins
_cached_connection_string: Optional[str] = None
_cached_cors_origins: Optional[list] = None

# NEW: GIS Data forwarding connection
_realtime_manager_ws: Optional[object] = None  # websockets client connection
_realtime_connected = False

async def get_connection_string() -> str:
    """Get maintenance database connection string from config helper"""
    global _cached_connection_string
    if _cached_connection_string is None:
        try:
            # Load server configuration from database
            server_config = await config_helper.get_server_config()
            host = server_config.get('host', get_server_host())
            _cached_connection_string = config_helper.get_connection_string("ParcoRTLSMaint", host)
            logger.info(f"Control server connection string configured for host: {host}")
        except Exception as e:
            logger.warning(f"Failed to load connection string from database, using fallback: {e}")
            # Fallback connection string using centralized config
            fallback_host = get_server_host()
            _cached_connection_string = f"postgresql://parcoadmin:parcoMCSE04106!@{fallback_host}:5432/ParcoRTLSMaint"
    
    return _cached_connection_string

async def get_cors_origins() -> list:
    """Get CORS origins from server configuration"""
    global _cached_cors_origins
    if _cached_cors_origins is None:
        try:
            server_config = await config_helper.get_server_config()
            host = server_config.get('host', get_server_host())
            _cached_cors_origins = [f"http://{host}:3000"]
            logger.info(f"CORS origins configured for host: {host}")
        except Exception as e:
            logger.warning(f"Failed to get CORS origins from config, using fallback: {e}")
            # Fallback CORS origins using centralized config
            fallback_host = get_server_host()
            _cached_cors_origins = [f"http://{fallback_host}:3000"]
    
    return _cached_cors_origins

# NEW: RealTime Manager connection functions
async def connect_to_realtime_manager() -> bool:
    """
    Connect to RealTime Manager on Port 8002 for GIS data forwarding.
    
    Returns:
        bool: True if connected successfully
    """
    global _realtime_manager_ws, _realtime_connected
    
    try:
        server_host = get_server_host()
        realtime_url = f"ws://{server_host}:{DEFAULT_REALTIME_PORT}/ws/RealTimeManager"
        
        logger.info(f"🔗 Connecting to RealTime Manager at {realtime_url}")
        file_handler.flush()
        
        _realtime_manager_ws = await websockets.connect(realtime_url)
        
        logger.info("✅ Connected to RealTime Manager, sending BeginStream handshake")
        file_handler.flush()
        
        # Send BeginStream for GIS data forwarding
        begin_stream_msg = {
            "type": "request",
            "request": "BeginStream", 
            "reqid": "ControlManagerBridge",
            "params": [
                {"id": "26102", "data": "true"},
                {"id": "26099", "data": "true"},
                {"id": "13351", "data": "true"}
            ],
            "zone_id": 451
        }
        
        await _realtime_manager_ws.send(json.dumps(begin_stream_msg))  # type: ignore
        logger.info(f"📤 Sent BeginStream to RealTime Manager: {begin_stream_msg}")
        file_handler.flush()
        
        # Wait for response
        try:
            response_data = await asyncio.wait_for(_realtime_manager_ws.recv(), timeout=5.0)  # type: ignore
            response = json.loads(response_data)
            
            logger.info(f"📥 Received response from RealTime Manager: {response}")
            file_handler.flush()
            
            if response.get("type") == "response" and response.get("request") == "BgnStrm":
                if not response.get("message"):  # Empty message means success
                    logger.info("✅ BeginStream handshake successful with RealTime Manager")
                    _realtime_connected = True
                    return True
                else:
                    logger.error(f"❌ BeginStream failed: {response.get('message')}")
                    return False
            else:
                logger.error(f"❌ Unexpected response format: {response}")
                return False
        except asyncio.TimeoutError:
            logger.error("❌ Timeout waiting for BeginStream response from RealTime Manager")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to RealTime Manager: {str(e)}")
        file_handler.flush()
        _realtime_manager_ws = None
        _realtime_connected = False
        return False

async def forward_gis_data_to_realtime(gis_data: dict):
    """
    Forward GIS data to RealTime Manager on port 8002.
    
    Args:
        gis_data: GIS data message to forward
    """
    global _realtime_manager_ws, _realtime_connected
    
    if not _realtime_connected or _realtime_manager_ws is None:
        logger.warning("⚠️ RealTime Manager not connected, attempting reconnection")
        file_handler.flush()
        
        if not await connect_to_realtime_manager():
            logger.error("❌ Failed to connect to RealTime Manager, dropping GIS data")
            file_handler.flush()
            return
    
    try:
        # Forward the GIS data to RealTime Manager
        await _realtime_manager_ws.send(json.dumps(gis_data))  # type: ignore
        logger.info(f"✅ Forwarded GIS data to RealTime Manager for tag {gis_data.get('ID')}")
        file_handler.flush()
        
    except Exception as e:
        logger.error(f"❌ Failed to forward GIS data to RealTime Manager: {str(e)}")
        file_handler.flush()
        
        # Reset connection on error
        _realtime_manager_ws = None
        _realtime_connected = False

# Heartbeat configuration
HEARTBEAT_INTERVAL = 30.0  # Heartbeat every 30 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan: Initializing connection string and DB pool")
    file_handler.flush()
    try:
        # Initialize connection string
        maint_conn_string = await get_connection_string()
        
        async with asyncpg.create_pool(maint_conn_string) as pool:
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
                        # Fix: Use default zone_id instead of None
                        manager_instance = Manager(manager_name, zone_id=1)  
                        _MANAGER_INSTANCES[manager_name] = manager_instance
                        logger.debug(f"Starting manager {manager_name}")
                        file_handler.flush()
                        await manager_instance.start()
                        logger.debug(f"Manager {manager_name} started successfully")
                        file_handler.flush()
                        
                        # Register manager with heartbeat integration
                        heartbeat_integration.register_manager(manager_name, manager_instance)
                        logger.debug(f"Registered manager {manager_name} with heartbeat integration")
                        file_handler.flush()
        
        # NEW: Initialize connection to RealTime Manager
        logger.info("🔗 Initializing connection to RealTime Manager for GIS data forwarding")
        file_handler.flush()
        await connect_to_realtime_manager()
                        
        yield
    except Exception as e:
        logger.error(f"Lifespan error: {str(e)}")
        file_handler.flush()
        raise
    finally:
        # NEW: Cleanup RealTime Manager connection
        if _realtime_manager_ws is not None:
            await _realtime_manager_ws.close()  # type: ignore
            logger.info("🔌 Disconnected from RealTime Manager")
            file_handler.flush()
    logger.info("Application shutdown")
    file_handler.flush()

app = FastAPI(lifespan=lifespan)

# Configure CORS middleware with dynamic origins
@app.on_event("startup")
async def configure_cors():
    """Configure CORS with dynamic origins after server config is loaded"""
    cors_origins = await get_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    logger.debug(f"CORS middleware added with allow_origins: {cors_origins}")
    file_handler.flush()

_MANAGER_INSTANCES = {}
_WEBSOCKET_CLIENTS = {}

@app.websocket("/ws/{manager_name}")
async def websocket_endpoint_control(websocket: WebSocket, manager_name: str):
    # Fix: Handle potential None client
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else 0
    client_id = f"{client_host}:{client_port}"
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {client_id}")
    file_handler.flush()

    maint_conn_string = await get_connection_string()
    
    async with asyncpg.create_pool(maint_conn_string) as pool:
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
    is_disconnected = False
    manager = None
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name}")
        file_handler.flush()
        
        if manager_name not in _MANAGER_INSTANCES:
            # Fix: Use default zone_id instead of None
            manager = Manager(manager_name, zone_id=1)
            _MANAGER_INSTANCES[manager_name] = manager
        else:
            manager = _MANAGER_INSTANCES[manager_name]
            
        sdk_client = SDKClient(websocket, client_id)
        # Note: Setting parent - SDKClient.parent may be typed as None
        sdk_client.parent = manager  # type: ignore
        manager.sdk_clients[client_id] = sdk_client
        sdk_client.start_q_timer()

        if manager_name not in _WEBSOCKET_CLIENTS:
            _WEBSOCKET_CLIENTS[manager_name] = []
        _WEBSOCKET_CLIENTS[manager_name].append(sdk_client)

        # Initialize heartbeat manager (note: some methods may not exist)
        heartbeat_manager = HeartbeatManager(websocket, str(HEARTBEAT_INTERVAL))
        # Note: HeartbeatManager.start may not exist

        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message from client {client_id}: {data}")
                file_handler.flush()
                
                json_data = json.loads(data)
                msg_type = json_data.get("type", "")
                sdk_client.last_message_type = msg_type  # Track last received message type for heartbeat filtering

                if msg_type == "HeartBeat":
                    hb = HeartBeat(ticks=json_data["ts"])
                    sdk_client.heartbeat = hb.ticks
                    # Note: HeartbeatManager.handle_heartbeat may not exist, using basic heartbeat handling
                    logger.debug(f"Processed HeartBeat for client {client_id}, ts: {hb.ticks}")
                    file_handler.flush()
                    continue

                # NEW: GISData forwarding logic
                elif msg_type == "GISData":
                    tag_id = json_data.get("ID")
                    zone_id = json_data.get("zone_id")
                    x = json_data.get("X", 0.0)
                    y = json_data.get("Y", 0.0)
                    z = json_data.get("Z", 0.0)
                    
                    logger.info(f"🔄 Processing GISData for tag {tag_id} in zone {zone_id} from client {client_id}")
                    file_handler.flush()
                    
                    # Forward GIS data to RealTime Manager
                    await forward_gis_data_to_realtime(json_data)
                    
                    logger.info(f"✅ GIS data processing complete for tag {tag_id}")
                    file_handler.flush()
                    continue

                elif msg_type == "request":
                    request_type = json_data.get("request", "")
                    req_id = json_data.get("reqid", "")
                    zone_id = json_data.get("zone_id")

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
                    
                    # Store zone_id separately since Request may not have zone_id attribute
                    request_zone_id = zone_id
                    if request_zone_id is not None:
                        if manager.zone_id != request_zone_id:
                            manager.zone_id = request_zone_id
                            await manager.load_triggers(request_zone_id)
                            logger.info(f"Manager {manager_name} zone changed to {request_zone_id}, triggers reloaded")
                            file_handler.flush()

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
                        logger.info(f"BeginStream processed for client {client_id}, tags: {[t.id for t in req.tags]}")
                        file_handler.flush()
                        
                        if not resp.message:  # Only send PortRedirect if BeginStream was successful
                            # Send PortRedirect message to inform simulator of RealTime stream port
                            port_redirect_msg = {
                                "type": "PortRedirect",
                                "port": DEFAULT_REALTIME_PORT,
                                "stream_type": "RealTime",
                                "manager_name": "RealTimeManager"
                            }
                            await websocket.send_text(json.dumps(port_redirect_msg))
                            logger.info(f"Sent PortRedirect to client {client_id}, redirecting to port {DEFAULT_REALTIME_PORT}")
                            file_handler.flush()
                        else:
                            await manager.close_client(sdk_client)
                            break
                            
                    elif req.req_type == RequestType.EndStream:
                        await websocket.send_text(resp.to_json())
                        await manager.close_client(sdk_client)
                        logger.info(f"EndStream processed for client {client_id}")
                        file_handler.flush()
                        break
                        
                    elif req.req_type == RequestType.AddTag:
                        if req.tags:
                            for t in req.tags:
                                sdk_client.add_tag(t.id, t)
                            logger.info(f"AddTag processed for client {client_id}, tags: {[t.id for t in req.tags]}")
                            file_handler.flush()
                        await websocket.send_text(resp.to_json())
                        
                    elif req.req_type == RequestType.RemoveTag:
                        if req.tags:
                            for t in req.tags:
                                sdk_client.remove_tag(t.id)
                            logger.info(f"RemoveTag processed for client {client_id}, tags: {[t.id for t in req.tags]}")
                            file_handler.flush()
                        await websocket.send_text(resp.to_json())
                        
                    else:
                        resp.message = f"Request type {request_type} not supported in Control stream."
                        await websocket.send_text(resp.to_json())
                        logger.debug(f"Unsupported request type {request_type} from client {client_id}")
                        file_handler.flush()

                else:
                    logger.warning(f"Unknown message type from client {client_id}: {msg_type}")
                    file_handler.flush()

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for /ws/{manager_name}")
                file_handler.flush()
                is_disconnected = True
                if sdk_client:
                    await sdk_client.close()
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler: {str(e)}")
                file_handler.flush()
                break
    finally:
        if sdk_client and not is_disconnected:
            await sdk_client.close()
        if manager and hasattr(manager, 'sdk_clients') and client_id in manager.sdk_clients:
            del manager.sdk_clients[client_id]
        if manager_name in _WEBSOCKET_CLIENTS and sdk_client and sdk_client in _WEBSOCKET_CLIENTS[manager_name]:
            _WEBSOCKET_CLIENTS[manager_name].remove(sdk_client)
        logger.info(f"WebSocket cleanup completed for client {client_id}")
        file_handler.flush()

def refresh_connection_config():
    """Clear cached connection configuration to force reload"""
    global _cached_connection_string, _cached_cors_origins
    _cached_connection_string = None
    _cached_cors_origins = None
    logger.info("Connection configuration cache cleared")
    file_handler.flush()