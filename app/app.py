# Name: app.py
# Version: 0.1.74
# Created: 971201
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & AI Assistant
# Description: Python script for ParcoRTLS backend - Updated to use centralized configuration
# Location: /home/parcoadmin/parco_fastapi/app/app.py
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/app.py
# Version: 0.1.74 - Updated to use centralized configuration instead of hardcoded IP addresses, bumped from 0.1.73
# Version: 0.1.73 - create zone types and device types in TETSE to store and retrieve virtual data
# Version: 0.1.70 - Added in tetse_zone for the Rule Buider
# Version: 0.1.68 - Added prefix=/api to portable_triggers_router, bumped from 0.1.67
# Version: 0.1.67 - add Portable Triggers Endpoint
# Version: 0.1.66 - Integrated openai_trigger_api router into main FastAPI app, bumped from 0.1.65
# Version: 0.1.65 - Removed tetse_main import and run_tetse_server, TETSE server now runs independently, bumped from 0.1.64
# Version: 0.1.64 - Commented out TETSE WebSocket server process to avoid conflict with 06-devsession.sh, bumped from 0.1.63
# Version: 0.1.63 - Added TETSE WebSocket server on port 9000, bumped from 0.1.62
# Version: 0.1.62 - Added route to Events for AI TETSE and RTLS
# Version: 0.1.61 - Added Uvicorn logging to /home/parcoadmin/parco_fastapi/app/logs/server.log, bumped from 0.1.60
# Previous: Confirmed CORSMiddleware import, version bump for clarity
# Previous: Split WebSocket servers into control (port 8001) and real-time (port 8002)
# Previous: Added components router for /api/components endpoint
# Previous: Added debug logging for route registration
# Previous: Restored original, ensured CORS

# 
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import asyncpg
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from logging.handlers import RotatingFileHandler
from database.db import get_async_db_pool
from routes.device import router as device_router
from routes.trigger import router as trigger_router
from routes.portable_triggers import router as portable_triggers_router
from routes.zone import router as zone_router
from routes.tetse_zone import router as tetse_zone_router
from routes.tetse_device import router as tetse_device_router
from routes.tetse_device_registry import router as tetse_device_registry_router  # ← Rename this
from routes.entity import router as entity_router
from routes.history import router as history_router
from routes.text import router as text_router
from routes.input import router as input_router
from routes.region import router as region_router
from routes.vertex import router as vertex_router
from routes.zonebuilder_routes import router as zonebuilder_router
from routes.zoneviewer_routes import router as zoneviewer_router
from routes import maps, maps_upload
from routes.components import router as components_router
from routes.event import router as event_router
from manager.websocket_control import app as control_app
from manager.websocket_realtime import app as realtime_app
from routes.websocket_event import router as websocket_event_router
from routes import openai_trigger_api
from contextlib import asynccontextmanager
from routes.simulator import router as simulator_router
from routes.dashboard import router as dashboard_router
from routes import dashboard_manager
import uvicorn
import multiprocessing
import os

# Import centralized configuration
from config import get_server_host, get_db_configs_sync, initialize_config

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "server.log"),
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

logger.handlers = [console_handler, file_handler]
logger.propagate = False

# Configure Uvicorn logger
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = [console_handler, file_handler]
uvicorn_logger.setLevel(logging.INFO)
uvicorn_logger.propagate = False

logger.info("Starting Parco RTLS backend")
file_handler.flush()

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing async database connections...")
    
    # Initialize centralized configuration
    await initialize_config()
    
    app.state.async_db_pools = {}
    for db_type in ["maint", "data", "hist_r", "hist_p", "hist_o"]:
        try:
            pool = await get_async_db_pool(db_type)
            if pool:
                app.state.async_db_pools[db_type] = pool
                logger.info(f"Successfully initialized pool for {db_type}")
            else:
                logger.warning(f"Database {db_type} is empty or inaccessible, skipping.")
        except Exception as e:
            logger.error(f"Failed to initialize pool for {db_type}: {str(e)}")
    logger.info("Database connections established.")
    
    # Debug: Log all registered routes
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            logger.info(f"Path: {route.path}, Methods: {route.methods}") # type: ignore

    yield  # Application runs here
    
    # Shutdown logic
    logger.info("Closing async database connections...")
    if hasattr(app.state, "async_db_pools"):
        for db_type, pool in app.state.async_db_pools.items():
            try:
                await pool.close()
                logger.info(f"Closed pool for {db_type}")
            except Exception as e:
                logger.error(f"Error closing pool for {db_type}: {str(e)}")
    logger.info("All connections closed.")

# Create the main FastAPI app for HTTP routes
app = FastAPI(
    title="Parco RTLS API",
    version="0P.10B.11",
    docs_url="/docs",
    lifespan=lifespan
)

