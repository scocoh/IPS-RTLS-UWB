"""
routes/history.py
Historical data and positioning endpoints for ParcoRTLS FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError
from models import PositionRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/get_recent_device_positions/{device_id}")
async def get_recent_device_positions(device_id: str):
    try:
        result = await call_stored_procedure("hist_r", "usp_location_by_id", device_id)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No recent positions found")
    except DatabaseError as e:
        logger.error(f"Database error fetching positions: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.post("/insert_position")
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

@router.get("/get_history_by_device/{device_id}")
async def get_history_by_device(device_id: str, start_date: datetime, end_date: datetime):
    try:
        result = await call_stored_procedure("hist_r", "usp_history_by_id", device_id, start_date, end_date)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No history found for device")
    except DatabaseError as e:
        logger.error(f"Database error fetching history: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)