# Name: websocket_alltraq.py
# Version: 0.1.7
# Created: 250717
# Modified: 250717
# Creator: AI Assistant
# Modified By: AI Assistant
# Description: AllTraq WebSocket Server on port 18002 to receive AllTraq data and forward to Control Manager
# Location: /home/parcoadmin/parco_fastapi/app/manager/websocket_alltraq.py
# Role: AllTraq Data Bridge
# Status: Active
# Dependent: TRUE
#
# Version: 0.1.7 - FIXED: Removed timeout parameter causing connection failure, bumped from 0.1.6
# Version: 0.1.6 - Fixed proper routing to Port 8001 Control Manager, bumped from 0.1.5
# Version: 0.1.5 - Fixed proper routing to Port 8001 Control Manager, bumped from 0.1.4
# Version: 0.1.4 - EXPERIMENTAL: Direct forwarding to Port 8001 bypass (creates technical debt)
# Version: 0.1.3 - Enhanced dashboard broadcasting with proper GIS data handling
# Version: 0.1.2 - Added HTTP endpoint for dashboard message broadcasting  
# Version: 0.1.1 - Added BeginStream handshake and AllTraq authentication
# Version: 0.1.0 - Initial implementation for AllTraq data reception
# AllTraq is a registered trademark of ABG Tag and Traq Inc (Oklahoma) Serial Num 87037989 for Goods & Service IC 009

import asyncio
import logging
import os
import sys
import json
import websockets
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any
import httpx

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host
from manager.line_limited_logging import LineLimitedFileHandler

# Log directory and file
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "websocket_alltraq.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("manager.websocket_alltraq")
logger.setLevel(logging.DEBUG)

# StreamHandler for console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

