# Name: websocket_dashboard.py
# Version: 0.1.1
# Created: 250712
# Modified: 250713
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: Python script for ParcoRTLS Dashboard WebSocket server on port 8008 - Real-time dashboard data streaming with customer filtering - Added broadcast endpoint
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Set, Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import asyncpg
import sys
import os

# Import centralized configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "websocket_dashboard.log"),
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

logger.handlers = [console_handler, file_handler]
logger.propagate = False

# Stream configuration
STREAM_TYPE = "Dashboard"
RESOURCE_TYPE = 8008  # Dashboard Stream

# Get centralized configuration
server_host = get_server_host()
db_configs = get_db_configs_sync()
maint_config = db_configs['maint']

# Database connection string
MAINT_CONN_STRING = f"postgresql://{maint_config['user']}:{maint_config['password']}@{server_host}:{maint_config['port']}/{maint_config['database']}"

# Global connection tracking
_DASHBOARD_CLIENTS: Dict[str, Set[WebSocket]] = {}
_CUSTOMER_CONFIGS: Dict[int, Dict[str, Any]] = {}
_DEVICE_CATEGORY_MAPPINGS: Dict[int, Dict[str, Dict[str, Any]]] = {}

# Pydantic model for broadcast messages
class BroadcastMessage(BaseModel):
    message: Dict[str, Any]
    source: str
    timestamp: str

async def load_customer_configurations():
    """Load customer dashboard configurations and device category mappings"""
    global _CUSTOMER_CONFIGS, _DEVICE_CATEGORY_MAPPINGS
    
    try:
        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            async with pool.acquire() as conn:
                # Check if dashboard tables exist first
                table_check = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'dashboard_customer_config'
                    )
                """)
                
                if not table_check:
                    logger.warning("Dashboard tables not found, using default configuration")
                    await create_default_configuration()
                    return
                
                # Load customer configurations
                customer_configs = await conn.fetch("""
                    SELECT customer_id, customer_name, dashboard_title, created_at
                    FROM dashboard_customer_config
                    ORDER BY customer_id
                """)
                
                _CUSTOMER_CONFIGS.clear()
                for config in customer_configs:
                    customer_id = config['customer_id']
                    _CUSTOMER_CONFIGS[customer_id] = {
                        'customer_name': config['customer_name'],
                        'dashboard_title': config['dashboard_title'],
                        'created_at': config['created_at']
                    }
                    logger.info(f"Loaded customer config: {customer_id} - {config['customer_name']}")
                
                # Load device category mappings for each customer
                _DEVICE_CATEGORY_MAPPINGS.clear()
                for customer_id in _CUSTOMER_CONFIGS.keys():
                    category_mappings = await conn.fetch("""
                        SELECT category_name, device_filter, display_name, sort_order
                        FROM dashboard_device_categories
                        WHERE customer_id = $1
                        ORDER BY sort_order
                    """, customer_id)
                    
                    _DEVICE_CATEGORY_MAPPINGS[customer_id] = {}
                    for mapping in category_mappings:
                        _DEVICE_CATEGORY_MAPPINGS[customer_id][mapping['category_name']] = {
                            'device_filter': str(mapping['device_filter']),
                            'display_name': str(mapping['display_name']),
                            'sort_order': int(mapping['sort_order'])
                        }
                    
                    logger.info(f"Loaded {len(category_mappings)} device categories for customer {customer_id}")
                
                logger.info(f"Loaded configurations for {len(_CUSTOMER_CONFIGS)} customers")
                
    except Exception as e:
        logger.error(f"Failed to load customer configurations: {str(e)}")
        await create_default_configuration()

async def create_default_configuration():
    """Create default configuration when database tables don't exist"""
    global _CUSTOMER_CONFIGS, _DEVICE_CATEGORY_MAPPINGS
    
    logger.info("Creating default dashboard configuration")
    
    # Set default configuration
    _CUSTOMER_CONFIGS[1] = {
        'customer_name': 'Default Customer',
        'dashboard_title': 'ParcoRTLS Dashboard',
        'created_at': datetime.now()
    }
    _DEVICE_CATEGORY_MAPPINGS[1] = {
        'vehicles': {'device_filter': 'vehicle', 'display_name': 'Vehicles', 'sort_order': 1},
        'assets': {'device_filter': 'asset', 'display_name': 'Assets', 'sort_order': 2},
        'staff': {'device_filter': 'staff', 'display_name': 'Staff', 'sort_order': 3},
        'equipment': {'device_filter': 'equipment', 'display_name': 'Equipment', 'sort_order': 4}
    }
    
    logger.info("Default configuration created for customer 1")

