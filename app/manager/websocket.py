# Name: websocket.py
# Version: 0.1.1
# Created: 250513
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS Main WebSocket server - Updated to use database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncio
import logging
import traceback
import sys
import os
import websockets  # type: ignore
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config_helper import config_helper

from .manager import Manager
from .sdk_client import SDKClient
from .models import HeartBeat, Response, ResponseType, Request, Tag
from .enums import RequestType, eMode
from .constants import REQUEST_TYPE_MAP, NEW_REQUEST_TYPES

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Cache for connection string and CORS origins
_cached_connection_string: Optional[str] = None
_cached_cors_origins: Optional[List[str]] = None

async def get_connection_string() -> str:
    """Get maintenance database connection string from config helper"""
    global _cached_connection_string
    if _cached_connection_string is None:
        try:
            # Load server configuration from database
            server_config = await config_helper.get_server_config()
            host = server_config.get('host', '192.168.210.226')
            _cached_connection_string = config_helper.get_connection_string("ParcoRTLSMaint", host)
            logger.info(f"Main WebSocket connection string configured for host: {host}")
        except Exception as e:
            logger.warning(f"Failed to load connection string from database, using fallback: {e}")
            # Fallback connection string
            _cached_connection_string = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint"
    
    return _cached_connection_string

async def get_cors_origins() -> List[str]:
    """Get CORS origins from server configuration"""
    global _cached_cors_origins
    if _cached_cors_origins is None:
        try:
            server_config = await config_helper.get_server_config()
            host = server_config.get('host', '192.168.210.226')
            _cached_cors_origins = [f"http://{host}:3000"]
            logger.info(f"CORS origins configured for host: {host}")
        except Exception as e:
            logger.warning(f"Failed to get CORS origins from config, using fallback: {e}")
            _cached_cors_origins = ["http://192.168.210.226:3000"]
    
    return _cached_cors_origins

# Stream ports configuration
STREAM_PORTS = {
    "RealTime": 8002,
    "HistoricalData": 8003,
    "OData": 8006,
    "Control": 8001
}

async def process_raw_request(path, request_headers):
    """Process raw WebSocket requests"""
    logger.debug(f"Processing raw request: path={path}, headers={dict(request_headers)}")
    return None

async def stream_handler(websocket: Any, stream_type: str):  # type: ignore
    """Handler for stream-specific WebSocket connections."""
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    logger.info(f"Stream handler for {stream_type} - client {client_id}")
    
    try:
        # Handle different stream types
        if stream_type == "RealTime":
            await handle_realtime_stream(websocket, client_id)
        elif stream_type == "HistoricalData":
            await handle_historical_stream(websocket, client_id)
        elif stream_type == "OData":
            await handle_odata_stream(websocket, client_id)
        elif stream_type == "Control":
            await handle_control_stream(websocket, client_id)
        else:
            logger.warning(f"Unknown stream type: {stream_type}")
            await websocket.close(code=1008, reason="Unknown stream type")
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Stream connection closed for {stream_type} client {client_id}")
    except Exception as e:
        logger.error(f"Error in stream handler for {stream_type}: {e}")
        await websocket.close(code=1011, reason="Internal error")

