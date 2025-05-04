# Name: text.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
routes/text.py
Text data storage endpoints for ParcoRTLS FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError
from models import TextEventRequest
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["text"])

@router.post("/log_text_event")
async def log_text_event(device_id: str = Form(...), event_data: str = Form(...)):
    timestamp = datetime.now()
    request = TextEventRequest(device_id=device_id, event_data=event_data, timestamp=timestamp)
    try:
        device = await call_stored_procedure("maint", "usp_device_select_by_id", request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found in ParcoRTLSMaint")
        async with asyncio.timeout(30):
            result = await call_stored_procedure(
                "data", "usp_textdata_add",
                request.device_id, request.event_data, request.timestamp
            )
        if result and isinstance(result, (int, str)):
            return {"message": "Text event logged successfully"}
        raise HTTPException(status_code=500, detail="Failed to log text event")
    except asyncio.TimeoutError:
        logger.error("Timeout occurred while logging text event for ParcoRTLSData")
        raise HTTPException(status_code=504, detail="Request timed out connecting to ParcoRTLSData")
    except DatabaseError as e:
        logger.error(f"Database error logging text event: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error logging text event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_text_events_by_device/{device_id}")
async def get_text_events_by_device(device_id: str):
    try:
        async with asyncio.timeout(30):
            result = await call_stored_procedure("data", "usp_textdata_all_by_device", device_id)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No text events found for device")
    except asyncio.TimeoutError:
        logger.error("Timeout occurred while fetching text events for ParcoRTLSData")
        raise HTTPException(status_code=504, detail="Request timed out connecting to ParcoRTLSData")
    except DatabaseError as e:
        logger.error(f"Database error fetching text events: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)