def get_customer_device_categories(customer_id: int) -> Dict[str, Dict[str, Any]]:
    """Get device categories for a specific customer"""
    return _DEVICE_CATEGORY_MAPPINGS.get(customer_id, {})

def validate_customer_access(customer_id: int) -> bool:
    """Validate if customer_id exists and has valid configuration"""
    return customer_id in _CUSTOMER_CONFIGS

async def filter_message_for_customer(message: Dict[str, Any], customer_id: int) -> Optional[Dict[str, Any]]:
    """Filter and transform message data for specific customer"""
    try:
        # Check if customer has access to this message
        if not validate_customer_access(customer_id):
            logger.warning(f"Invalid customer access: {customer_id}")
            return None
        
        # Apply customer-specific filtering based on device categories
        customer_categories = get_customer_device_categories(customer_id)
        
        # Transform message based on customer configuration
        filtered_message = {
            'timestamp': message.get('timestamp', datetime.now().isoformat()),
            'customer_id': customer_id,
            'message_type': message.get('message_type', 'unknown'),
            'data': message.get('data', {}),
            'device_categories': customer_categories
        }
        
        # Add customer-specific metadata
        if customer_id in _CUSTOMER_CONFIGS:
            filtered_message['customer_info'] = _CUSTOMER_CONFIGS[customer_id]
        
        return filtered_message
        
    except Exception as e:
        logger.error(f"Error filtering message for customer {customer_id}: {str(e)}")
        return None

async def broadcast_to_customer(customer_id: int, message: Dict[str, Any]):
    """Broadcast message to all WebSocket clients for a specific customer"""
    customer_key = str(customer_id)
    
    if customer_key not in _DASHBOARD_CLIENTS:
        return
    
    # Filter message for this customer
    filtered_message = await filter_message_for_customer(message, customer_id)
    if not filtered_message:
        return
    
    # Broadcast to all connected clients for this customer
    disconnected_clients = set()
    for websocket in _DASHBOARD_CLIENTS[customer_key].copy():
        try:
            await websocket.send_text(json.dumps(filtered_message))
            logger.debug(f"Sent message to customer {customer_id} client")
        except Exception as e:
            logger.warning(f"Failed to send message to customer {customer_id} client: {str(e)}")
            disconnected_clients.add(websocket)
    
    # Remove disconnected clients
    for websocket in disconnected_clients:
        _DASHBOARD_CLIENTS[customer_key].discard(websocket)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Dashboard WebSocket server lifespan")
    try:
        # Load customer configurations on startup
        await load_customer_configurations()
        
        # TODO: In Phase 2, connect to RTLSMessageFilter on port 18000
        # For now, we'll integrate with existing WebSocket infrastructure
        
        logger.info("Dashboard WebSocket server initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Dashboard WebSocket lifespan error: {str(e)}")
        raise
    finally:
        logger.info("Dashboard WebSocket server shutdown")

app = FastAPI(lifespan=lifespan)

