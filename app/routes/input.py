"""
routes/input.py
Version: 0.1.8 (Removed autogeneration, manual device_id input)
Input screen endpoint for ParcoRTLS FastAPI application.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.db import call_stored_procedure
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/input", response_class=HTMLResponse)
async def input_screen(request: Request):
    """Serve an input screen with default data from the database."""
    try:
        devices = await call_stored_procedure("maint", "usp_device_select_all")
        entities = await call_stored_procedure("maint", "usp_entity_all")
        reasons = await call_stored_procedure("maint", "usp_assmt_reason_list")
        triggers = await call_stored_procedure("maint", "usp_trigger_list")
        device_types = await call_stored_procedure("maint", "usp_device_type_list")

        default_device = devices[0]["x_id_dev"] if devices else "DEV001"
        default_entity = entities[0]["x_id_ent"] if entities else "ENT101"
        default_reason = reasons[0]["i_rsn"] if reasons else 1
        default_trigger = triggers[0]["x_nm_trg"] if triggers else "test_trigger"
        default_device_type = device_types[0]["i_typ_dev"] if device_types else 1

        return templates.TemplateResponse(
            "input_screen.html",
            {
                "request": request,
                "devices": devices,
                "entities": entities,
                "reasons": reasons,
                "triggers": triggers,
                "device_types": device_types,
                "default_device": default_device,
                "default_entity": default_entity,
                "default_reason": default_reason,
                "default_trigger": default_trigger,
                "default_device_type": default_device_type,
            }
        )
    except Exception as e:
        logger.error(f"Error loading input screen: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load input screen")