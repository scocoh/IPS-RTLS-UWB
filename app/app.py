import asyncpg  # ✅ Import asyncpg to fix "asyncpg is not defined"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
from routes import maps, maps_upload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Parco RTLS API", version="0P.7B.34", docs_url="/docs")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.210.231:3000"],  # Allow your React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(device_router, prefix="/api")
app.include_router(trigger_router, prefix="/api")
app.include_router(zone_router, prefix="/api")
app.include_router(entity_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(text_router, prefix="/api")
app.include_router(input_router)
app.include_router(region_router, prefix="/api")
app.include_router(vertex_router, prefix="/api", tags=["vertices"])
app.include_router(zonebuilder_router, prefix="/zonebuilder", tags=["zonebuilder"])
app.include_router(maps.router, prefix="/maps", tags=["maps"])
app.include_router(maps_upload.router, prefix="/maps", tags=["maps_upload"])

async def get_async_db_pool(db_type: str = "maint"):
    """Creates an asyncpg connection pool with explicit parameters."""
    from config import DB_CONFIGS_ASYNC
    db_config = DB_CONFIGS_ASYNC[db_type]  # ✅ Ensure correct DB config

    try:
        pool = await asyncpg.create_pool(
            database=db_config["database"],  # ✅ Explicitly pass database, not dbname
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

@app.on_event("startup")
async def startup_event():
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
    app.state.sdk_clients = []
    logger.info("Database connections established.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Closing async database connections...")
    if hasattr(app.state, "async_db_pools"):
        for db_type, pool in app.state.async_db_pools.items():
            try:
                await pool.close()
                logger.info(f"Closed pool for {db_type}")
            except Exception as e:
                logger.error(f"Error closing pool for {db_type}: {str(e)}")
    logger.info("All connections closed.")

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
