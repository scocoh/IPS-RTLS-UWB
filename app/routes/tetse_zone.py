# Name: tetse_zone.py
# Version: 0.1.9
# Created: 250615
# Modified: 250618
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend to manage zones and zone types
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/tetse_zone.py
# Version: 0.1.9 - Fixed /api/zone_types/create to accept JSON body, bumped from 0.1.8
# Version: 0.1.8 - Merged zone_types.py to add /api/zone_types/create endpoint, bumped from 0.1.7
# Version: 0.1.7 - Renamed from zone.py to tetse_zone.py
# 
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from fastapi import APIRouter, HTTPException, Response, Depends
from database.db import call_stored_procedure, DatabaseError, execute_raw_query, get_async_db_pool
from models import ZoneRequest
from pydantic import BaseModel
import asyncpg
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(tags=["tetse_zones"])

class ZoneTypeCreate(BaseModel):
    i_typ_zn: int
    x_dsc_zn: str

@router.get("/tetse_zones")
async def get_tetse_zones():
    """
    Fetch all zones from the ParcoRTLSMaint database.
    """
    try:
        query = "SELECT i_zn AS id, x_nm_zn AS name FROM public.zones ORDER BY i_zn;"
        zones = await execute_raw_query("maint", query)
        if not zones:
            logger.warning("No zones found")
            return []
        logger.info(f"Retrieved {len(zones)} zones")
        return zones
    except Exception as e:
        logger.error(f"Error retrieving zones: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving zones: {str(e)}")

@router.get("/zones_for_ai")
async def zones_for_ai():
    """
    Provide full zone metadata for GPT rule parsing context.
    """
    try:
        query = """
            SELECT i_zn AS id, x_nm_zn AS name, i_pnt_zn AS parent, i_typ_zn AS type
            FROM public.zones
            ORDER BY i_zn;
        """
        zones = await execute_raw_query("maint", query)
        if not zones:
            logger.warning("No zones found for AI export")
            return {"zones": []}
        logger.info(f"Returned {len(zones)} zones for AI.")
        return {"zones": zones}
    except Exception as e:
        logger.error(f"Error generating zones_for_ai: {str(e)}")
        return {"zones": [], "error": str(e)}

@router.post("/zone_types/create")
async def create_zone_type(zone_type: ZoneTypeCreate, pool: asyncpg.Pool = Depends(get_async_db_pool)):
    """
    Create a new zone type in tlkzonetypes.
    """
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO tlkzonetypes (i_typ_zn, x_dsc_zn) VALUES ($1, $2)",
                zone_type.i_typ_zn, zone_type.x_dsc_zn
            )
            logger.info(f"Created zone type: i_typ_zn={zone_type.i_typ_zn}, x_dsc_zn={zone_type.x_dsc_zn}")
            return {"message": f"Zone type {zone_type.i_typ_zn} created successfully"}
    except Exception as e:
        logger.error(f"Error creating zone type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")