# CORS configuration
cors_origins = [f"http://{server_host}:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.websocket("/ws/dashboard/{customer_id}")
async def websocket_dashboard_endpoint(websocket: WebSocket, customer_id: int):
    """WebSocket endpoint for dashboard real-time data streaming"""
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else 0
    logger.info(f"Dashboard WebSocket connection attempt for customer {customer_id} from {client_host}:{client_port}")
    
    # Validate customer access
    if not validate_customer_access(customer_id):
        logger.warning(f"Invalid customer ID: {customer_id}")
        await websocket.close(code=1008, reason="Invalid customer ID")
        return
    
    await websocket.accept()
    
    # Add client to customer group
    customer_key = str(customer_id)
    if customer_key not in _DASHBOARD_CLIENTS:
        _DASHBOARD_CLIENTS[customer_key] = set()
    _DASHBOARD_CLIENTS[customer_key].add(websocket)
    
    logger.info(f"Dashboard client connected for customer {customer_id}. Total clients: {len(_DASHBOARD_CLIENTS[customer_key])}")
    
    try:
        # Send initial customer configuration
        initial_message = {
            'type': 'customer_config',
            'customer_id': customer_id,
            'customer_info': _CUSTOMER_CONFIGS.get(customer_id, {}),
            'device_categories': get_customer_device_categories(customer_id),
            'timestamp': datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(initial_message))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (ping/pong, configuration requests, etc.)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                logger.debug(f"Received message from customer {customer_id}: {data}")
                
                # Parse and handle client requests
                try:
                    client_message = json.loads(data)
                    message_type = client_message.get('type', '')
                    
                    if message_type == 'ping':
                        # Respond to ping with pong
                        pong_response = {
                            'type': 'pong',
                            'timestamp': datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(pong_response))
                    
                    elif message_type == 'request_config':
                        # Resend customer configuration
                        await websocket.send_text(json.dumps(initial_message))
                    
                    elif message_type == 'subscribe_categories':
                        # Handle category subscription requests
                        requested_categories = client_message.get('categories', [])
                        logger.info(f"Customer {customer_id} subscribed to categories: {requested_categories}")
                        # TODO: Implement category-specific filtering
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from customer {customer_id}: {data}")
                
            except asyncio.TimeoutError:
                # Send heartbeat if no activity
                heartbeat = {
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat(),
                    'customer_id': customer_id
                }
                await websocket.send_text(json.dumps(heartbeat))
                
    except WebSocketDisconnect:
        logger.info(f"Dashboard client disconnected for customer {customer_id}")
    except Exception as e:
        logger.error(f"Dashboard WebSocket error for customer {customer_id}: {str(e)}")
    finally:
        # Remove client from customer group
        if customer_key in _DASHBOARD_CLIENTS:
            _DASHBOARD_CLIENTS[customer_key].discard(websocket)
            if not _DASHBOARD_CLIENTS[customer_key]:
                del _DASHBOARD_CLIENTS[customer_key]
        logger.info(f"Dashboard client cleanup completed for customer {customer_id}")

@app.post("/broadcast_dashboard_message")
async def broadcast_dashboard_message_endpoint(broadcast_data: BroadcastMessage):
    """
    HTTP endpoint for other services to broadcast messages to dashboard clients
    This is what AllTraq service calls to send data to dashboard
    """
    try:
        logger.info(f"Received broadcast message from {broadcast_data.source}")
        logger.debug(f"Message data: {broadcast_data.message}")
        
        # Transform the message for dashboard broadcasting
        dashboard_message = {
            'type': 'external_data',
            'source': broadcast_data.source,
            'timestamp': broadcast_data.timestamp,
            'message_type': 'broadcast',
            'data': broadcast_data.message
        }
        
        # Broadcast to all customers (you could filter by customer if needed)
        customers_to_notify = set(_CUSTOMER_CONFIGS.keys())
        
        for customer_id in customers_to_notify:
            await broadcast_to_customer(customer_id, dashboard_message)
        
        return {
            "status": "success",
            "message": "Broadcast sent to dashboard clients",
            "customers_notified": len(customers_to_notify),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to broadcast dashboard message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Dashboard WebSocket",
        "port": 8008,
        "timestamp": datetime.now().isoformat(),
        "connected_customers": len(_DASHBOARD_CLIENTS),
        "total_connections": sum(len(clients) for clients in _DASHBOARD_CLIENTS.values())
    }

@app.get("/customers")
async def list_customers():
    """List available customers for dashboard access"""
    return {
        "customers": _CUSTOMER_CONFIGS,
        "device_categories": _DEVICE_CATEGORY_MAPPINGS
    }

# Function to be called by other WebSocket servers to broadcast dashboard data
async def broadcast_dashboard_message(message: Dict[str, Any], target_customers: Optional[Set[int]] = None):
    """
    External function to broadcast messages to dashboard clients
    Called by other WebSocket servers (realtime, control, etc.)
    """
    if not _DASHBOARD_CLIENTS:
        return
    
    customers_to_notify = target_customers or set(_CUSTOMER_CONFIGS.keys())
    
    for customer_id in customers_to_notify:
        await broadcast_to_customer(customer_id, message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)