# Custom middleware to bypass CORS for WebSocket requests
@app.middleware("http")
async def bypass_cors_for_websocket(request: Request, call_next):
    logger.debug(f"Request path: {request.url.path}, Headers: {request.headers}")
    try:
        if "upgrade" in request.headers.get("connection", "").lower() and request.headers.get("upgrade", "").lower() == "websocket":
            logger.info(f"Bypassing CORS for WebSocket request: {request.url.path}")
            response = await call_next(request)
            return response

        response = await call_next(request)
        
        # Use centralized configuration for CORS origin
        server_host = get_server_host()
        cors_origin = f"http://{server_host}:3000"
        
        response.headers["Access-Control-Allow-Origin"] = cors_origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except Exception as e:
        logger.error(f"Middleware error: {str(e)}")
        
        # Use centralized configuration for error response CORS
        server_host = get_server_host()
        cors_origin = f"http://{server_host}:3000"
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
            headers={
                "Access-Control-Allow-Origin": cors_origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

# Configure CORS for HTTP requests using centralized configuration
server_host = get_server_host()
cors_origins = [
    f"http://{server_host}:3000",  # Allow your React development server
    f"http://{server_host}:8000"   # Allow HTTP requests from the same host
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for HTTP routes
app.include_router(device_router, prefix="/api")
app.include_router(trigger_router, prefix="/api")
app.include_router(zone_router, prefix="/api")
app.include_router(tetse_zone_router, prefix="/api")
app.include_router(tetse_device_router, prefix="/api", tags=["tetse_devices"])
app.include_router(tetse_device_registry_router)  # ← Use new name, already has prefix in router
app.include_router(entity_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(text_router, prefix="/api")
app.include_router(input_router, prefix="/api")
app.include_router(region_router, prefix="/api")
app.include_router(vertex_router, prefix="/api", tags=["vertices"])
app.include_router(zonebuilder_router, prefix="/zonebuilder", tags=["zonebuilder"])
app.include_router(zoneviewer_router, prefix="/zoneviewer", tags=["zoneviewer"])
app.include_router(maps.router, prefix="/maps", tags=["maps"])
app.include_router(maps_upload.router, prefix="/maps", tags=["maps_upload"])
app.include_router(components_router, prefix="/api", tags=["components"])
app.include_router(event_router, prefix="/api", tags=["event"])
app.include_router(portable_triggers_router, prefix="/api")
app.include_router(websocket_event_router)
app.include_router(openai_trigger_api.router, prefix="/api/openai")
app.include_router(simulator_router)
app.include_router(dashboard_router)
app.include_router(dashboard_manager.router, prefix="/api")

async def get_async_db_pool(db_type: str = "maint"):
    """Creates an asyncpg connection pool with explicit parameters."""
    from config import DB_CONFIGS_ASYNC
    db_config = DB_CONFIGS_ASYNC[db_type]

    try:
        pool = await asyncpg.create_pool(
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"],
            min_size=2,
            max_size=20,
            timeout=30,
            command_timeout=60
        )
        async with pool.acquire() as connection:
            await connection.execute("SELECT 1")
        logger.info(f"✅ Database pool created for {db_type}")
        return pool

    except Exception as e:
        logger.error(f"❌ Error creating async database pool for {db_type}: {e}")
        return None

@app.get("/", tags=["root"])
def root():
    return {"message": "FastAPI is running!"}

def run_control_server():
    """Run the control WebSocket server on port 8001."""
    logger.info("Starting Uvicorn for control WebSocket on port 8001")
    uvicorn.run(
        "manager.websocket_control:app",
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

def run_realtime_server():
    """Run the real-time WebSocket server on port 8002."""
    logger.info("Starting Uvicorn for real-time WebSocket on port 8002")
    uvicorn.run(
        "manager.websocket_realtime:app",
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )

if __name__ == "__main__":
    # Start the main app (HTTP routes) on port 8000
    logger.info("Starting main FastAPI app on port 8000...")
    main_process = multiprocessing.Process(target=uvicorn.run, args=(app,), kwargs={"host": "0.0.0.0", "port": 8000, "log_level": "debug", "logger": uvicorn_logger})
    main_process.start()

    # Start the control WebSocket server on port 8001
    logger.info("Starting control WebSocket server on port 8001...")
    control_process = multiprocessing.Process(target=run_control_server)
    control_process.start()

    # Start the real-time WebSocket server on port 8002
    logger.info("Starting real-time WebSocket server on port 8002...")
    realtime_process = multiprocessing.Process(target=run_realtime_server)
    realtime_process.start()

    # Wait for all processes to complete
    main_process.join()
    control_process.join()
    realtime_process.join()