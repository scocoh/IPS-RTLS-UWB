# Name: device_registry.py
# Version: 0.1.1
# Created: 971201
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend - Updated to use database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Device Registry Module for ParcoRTLS
Handles tag-to-subject mappings from the devices table
Updated to use database-driven configuration instead of hardcoded IP addresses
"""

import asyncpg
import logging
import sys
import os
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config_helper import config_helper

logger = logging.getLogger(__name__)

# Global device registry cache
DEVICE_REGISTRY: Dict[str, str] = {}

# Cache for connection string
_cached_conn_string = None

def get_maint_connection_string() -> str:
    """Get maintenance database connection string from config helper"""
    global _cached_conn_string
    if _cached_conn_string is None:
        _cached_conn_string = config_helper.get_connection_string("ParcoRTLSMaint")
        host = config_helper.get_database_configs()['maint']['host']
        logger.info(f"Maintenance database connection string configured for host: {host}")
    return _cached_conn_string

async def load_device_registry() -> Dict[str, str]:
    """
    Load tag-to-subject mappings from database.
    Returns dict mapping tag_id -> subject_id
    """
    global DEVICE_REGISTRY
    
    try:
        conn_string = get_maint_connection_string()
        async with asyncpg.create_pool(conn_string) as pool:
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

def refresh_device_registry():
    """
    Clear the device registry cache to force reload from database.
    Call this after updating device mappings in the database.
    """
    global DEVICE_REGISTRY, _cached_conn_string
    DEVICE_REGISTRY.clear()
    _cached_conn_string = None
    logger.info("Device registry cache cleared - will reload on next access")

def add_device_mapping(tag_id: str, subject_id: str):
    """
    Add a device mapping to the local cache.
    Note: This only updates the cache, not the database.
    """
    DEVICE_REGISTRY[str(tag_id)] = str(subject_id)
    logger.info(f"Added device mapping to cache: {tag_id} -> {subject_id}")

def remove_device_mapping(tag_id: str) -> bool:
    """
    Remove a device mapping from the local cache.
    Note: This only updates the cache, not the database.
    Returns True if mapping was removed, False if not found.
    """
    tag_id = str(tag_id)
    if tag_id in DEVICE_REGISTRY:
        del DEVICE_REGISTRY[tag_id]
        logger.info(f"Removed device mapping from cache: {tag_id}")
        return True
    return False

def get_registry_stats() -> Dict[str, any]: # type: ignore
    """
    Get statistics about the current device registry.
    """
    return {
        "total_mappings": len(DEVICE_REGISTRY),
        "sample_mappings": dict(list(DEVICE_REGISTRY.items())[:5]),  # First 5 mappings
        "has_fallback_tag": "23001" in DEVICE_REGISTRY
    }