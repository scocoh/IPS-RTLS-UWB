# /home/parcoadmin/parco_fastapi/app/app.py
# Version: 0P.10B.06 - Restored original, ensured CORS
import asyncpg
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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
from manager.websocket import app as manager_app
from contextlib import asynccontextmanager

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

# Create the FastAPI app with the lifespan handler
app = FastAPI(
    title="Parco RTLS API",
    version="0P.10B.06",  # Updated to match file version
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

# Include routers
app.include_router(device_router, prefix="/api")
app.include_router(trigger_router, prefix="/api")
app.include_router(zone_router, prefix="/api")
app.include_router(entity_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(text_router, prefix="/api")
app.include_router(input_router, prefix="/api")  # Added prefix for consistency
app.include_router(region_router, prefix="/api")
app.include_router(vertex_router, prefix="/api", tags=["vertices"])
app.include_router(zonebuilder_router, prefix="/zonebuilder", tags=["zonebuilder"])
app.include_router(zoneviewer_router, prefix="/zoneviewer", tags=["zoneviewer"])
app.include_router(maps.router, prefix="/maps", tags=["maps"])
app.include_router(maps_upload.router, prefix="/maps", tags=["maps_upload"])
app.mount("/manager", manager_app)  # Mount the manager app

async def get_async_db_pool(db_type: str = "maint"):
    """Creates an asyncpg connection pool with explicit parameters."""
    from config import DB_CONFIGS_ASYNC
    db_config = DB_CONFIGS_ASYNC[db_type]  # ✅ Ensure correct DB config

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
            await connection.execute("SELECT 1")  # ✅ Test query inside pool
        logger.info(f"✅ Database pool created for {db_type}")
        return pool

    except Exception as e:
        logger.error(f"❌ Error creating async database pool for {db_type}: {e}")
        return None

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)