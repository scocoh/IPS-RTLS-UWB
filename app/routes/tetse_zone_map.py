# Name: tetse_zone_map.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: tetse_zone_map.py
# Version: 0.2.1
# Created: 250616
# Modified: 250617
# Author: ParcoAdmin + AI Assistant
# Purpose: Load zone hierarchy into in-memory cache for TETSE enrichment
# Update: Used get_async_db_pool("maint"), removed asyncio.run; bumped from 0.2.0

import asyncpg
import asyncio
import logging
from database.db import get_async_db_pool

# Global zone cache
_ZONE_HIERARCHY = {}
_LOADED = False

logger = logging.getLogger("TETSE_ZONE_MAP")
logger.setLevel(logging.DEBUG)

async def load_zone_map():
    """
    Load the full zone table into memory as { zone_id: { 'name': ..., 'parent_id': ... } }
    """
    global _ZONE_HIERARCHY, _LOADED
    if _LOADED:
        return
    logger.info("Loading zones from ParcoRTLSMaint...")
    try:
        db_pool = await get_async_db_pool("maint")
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT i_zn, x_nm_zn, i_pnt_zn FROM public.zones")
            _ZONE_HIERARCHY = {
                int(row['i_zn']): {
                    "name": row['x_nm_zn'],
                    "parent_id": int(row['i_pnt_zn']) if row['i_pnt_zn'] is not None else None
                }
                for row in rows
            }
        _LOADED = True
        logger.info(f"Loaded {len(_ZONE_HIERARCHY)} zones into hierarchy cache.")
    except Exception as e:
        logger.error(f"Error loading zones: {str(e)}")
        _ZONE_HIERARCHY = {}
        _LOADED = False

def get_zone_hierarchy():
    """
    Accessor for current cached zone map.
    """
    if not _LOADED:
        asyncio.create_task(load_zone_map())  # Lazy load
    return _ZONE_HIERARCHY.copy()

# For standalone CLI testing
if __name__ == "__main__":
    async def test():
        await load_zone_map()
        for zid, zinfo in get_zone_hierarchy().items():
            print(f"Zone {zid}: {zinfo}")
    
    asyncio.run(test())
