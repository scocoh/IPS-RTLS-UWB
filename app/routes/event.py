# Name: event.py
# Version: 0.1.2
# Created: 250525
# Modified: 250525
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Event Engine for Backend (TETSE - Temporal Entity Trigger State Engine)
# Location: /home/parcoadmin/parco_fastapi/app/routes/event.py
# Role: Backend
# Status: Active
# Dependent: TRUE

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
        query = """
            INSERT INTO event_log (entity_id, event_type_id, reason_id, value, unit, ts)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id;
        """
        result = await execute_raw_query("maint", query,
                                         event.entity_id, event.event_type_id,
                                         event.reason_id, event.value, event.unit, ts)

        if result and isinstance(result, list) and result:
            logger.info(f"Event logged with ID {result[0]['id']}")
            return EventOut(id=result[0]["id"], **event.model_dump())
        raise HTTPException(status_code=500, detail="Insert failed")
    except Exception as e:
        logger.error(f"Failed to log event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
