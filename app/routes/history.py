# Name: history.py
# Version: 0.1.1
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Version 0.1.1 Converted to external descriptions using load_description()
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
routes/history.py
Historical data and positioning endpoints for ParcoRTLS FastAPI application.
// # VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/history.py 0P.10B.02
// # Changelog:
// # - 0P.10B.02 (2025-04-26): Enhanced endpoint docstrings with detailed descriptions, parameters, return values, examples, use cases, and error handling.
// # - 0P.10B.01 (2025-03-16): Initial implementation of history routes.
// #
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError
from models import PositionRequest
from datetime import datetime
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "history" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter(tags=["history"])

@router.get(
    "/get_recent_device_positions/{device_id}",
    summary="Retrieve recent position data for a specific device in the ParcoRTLS system",
    description=load_description("get_recent_device_positions"),
    tags=["triggers"]
)
async def get_recent_device_positions(device_id: str):
    try:
        result = await call_stored_procedure("hist_r", "usp_location_by_id", device_id)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No recent positions found")
    except DatabaseError as e:
        logger.error(f"Database error fetching positions: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.post(
    "/insert_position",
    summary="Insert a new position record for a device in the ParcoRTLS system",
    description=load_description("insert_position"),
    tags=["triggers"]
)
async def insert_position(device_id: str = Form(...), x: float = Form(...), y: float = Form(...), z: float = Form(...)):
    start_time = datetime.now()
    end_time = start_time
    request = PositionRequest(device_id=device_id, start_time=start_time, end_time=end_time, x=x, y=y, z=z)
    try:
        device = await call_stored_procedure("maint", "usp_device_select_by_id", request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found in ParcoRTLSMaint")
        result = await call_stored_procedure(
            "hist_r", "usp_position_insert",
            request.device_id, request.start_time, request.end_time, request.x, request.y, request.z
        )
        if result and isinstance(result, (int, str)):
            return {"message": "Position inserted successfully"}
        raise HTTPException(status_code=500, detail="Failed to insert position")
    except DatabaseError as e:
        logger.error(f"Database error inserting position: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error inserting position: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_history_by_device/{device_id}",
    summary="Retrieve historical position data for a device within a specified time range in the ParcoRTLS system",
    description=load_description("get_history_by_device"),
    tags=["triggers"]
)
async def get_history_by_device(device_id: str, start_date: datetime, end_date: datetime):
    try:
        result = await call_stored_procedure("hist_r", "usp_history_by_id", device_id, start_date, end_date)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No history found for device")
    except DatabaseError as e:
        logger.error(f"Database error fetching history: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)