# LineLimitedFileHandler for file
file_handler = LineLimitedFileHandler(
    LOG_FILE,
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

logger.handlers = [stream_handler, file_handler]
logger.propagate = False

logger.info("Starting AllTraq WebSocket Bridge server on port 18002")
file_handler.flush()

# Configuration
DEFAULT_ZONE_ID = 451  # AllTraq default zone
CONTROL_MANAGER_PORT = 8001
REALTIME_MANAGER_PORT = 8002

# Get server host
server_host = get_server_host()

# Dashboard message model
class DashboardMessage(BaseModel):
    type: str
    ID: str
    Type: str
    TS: str
    X: float
    Y: float
    Z: float
    Bat: int
    CNF: float
    GWID: str
    Sequence: int
    zone_id: int

# Connection tracking
_ALLTRAQ_CLIENTS: Dict[str, WebSocket] = {}
_CONTROL_MANAGER_WS: Optional[Any] = None
_MANAGER_CONNECTED = False

async def connect_to_control_manager() -> bool:
    """
    Connect to Control Manager on Port 8001 with proper BeginStream handshake.
    
    Returns:
        bool: True if connected and handshake successful
    """
    global _CONTROL_MANAGER_WS, _MANAGER_CONNECTED
    
    try:
        logger.info(f"Connecting to Control Manager at ws://{server_host}:{CONTROL_MANAGER_PORT}/ws/ControlManager")
        file_handler.flush()
        
        # FIXED v0.1.7: Removed timeout parameter - not supported in this websockets version
        _CONTROL_MANAGER_WS = await websockets.connect(
            f"ws://{server_host}:{CONTROL_MANAGER_PORT}/ws/ControlManager"
        )
        assert _CONTROL_MANAGER_WS is not None  # Type assertion for Pylance
        
        logger.info("✅ FIXED v0.1.7: Connected to Control Manager, sending BeginStream handshake")
        file_handler.flush()
        
        # Send BeginStream for AllTraq tags - using a representative sample
        begin_stream_msg = {
            "type": "request",
            "request": "BeginStream", 
            "reqid": "AllTraqBridge",
            "params": [
                {"id": "26102", "data": "true"},
                {"id": "26099", "data": "true"},
                {"id": "13351", "data": "true"}
            ],
            "zone_id": DEFAULT_ZONE_ID
        }
        
        await _CONTROL_MANAGER_WS.send(json.dumps(begin_stream_msg))
        logger.info(f"📤 Sent BeginStream to Control Manager: {begin_stream_msg}")
        file_handler.flush()
        
        # Wait for response using asyncio.wait_for for timeout
        try:
            response_data = await asyncio.wait_for(_CONTROL_MANAGER_WS.recv(), timeout=5.0)
            response = json.loads(response_data)
            
            logger.info(f"📥 Received response from Control Manager: {response}")
            file_handler.flush()
            
            if response.get("type") == "response" and response.get("request") == "BgnStrm":
                if not response.get("message"):  # Empty message means success
                    logger.info("✅ BeginStream handshake successful with Control Manager")
                    _MANAGER_CONNECTED = True
                    
                    # Start listening for responses and redirects
                    asyncio.create_task(listen_to_control_manager())
                    
                    return True
                else:
                    logger.error(f"❌ BeginStream failed: {response.get('message')}")
                    return False
            else:
                logger.error(f"❌ Unexpected response format: {response}")
                return False
        except asyncio.TimeoutError:
            logger.error("❌ Timeout waiting for BeginStream response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to Control Manager: {str(e)}")
        file_handler.flush()
        _CONTROL_MANAGER_WS = None
        _MANAGER_CONNECTED = False
        return False

async def listen_to_control_manager():
    """Listen for responses from Control Manager including PortRedirect."""
    global _CONTROL_MANAGER_WS
    
    try:
        if _CONTROL_MANAGER_WS is None:
            return
            
        async for message in _CONTROL_MANAGER_WS:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                
                logger.debug(f"📨 Received from Control Manager: {data}")
                file_handler.flush()
                
                if msg_type == "PortRedirect":
                    port = data.get("port", REALTIME_MANAGER_PORT)
                    logger.info(f"🔄 Control Manager redirected to port {port}")
                    file_handler.flush()
                    
                elif msg_type == "HeartBeat":
                    # Respond to heartbeats
                    heartbeat_response = {
                        "type": "HeartBeat",
                        "ts": data.get("ts")
                    }
                    if _CONTROL_MANAGER_WS is not None:
                        await _CONTROL_MANAGER_WS.send(json.dumps(heartbeat_response))
                        logger.debug(f"💓 Heartbeat response sent: {heartbeat_response}")
                        file_handler.flush()
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse Control Manager message: {e}")
                file_handler.flush()
                
    except websockets.exceptions.ConnectionClosed:
        logger.warning("⚠️ Control Manager connection closed")
        _CONTROL_MANAGER_WS = None
        _MANAGER_CONNECTED = False
        file_handler.flush()
    except Exception as e:
        logger.error(f"❌ Error listening to Control Manager: {str(e)}")
        file_handler.flush()

async def forward_gis_data_to_control_manager(gis_data: dict):
    """
    Forward GIS data to Control Manager.
    
    Args:
        gis_data: AllTraq GIS data message
    """
    global _CONTROL_MANAGER_WS, _MANAGER_CONNECTED
    
    if not _MANAGER_CONNECTED or _CONTROL_MANAGER_WS is None:
        logger.warning("⚠️ Control Manager not connected, attempting reconnection")
        file_handler.flush()
        
        if not await connect_to_control_manager():
            logger.error("❌ Failed to connect to Control Manager, dropping GIS data")
            file_handler.flush()
            return
    
    try:
        # Forward the GIS data as-is to Control Manager
        if _CONTROL_MANAGER_WS is not None:
            await _CONTROL_MANAGER_WS.send(json.dumps(gis_data))
            logger.info(f"✅ Forwarded GIS data to Control Manager for tag {gis_data.get('ID')}")
            file_handler.flush()
        
    except Exception as e:
        logger.error(f"❌ Failed to forward GIS data to Control Manager: {str(e)}")
        file_handler.flush()
        
        # Reset connection on error
        _CONTROL_MANAGER_WS = None
        _MANAGER_CONNECTED = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting AllTraq WebSocket Bridge")
    file_handler.flush()
    
    # Attempt initial connection to Control Manager
    await connect_to_control_manager()
    
    yield
    
    # Cleanup on shutdown
    if _CONTROL_MANAGER_WS is not None:
        await _CONTROL_MANAGER_WS.close()
        logger.info("🔌 Disconnected from Control Manager")
        file_handler.flush()
    
    logger.info("🛑 AllTraq WebSocket Bridge shutdown")
    file_handler.flush()

app = FastAPI(lifespan=lifespan)

# Configure CORS
cors_origins = [f"http://{server_host}:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
logger.debug(f"CORS middleware added with allow_origins: {cors_origins[0]}")
file_handler.flush()

@app.post("/broadcast_dashboard_message")
async def broadcast_dashboard_message(message: DashboardMessage):
    """
    HTTP endpoint to receive AllTraq GIS data and forward to Control Manager.
    
    This endpoint receives data from alltraq_service.py and forwards it to the
    Control Manager which then routes it to the appropriate RealTime streams.
    
    FIXED: Now properly forwards HTTP POST data to Control Manager.
    """
    try:
        logger.info(f"📥 HTTP POST: Received AllTraq GIS data for tag {message.ID} in zone {message.zone_id}")
        logger.debug(f"📊 GIS Data: X={message.X}, Y={message.Y}, Z={message.Z}, CNF={message.CNF}")
        file_handler.flush()
        
        # Convert message to dict for forwarding
        gis_data = message.dict()
        
        # CRITICAL FIX: Forward HTTP POST data to Control Manager
        logger.info(f"🔄 v0.1.7: Forwarding HTTP POST AllTraq data to Control Manager for tag {message.ID}")
        file_handler.flush()
        
        # Forward to Control Manager for proper routing
        await forward_gis_data_to_control_manager(gis_data)
        
        # Also broadcast to any connected AllTraq clients
        disconnected_clients = []
        for client_id, websocket in _ALLTRAQ_CLIENTS.items():
            try:
                await websocket.send_json(gis_data)
                logger.debug(f"📤 Sent GIS data to AllTraq client {client_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to send to AllTraq client {client_id}: {str(e)}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            del _ALLTRAQ_CLIENTS[client_id]
            logger.info(f"🧹 Removed disconnected AllTraq client {client_id}")
        
        logger.info(f"✅ v0.1.7: Successfully processed HTTP POST for tag {message.ID} → Control Manager → RealTime")
        file_handler.flush()
        
        return {"status": "success", "message": "GIS data forwarded to Control Manager via HTTP POST"}
        
    except Exception as e:
        logger.error(f"❌ Error processing AllTraq HTTP POST message: {str(e)}")
        file_handler.flush()
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/AllTraqAppAPIInbound")
async def websocket_alltraq_inbound(websocket: WebSocket):
    """
    WebSocket endpoint for AllTraq service connections.
    
    This endpoint handles connections from alltraq_service.py and provides
    BeginStream handshake functionality for AllTraq tag streaming.
    """
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else 0
    client_id = f"{client_host}:{client_port}"
    
    logger.info(f"🔗 AllTraq WebSocket connection attempt from {client_id}")
    file_handler.flush()
    
    try:
        await websocket.accept()
        logger.info(f"✅ AllTraq WebSocket connection accepted for {client_id}")
        file_handler.flush()
        
        # Track client
        _ALLTRAQ_CLIENTS[client_id] = websocket
        
        # Ensure Control Manager connection
        if not _MANAGER_CONNECTED:
            await connect_to_control_manager()
        
        while True:
            try:
                # Receive data from AllTraq service
                data = await websocket.receive_json()
                logger.debug(f"📨 Received from AllTraq client {client_id}: {data}")
                file_handler.flush()
                
                msg_type = data.get("type")
                
                if msg_type == "request":
                    request_type = data.get("request")
                    req_id = data.get("reqid", "")
                    
                    if request_type == "BeginStream":
                        # Send successful response
                        response = {
                            "version": "1.0",
                            "type": "response", 
                            "request": "BgnStrm",
                            "reqid": req_id,
                            "msg": ""  # Empty message indicates success
                        }
                        
                        await websocket.send_json(response)
                        logger.info(f"✅ Sent BeginStream response to AllTraq client {client_id}")
                        file_handler.flush()
                        
                    elif request_type == "EndStream":
                        # Send end response and break
                        response = {
                            "version": "1.0",
                            "type": "response",
                            "request": "EndStrm", 
                            "reqid": req_id,
                            "msg": ""
                        }
                        
                        await websocket.send_json(response)
                        logger.info(f"✅ Sent EndStream response to AllTraq client {client_id}")
                        file_handler.flush()
                        break
                        
                elif msg_type == "GISData":
                    # Forward GIS data to Control Manager
                    logger.info(f"🔄 v0.1.7: Forwarding WebSocket GIS data to Control Manager for tag {data.get('ID')}")
                    file_handler.flush()
                    await forward_gis_data_to_control_manager(data)
                    
                elif msg_type == "HeartBeat":
                    # Echo heartbeat back
                    heartbeat_response = {
                        "type": "HeartBeat",
                        "heartbeat_id": data.get("heartbeat_id"),
                        "ts": data.get("ts"),
                        "source": "AllTraqBridge"
                    }
                    await websocket.send_json(heartbeat_response)
                    logger.debug(f"💓 Heartbeat response sent to AllTraq client {client_id}")
                    file_handler.flush()
                
            except WebSocketDisconnect:
                logger.info(f"🔌 AllTraq client {client_id} disconnected")
                file_handler.flush()
                break
            except Exception as e:
                logger.error(f"❌ Error handling AllTraq client {client_id}: {str(e)}")
                file_handler.flush()
                break
                
    except Exception as e:
        logger.error(f"❌ AllTraq WebSocket error for {client_id}: {str(e)}")
        file_handler.flush()
    finally:
        # Clean up client tracking
        if client_id in _ALLTRAQ_CLIENTS:
            del _ALLTRAQ_CLIENTS[client_id]
            logger.info(f"🧹 Removed AllTraq client {client_id} from tracking")
            file_handler.flush()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18002, log_level="debug")