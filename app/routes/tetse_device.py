# Name: tetse_device.py
# Version: 0.1.3
# Created: 250617
# Modified: 250617
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Python script for TETSE backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE
# Update: Fixed async db_pool dependency, enhanced logging; bumped from 0.1.2

from fastapi import APIRouter, Depends, Form
from database.db import call_stored_procedure, DatabaseError, execute_raw_query, get_async_db_pool
from models import DeviceAddRequest, DeviceStateRequest, DeviceTypeRequest, DeviceEndDateRequest, AssignDeviceRequest, AssignDeviceDeleteRequest, AssignDeviceEditRequest, AssignDeviceEndRequest
from datetime import datetime
import logging
import asyncpg
import traceback

logger = logging.getLogger(__name__)
router = APIRouter(tags=["tetse_devices"])

@router.get("/devices_for_ai")
async def get_devices_for_ai(db_pool: asyncpg.Pool = Depends(get_async_db_pool)):
    try:
        async with db_pool.acquire() as conn:
            logger.debug("Executing devices query for AI")
            devices = await conn.fetch("""
                SELECT x_id_dev, x_nm_dev
                FROM devices
                WHERE i_typ_dev IN (1, 2, 4) AND d_srv_end IS NULL
                ORDER BY x_id_dev
            """)
            result = {"devices": [{"id": row["x_id_dev"], "name": row["x_nm_dev"]} for row in devices]}
            logger.debug(f"Fetched {len(result['devices'])} devices: {result}")
            return result
    except Exception as e:
        logger.error(f"Failed to fetch devices for AI: {str(e)}\n{traceback.format_exc()}")
        return {"devices": []}  # Fallback to empty list
