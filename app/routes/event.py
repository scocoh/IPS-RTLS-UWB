# Name: event.py
# Version: 0.1.11
# Created: 250525
# Modified: 250528
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Event Engine for Backend (TETSE - Temporal Entity Trigger State Engine)
# Location: /home/parcoadmin/parco_fastapi/app/routes/event.py
# Role: Backend
# Status: Active
# Dependent: TRUE
#
# Version: 0.1.11 - Added defaults for reason_id, value, unit in /event, bumped from 0.1.10
# Version: 0.1.10 - Added debug logging for TETSE_MANAGER instance in broadcast, bumped from 0.1.9
# Version: 0.1.9 - Use TETSE_MANAGER.broadcast_event_instance() to fix broadcasting, bumped from 0.1.8
# Version: 0.1.8 - Reverted to TETSE_MANAGER.broadcast_event() to align with client registration, bumped from 0.1.7
# Version: 0.1.7 - Reverted to Manager.broadcast_event() after client registration fix, bumped from 0.1.6
# Version: 0.1.6 - Use TETSE_MANAGER for broadcasting to fix subscriber issue, bumped from 0.1.5
# Version: 0.1.5 - (Prior version assumed based on user input)

from manager.websocket_tetse_event import TETSE_MANAGER
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List
from database.db import execute_raw_query
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["event"])

class EventIn(BaseModel):
    entity_id: str
    event_type_id: int
    reason_id: Optional[int] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    ts: Optional[datetime] = None

class EventOut(EventIn):
    id: int

@router.post("/event", response_model=EventOut)
async def log_event(event: EventIn):
    """
    Insert a new event into the event_log table.
    This endpoint supports symbolic and financial event tracking
    as part of the TETSE (Temporal Entity Trigger State Engine) layer.
    """
    try:
        ts = event.ts or datetime.now(timezone.utc)
        reason_id = event.reason_id or 4  # Analyst override
        value = event.value if event.value is not None else 1.0
        unit = event.unit or "percent"
        query = """
            INSERT INTO event_log (entity_id, event_type_id, reason_id, value, unit, ts)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id;
        """
        result = await execute_raw_query("data", query,
                                         event.entity_id, event.event_type_id,
                                         reason_id, value, unit, ts)
        if result and isinstance(result, list) and result:
            event_data = event.model_dump()
            event_data["id"] = result[0]["id"]
            event_data.update({"reason_id": reason_id, "value": value, "unit": unit})
            logger.info(f"Event logged with ID {event_data['id']}")
            logger.debug(f"Before broadcast, using TETSE_MANAGER instance: {id(TETSE_MANAGER)}")
            await TETSE_MANAGER.broadcast_event_instance(event.entity_id, event_data)
            return EventOut(**event_data)
        raise HTTPException(status_code=500, detail="Insert failed")
    except Exception as e:
        logger.error(f"Failed to log event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/event_by_entity/{entity_id}", response_model=List[EventOut])
async def get_event_by_entity(entity_id: str):
    """
    Retrieve all event(s) associated with a specific entity_id, ordered by most recent timestamp.
    """
    try:
        query = """
            SELECT id, entity_id, event_type_id, reason_id, value, unit, ts
            FROM event_log
            WHERE entity_id = $1
            ORDER BY ts DESC;
        """
        results = await execute_raw_query("data", query, entity_id)
        return [EventOut(**row) for row in results] if results else []
    except Exception as e:
        logger.error(f"Failed to fetch event(s) for entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve event(s).")