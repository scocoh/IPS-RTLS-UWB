# Name: device_registry.py
# Version: 0.1.2
# Created: 250622
# Modified: 250623
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: Dynamic tag-to-subject mapping registry for TETSE - Fixed schema and initialization
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncio
import logging
import asyncpg
from typing import Dict, Optional
import os

logger = logging.getLogger("DEVICE_REGISTRY")
logger.setLevel(logging.DEBUG)

# Global device registry cache
DEVICE_REGISTRY: Dict[str, str] = {}
MAINT_CONN_STRING = os.getenv("MAINT_CONN_STRING", "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint")

async def load_device_registry() -> Dict[str, str]:
    """
    Load tag-to-subject mappings from database.
    Returns dict mapping tag_id -> subject_id
    """
    global DEVICE_REGISTRY
    
    try:
        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            async with pool.acquire() as conn:
                # FIXED: Updated query to match actual devices table schema
                query = """
                SELECT 
                    x_id_dev as tag_id,
                    COALESCE(x_nm_dev, x_id_dev) as subject_id
                FROM devices 
                WHERE x_id_dev IS NOT NULL
                """
                
                try:
                    rows = await conn.fetch(query)
                    new_registry = {}
                    
                    for row in rows:
                        tag_id = str(row['tag_id'])
                        subject_id = str(row['subject_id'])
                        new_registry[tag_id] = subject_id
                        
                    DEVICE_REGISTRY.clear()
                    DEVICE_REGISTRY.update(new_registry)
                    
                    logger.info(f"Loaded {len(DEVICE_REGISTRY)} device mappings from database")
                    logger.debug(f"Device mappings: {dict(list(DEVICE_REGISTRY.items())[:10])}...")  # Show first 10
                    
                    # Ensure tag 23001 is mapped
                    if "23001" not in DEVICE_REGISTRY:
                        DEVICE_REGISTRY["23001"] = "23001"
                        logger.info("Added fallback mapping: 23001 -> 23001")
                    
                except Exception as db_error:
                    logger.warning(f"Database query failed, using fallback mappings: {str(db_error)}")
                    # Fallback to hardcoded mappings if database fails
                    DEVICE_REGISTRY.clear()
                    DEVICE_REGISTRY.update({
                        "23001": "23001",
                        "23002": "23002", 
                        "23003": "23003"
                    })
                    logger.info(f"Using fallback mappings: {DEVICE_REGISTRY}")
                    
    except Exception as e:
        logger.error(f"Failed to connect to database, using minimal fallback: {str(e)}")
        DEVICE_REGISTRY.clear()
        DEVICE_REGISTRY.update({"23001": "23001"})
        logger.info(f"Emergency fallback: {DEVICE_REGISTRY}")
        
    return DEVICE_REGISTRY

def get_subject_for_tag(tag_id: str) -> Optional[str]:
    """
    Get subject_id for a given tag_id.
    Returns None if tag not found.
    """
    result = DEVICE_REGISTRY.get(str(tag_id))
    logger.debug(f"get_subject_for_tag({tag_id}) -> {result} (registry has {len(DEVICE_REGISTRY)} entries)")
    return result

def get_all_mappings() -> Dict[str, str]:
    """
    Get all current tag-to-subject mappings.
    """
    return DEVICE_REGISTRY.copy()

async def reload_device_registry():
    """
    Reload device registry from database.
    """
    await load_device_registry()
    logger.info("Device registry reloaded")

async def add_device_mapping(tag_id: str, subject_id: str):
    """
    Add or update a device mapping.
    Note: This only updates the in-memory cache.
    For persistent storage, update the database separately.
    """
    DEVICE_REGISTRY[str(tag_id)] = str(subject_id)
    logger.info(f"Added device mapping: {tag_id} -> {subject_id}")

def get_registry_stats() -> dict:
    """
    Get registry statistics for monitoring.
    """
    return {
        "total_devices": len(DEVICE_REGISTRY),
        "sample_mappings": dict(list(DEVICE_REGISTRY.items())[:5]),
        "has_23001": "23001" in DEVICE_REGISTRY,
        "tag_23001_maps_to": DEVICE_REGISTRY.get("23001")
    }

def initialize_registry():
    """
    Synchronously initialize the registry for immediate availability.
    This ensures the registry is ready when the module is imported.
    """
    global DEVICE_REGISTRY
    if not DEVICE_REGISTRY:
        # Emergency initialization for immediate use
        DEVICE_REGISTRY.update({
            "23001": "23001",
            "23002": "23002", 
            "23003": "23003"
        })
        logger.info(f"Emergency registry initialized: {DEVICE_REGISTRY}")
        
        # Schedule async load
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(load_device_registry())
        except RuntimeError:
            # No event loop running, will load later
            pass

# Initialize registry immediately when module is imported
initialize_registry()