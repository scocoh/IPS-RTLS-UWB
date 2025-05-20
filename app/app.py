# Name: app.py
# Version: 0.1.60
# Created: 971201
# Modified: 250518
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/app.py
# Version: 0.1.60 - Confirmed CORSMiddleware import, version bump for clarity
# Previous: 0.1.59 - Split WebSocket servers into control (port 8001) and real-time (port 8002)
# Previous: 0.1.58 - Added components router for /api/components endpoint
# Previous: 0P.10B.07 - Added debug logging for route registration
# Previous: 0P.10B.06 - Restored original, ensured CORS

import asyncpg
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware  # Ensure this import is correct
from fastapi.responses import JSONResponse
import logging
from database.db import get_async_db_pool
from routes.device import router as device_router
from routes.trigger import router as trigger_router
from routes.zone import router as zone_router
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
from manager.websocket_control import app as control_app
from manager.websocket_realtime import app as realtime_app
from contextlib import asynccontextmanager
import uvicorn
import multiprocessing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing async database connections...")
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
            logger.info(f"Path: {route.path}, Methods: {route.methods}")

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
    version="0P.10B.10",
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
        response.headers["Access-Control-Allow-Origin"] = "http://192.168.210.226:3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except Exception as e:
        logger.error(f"Middleware error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
            headers={
                "Access-Control-Allow-Origin": "http://192.168.210.226:3000",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

# Configure CORS for HTTP requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.210.226:3000",  # Allow your React development server
        "http://192.168.210.226:8000"   # Allow HTTP requests from the same host
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for HTTP routes
app.include_router(device_router, prefix="/api")
app.include_router(trigger_router, prefix="/api")
app.include_router(zone_router, prefix="/api")
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
    uvicorn.run(
        "manager.websocket_control:app",
        host="0.0.0.0",
        port=8001,
        log_level="debug"
    )

def run_realtime_server():
    """Run the real-time WebSocket server on port 8002."""
    uvicorn.run(
        "manager.websocket_realtime:app",
        host="0.0.0.0",
        port=8002,
        log_level="debug"
    )

if __name__ == "__main__":
    # Start the main app (HTTP routes) on port 8000
    logger.info("Starting main FastAPI app on port 8000...")
    main_process = multiprocessing.Process(target=uvicorn.run, args=(app,), kwargs={"host": "0.0.0.0", "port": 8000, "log_level": "debug"})
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