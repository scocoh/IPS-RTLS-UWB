# Name: tetse_zone_utils.py
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

# File: tetse_zone_utils.py
# Version: 0.1.1
# Created: 250615
# Modified: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: TETSE helper utilities for zone hierarchy
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Status: Active

# V=0.1.1 Phase 3B Mini Refactor - Full production-safe version

from fastapi import APIRouter, HTTPException
from database.db import execute_raw_query
import logging
import asyncpg
import os

logger = logging.getLogger(__name__)
router = APIRouter(tags=["tetse_zone_utils"])

# Standalone database connection string for CLI testing (ParcoRTLSMaint)
MAINT_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint"

# ✅ Standard FastAPI route function (unchanged)
@router.get("/get_zone_descendants/{zone_id}")
async def get_zone_descendants(zone_id: int):
    """
    Return full list of descendant zones for a given parent zone.
    """
    try:
        query = """
            WITH RECURSIVE zone_tree AS (
                SELECT i_zn FROM public.zones WHERE i_zn = $1
                UNION ALL
                SELECT z.i_zn FROM public.zones z
                JOIN zone_tree t ON z.i_pnt_zn = t.i_zn
            )
            SELECT i_zn FROM zone_tree WHERE i_zn != $1;
        """
        result = await execute_raw_query("maint", query, zone_id)
        descendant_ids = [row["i_zn"] for row in result] if result else []
        logger.info(f"Found {len(descendant_ids)} descendants for zone_id={zone_id}")
        return {
            "parent_zone_id": zone_id,
            "descendants": descendant_ids
        }
    except Exception as e:
        logger.error(f"Error fetching descendants for zone {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching descendants: {str(e)}")

# ✅ CLI-safe version for standalone test harness usage
async def get_zone_descendants_raw(zone_id: int):
    """
    Standalone CLI-safe version of get_zone_descendants() without FastAPI state.
    This version can be used inside standalone test harnesses.
    """
    try:
        query = """
            WITH RECURSIVE zone_tree AS (
                SELECT i_zn FROM public.zones WHERE i_zn = $1
                UNION ALL
                SELECT z.i_zn FROM public.zones z
                JOIN zone_tree t ON z.i_pnt_zn = t.i_zn
            )
            SELECT i_zn FROM zone_tree WHERE i_zn != $1;
        """

        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            async with pool.acquire() as conn:
                result = await conn.fetch(query, zone_id)

        descendant_ids = [row["i_zn"] for row in result] if result else []
        logger.info(f"[RAW] Found {len(descendant_ids)} descendants for zone_id={zone_id}")
        return {
            "parent_zone_id": zone_id,
            "descendants": descendant_ids
        }

    except Exception as e:
        logger.error(f"Error (RAW) fetching descendants for zone {zone_id}: {str(e)}")
        raise