async def handle_realtime_stream(websocket: Any, client_id: str):  # type: ignore
    """Handle real-time stream connections"""
    logger.info(f"Handling real-time stream for client {client_id}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            logger.debug(f"Real-time message from {client_id}: {data}")
            
            # Echo back for now - implement actual real-time logic
            response = {"type": "ack", "original": data}
            await websocket.send(json.dumps(response))
            
    except Exception as e:
        logger.error(f"Error in real-time stream for {client_id}: {e}")

async def handle_historical_stream(websocket: Any, client_id: str):  # type: ignore
    """Handle historical data stream connections"""
    logger.info(f"Handling historical stream for client {client_id}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            logger.debug(f"Historical message from {client_id}: {data}")
            
            # Echo back for now - implement actual historical logic
            response = {"type": "historical_ack", "original": data}
            await websocket.send(json.dumps(response))
            
    except Exception as e:
        logger.error(f"Error in historical stream for {client_id}: {e}")

async def handle_odata_stream(websocket: Any, client_id: str):  # type: ignore
    """Handle OData stream connections"""
    logger.info(f"Handling OData stream for client {client_id}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            logger.debug(f"OData message from {client_id}: {data}")
            
            # Echo back for now - implement actual OData logic
            response = {"type": "odata_ack", "original": data}
            await websocket.send(json.dumps(response))
            
    except Exception as e:
        logger.error(f"Error in OData stream for {client_id}: {e}")

async def handle_control_stream(websocket: Any, client_id: str):  # type: ignore
    """Handle control stream connections"""
    logger.info(f"Handling control stream for client {client_id}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            logger.debug(f"Control message from {client_id}: {data}")
            
            # Echo back for now - implement actual control logic
            response = {"type": "control_ack", "original": data}
            await websocket.send(json.dumps(response))
            
    except Exception as e:
        logger.error(f"Error in control stream for {client_id}: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan: Initializing connection string and DB pool")
    try:
        # Initialize connection string
        maint_conn_string = await get_connection_string()
        
        async with asyncpg.create_pool(maint_conn_string) as pool:
            logger.debug("DB pool created successfully")
            async with pool.acquire() as conn:
                logger.debug("Acquired DB connection, querying tlkresources")
                managers = await conn.fetch("SELECT X_NM_RES FROM tlkresources")
                logger.debug(f"Queried tlkresources, found {len(managers)} managers")
                for manager in managers:
                    name = manager['x_nm_res']
                    logger.info(f"Manager {name} ready to accept connections")

        # Start WebSocket servers for stream ports
        servers = []
        for stream_type, port in STREAM_PORTS.items():
            async def handler(ws, path=None, stream_type=stream_type):  # Capture stream_type in closure
                logger.debug(f"Handler called with ws={ws}, path={path}, stream_type={stream_type}")
                await stream_handler(ws, stream_type)
            
            server = await websockets.serve(
                handler,
                host="0.0.0.0",
                port=port,
                process_request=process_raw_request
            )
            logger.info(f"Started WebSocket server for {stream_type} on port {port}")
            servers.append(server)
        
        yield
        
        # Close WebSocket servers on shutdown
        for server in servers:
            server.close()
            await server.wait_closed()
            if server.sockets:
                logger.info(f"Closed WebSocket server for port {server.sockets[0].getsockname()[1]}")
            else:
                logger.info(f"Closed WebSocket server (no active sockets)")
    
    except Exception as e:
        logger.error(f"Lifespan error: {str(e)}\n{traceback.format_exc()}")
        raise
    logger.info("Application shutdown")

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

REQUEST_TYPE_MAP = {
    "BeginStream": RequestType.BeginStream,
    "EndStream": RequestType.EndStream,
    "AddTag": RequestType.AddTag,
    "RemoveTag": RequestType.RemoveTag
}

_MANAGER_INSTANCES = {}
_WEBSOCKET_CLIENTS = {}

@app.websocket("/ws/{manager_name}")
async def websocket_endpoint_main(websocket: WebSocket, manager_name: str):
    """Main WebSocket endpoint for manager connections"""
    client_host = websocket.client.host  # type: ignore
    client_port = websocket.client.port  # type: ignore
    client_id = f"{client_host}:{client_port}"
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {client_id}")

    maint_conn_string = await get_connection_string()
    
    async with asyncpg.create_pool(maint_conn_string) as pool:
        async with pool.acquire() as conn:
            res = await conn.fetchval("SELECT COUNT(*) FROM tlkresources WHERE X_NM_RES = $1", manager_name)
            if not res:
                logger.error(f"Manager {manager_name} not found in tlkresources")
                await websocket.close(code=1008, reason="Manager not found")
                return
    
    sdk_client = None
    is_disconnected = False
    try:
        logger.debug(f"Attempting to accept WebSocket for {manager_name}")
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name}")
        
        if manager_name not in _MANAGER_INSTANCES:
            manager = Manager(manager_name, zone_id=None)  # type: ignore
            logger.debug(f"Created new Manager instance for {manager_name} with initial zone_id=None")
            _MANAGER_INSTANCES[manager_name] = manager
        else:
            manager = _MANAGER_INSTANCES[manager_name]
            logger.debug(f"Using existing Manager instance for {manager_name}, current zone_id={manager.zone_id}")
        
        sdk_client = SDKClient(websocket, client_id)
        sdk_client.parent = manager  # type: ignore
        manager.sdk_clients[client_id] = sdk_client
        logger.debug(f"Starting q_timer for {client_id}")
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
                        continue

                    req = Request(
                        req_type=req_type,
                        req_id=req_id,
                        tags=[Tag(id=tag["id"], send_payload_data=tag["data"] == "true") 
                              for tag in json_data.get("params", [])]
                    )
                    
                    if zone_id is not None:
                        if manager.zone_id != zone_id:
                            manager.zone_id = zone_id
                            await manager.load_triggers(zone_id)
                            logger.info(f"Manager {manager_name} zone changed to {zone_id}, triggers reloaded")

                    sdk_client.request_msg = req  # type: ignore
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
                        if resp.message:
                            await manager.close_client(sdk_client)
                            break
                            
                    elif req.req_type == RequestType.EndStream:
                        await websocket.send_text(resp.to_json())
                        await manager.close_client(sdk_client)
                        logger.info(f"EndStream processed for client {client_id}")
                        break
                        
                    elif req.req_type == RequestType.AddTag:
                        if req.tags:
                            for t in req.tags:
                                sdk_client.add_tag(t.id, t)
                            logger.info(f"AddTag processed for client {client_id}, tags: {[t.id for t in req.tags]}")
                        await websocket.send_text(resp.to_json())
                        
                    elif req.req_type == RequestType.RemoveTag:
                        if req.tags:
                            for t in req.tags:
                                sdk_client.remove_tag(t.id)
                            logger.info(f"RemoveTag processed for client {client_id}, tags: {[t.id for t in req.tags]}")
                        await websocket.send_text(resp.to_json())
                        
                    else:
                        resp.message = f"Request type {request_type} not supported."
                        await websocket.send_text(resp.to_json())
                        logger.debug(f"Unsupported request type {request_type} from client {client_id}")

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
        if client_id in manager.sdk_clients:
            del manager.sdk_clients[client_id]
        if manager_name in _WEBSOCKET_CLIENTS and sdk_client in _WEBSOCKET_CLIENTS[manager_name]:
            _WEBSOCKET_CLIENTS[manager_name].remove(sdk_client)
        logger.info(f"WebSocket cleanup completed for client {client_id}")

def refresh_connection_config():
    """Clear cached connection configuration to force reload"""
    global _cached_connection_string, _cached_cors_origins
    _cached_connection_string = None
    _cached_cors_origins = None
    logger.info("Main WebSocket connection configuration cache cleared")