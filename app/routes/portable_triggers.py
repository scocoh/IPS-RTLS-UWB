# /home/parcoadmin/parco_fastapi/app/routes/portable_triggers.py
# Name: portable_triggers.py
# Version: 0.1.5
# Created: 250607
# Modified: 250711
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: FastAPI routes for managing portable triggers in ParcoRTLS
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: FastAPI
# Status: Active
# Dependent: TRUE
#
# Version 0.1.5 - Added edit endpoints for portable trigger name, radius, and zone, bumped from 0.1.4
# Version 0.1.4 - Simplified /api/reload_triggers endpoint, bumped from 0.1.3
# Version 0.1.3 - Added /api/reload_triggers endpoint, bumped from 0.1.2
# Version 0.1.2 - Removed prefix=/api from router to fix 404, bumped from 0.1.1
# Version 0.1.1 - Removed duplicate TriggerAddRequest, added debug logging, bumped from 0.1.0
# Version 0.1.0 - Initial version with /api/add_portable_trigger endpoint
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from fastapi import APIRouter, HTTPException
from models import TriggerAddRequest
from pydantic import BaseModel
import asyncpg
import logging
from database.db import execute_raw_query

logger = logging.getLogger(__name__)
router = APIRouter(tags=["portable_triggers"])
logger.info("Portable triggers router initialized")

# Pydantic models for edit requests
class TriggerNameEditRequest(BaseModel):
    name: str

class TriggerRadiusEditRequest(BaseModel):
    radius_ft: float

class TriggerZoneEditRequest(BaseModel):
    zone_id: int

@router.post("/add_portable_trigger")
async def add_portable_trigger(request: TriggerAddRequest):
    """
    Add a portable trigger to the ParcoRTLS system.

    This endpoint creates a portable trigger with specified properties, storing it directly in the triggers table without associating a region or vertices. It is designed for triggers that follow a tag (e.g., SIM3) and use a radius-based boundary.

    Args:
        request (TriggerAddRequest): A Pydantic model containing:
            - name (str): Trigger name (required, unique).
            - direction (int): Trigger direction ID (required, references tlktrigdirections).
            - ignore (bool): Whether to ignore the trigger (required).
            - zone_id (int, optional): Zone ID.
            - is_portable (bool): Must be true.
            - assigned_tag_id (str): Tag ID the trigger follows (required).
            - radius_ft (float): Radius in feet (required, > 0).
            - z_min (float): Minimum z-coordinate in feet (required).
            - z_max (float): Maximum z-coordinate in feet (required, > z_min).
            - vertices (list[dict], optional): Must be empty.

    Returns:
        dict: JSON response containing:
            - message (str): Success message.
            - trigger_id (int): ID of the created trigger.

    Raises:
        HTTPException:
            - 400: If validation fails (e.g., missing fields, invalid values).
            - 500: For database or unexpected errors.

    Example:
        ```bash
        curl -X POST http://192.168.210.226:8000/api/add_portable_trigger \
             -H "Content-Type: application/json" \
             -d '{"name":"250607SIM3PTTEST1","direction":4,"ignore":false,"zone_id":417,"is_portable":true,"assigned_tag_id":"SIM3","radius_ft":1.5,"z_min":0,"z_max":10,"vertices":[]}'
        ```
        Response:
        ```json
        {
            "message": "Portable trigger added successfully",
            "trigger_id": 143
        }
        ```

    Use Case:
        Create portable triggers for tags (e.g., SIM3) to track dynamic areas, such as a safety zone around a moving asset in the ParcoRTLS system.

    Hint:
        - Ensure the direction ID exists in the tlktrigdirections table (maint.tlktrigdirections).
        - If zone_id is provided, verify it exists in the zones table (maint.zones, i_zn).
        - Use with simulator.py (e.g., mode 4, SIM3, zone 417) to test trigger events.
        - The trigger name must be unique (enforced by unique_trigger_name constraint in triggers table).
    """
    logger.debug(f"Received add_portable_trigger request: {request.dict()}")
    try:
        if not request.is_portable:
            raise HTTPException(status_code=400, detail="is_portable must be true")
        if not request.assigned_tag_id:
            raise HTTPException(status_code=400, detail="assigned_tag_id required")
        if not request.radius_ft or request.radius_ft <= 0:
            raise HTTPException(status_code=400, detail="radius_ft must be positive")
        if request.z_min is None or request.z_max is None or request.z_min >= request.z_max:
            raise HTTPException(status_code=400, detail="z_min must be less than z_max")
        if request.vertices:
            raise HTTPException(status_code=400, detail="vertices not allowed")
        
        # Validate direction
        dir_query = "SELECT COUNT(*) FROM tlktrigdirections WHERE i_dir = $1"
        dir_count = await execute_raw_query("maint", dir_query, request.direction)
        if dir_count[0]["count"] == 0:
            raise HTTPException(status_code=400, detail=f"Invalid direction_id: {request.direction}")

        # Validate zone
        if request.zone_id:
            zone_query = "SELECT COUNT(*) FROM zones WHERE i_zn = $1"
            zone_count = await execute_raw_query("maint", zone_query, request.zone_id)
            if zone_count[0]["count"] == 0:
                raise HTTPException(status_code=400, detail=f"Invalid zone_id: {request.zone_id}")

        query = """
            INSERT INTO triggers (x_nm_trg, i_dir, f_ign, is_portable, assigned_tag_id, radius_ft, z_min, z_max, i_zn)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING i_trg
        """
        result = await execute_raw_query(
            "maint", query, request.name, request.direction, request.ignore, True,
            request.assigned_tag_id, request.radius_ft, request.z_min, request.z_max, request.zone_id
        )
        trigger_id = result[0]["i_trg"]
        logger.info(f"Portable trigger {trigger_id} created: {request.name}")
        return {"message": "Portable trigger added successfully", "trigger_id": trigger_id}
    except asyncpg.exceptions.UniqueViolationError:
        logger.error(f"Trigger name '{request.name}' already exists")
        raise HTTPException(status_code=400, detail=f"Trigger name '{request.name}' already exists")
    except Exception as e:
        logger.error(f"Error adding portable trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/edit_trigger_name/{trigger_id}")
async def edit_trigger_name(trigger_id: int, request: TriggerNameEditRequest):
    """
    Edit the name of a portable trigger.

    This endpoint updates the name of an existing portable trigger in the ParcoRTLS system.

    Args:
        trigger_id (int): The ID of the trigger to edit (path parameter, required).
        request (TriggerNameEditRequest): A Pydantic model containing:
            - name (str): New trigger name (required, unique).

    Returns:
        dict: JSON response containing:
            - message (str): Success message.

    Raises:
        HTTPException:
            - 400: If validation fails (e.g., name already exists, trigger not portable).
            - 404: If trigger not found.
            - 500: For database or unexpected errors.

    Example:
        ```bash
        curl -X PUT http://192.168.210.226:8000/api/edit_trigger_name/143 \
             -H "Content-Type: application/json" \
             -d '{"name":"NewTriggerName"}'
        ```
        Response:
        ```json
        {
            "message": "Trigger name updated successfully"
        }
        ```

    Use Case:
        Rename portable triggers for better identification or organization.

    Hint:
        - Only works on portable triggers (is_portable = true).
        - Trigger name must be unique across all triggers.
    """
    logger.debug(f"Received edit_trigger_name request for trigger {trigger_id}: {request.dict()}")
    try:
        # Check if trigger exists and is portable
        check_query = "SELECT is_portable FROM triggers WHERE i_trg = $1"
        trigger_check = await execute_raw_query("maint", check_query, trigger_id)
        if not trigger_check:
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
        if not trigger_check[0]["is_portable"]:
            raise HTTPException(status_code=400, detail="Only portable triggers can be edited")

        # Update trigger name
        update_query = "UPDATE triggers SET x_nm_trg = $1 WHERE i_trg = $2"
        await execute_raw_query("maint", update_query, request.name, trigger_id)
        
        logger.info(f"Trigger {trigger_id} name updated to: {request.name}")
        return {"message": "Trigger name updated successfully"}
    except asyncpg.exceptions.UniqueViolationError:
        logger.error(f"Trigger name '{request.name}' already exists")
        raise HTTPException(status_code=400, detail=f"Trigger name '{request.name}' already exists")
    except Exception as e:
        logger.error(f"Error updating trigger name: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/edit_trigger_radius/{trigger_id}")
async def edit_trigger_radius(trigger_id: int, request: TriggerRadiusEditRequest):
    """
    Edit the radius of a portable trigger.

    This endpoint updates the radius of an existing portable trigger in the ParcoRTLS system.

    Args:
        trigger_id (int): The ID of the trigger to edit (path parameter, required).
        request (TriggerRadiusEditRequest): A Pydantic model containing:
            - radius_ft (float): New radius in feet (required, > 0).

    Returns:
        dict: JSON response containing:
            - message (str): Success message.

    Raises:
        HTTPException:
            - 400: If validation fails (e.g., invalid radius, trigger not portable).
            - 404: If trigger not found.
            - 500: For database or unexpected errors.

    Example:
        ```bash
        curl -X PUT http://192.168.210.226:8000/api/edit_trigger_radius/143 \
             -H "Content-Type: application/json" \
             -d '{"radius_ft":2.5}'
        ```
        Response:
        ```json
        {
            "message": "Trigger radius updated successfully"
        }
        ```

    Use Case:
        Adjust the detection area of portable triggers based on operational requirements.

    Hint:
        - Only works on portable triggers (is_portable = true).
        - Radius must be positive.
    """
    logger.debug(f"Received edit_trigger_radius request for trigger {trigger_id}: {request.dict()}")
    try:
        # Validate radius
        if request.radius_ft <= 0:
            raise HTTPException(status_code=400, detail="radius_ft must be positive")

        # Check if trigger exists and is portable
        check_query = "SELECT is_portable FROM triggers WHERE i_trg = $1"
        trigger_check = await execute_raw_query("maint", check_query, trigger_id)
        if not trigger_check:
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
        if not trigger_check[0]["is_portable"]:
            raise HTTPException(status_code=400, detail="Only portable triggers can be edited")

        # Update trigger radius
        update_query = "UPDATE triggers SET radius_ft = $1 WHERE i_trg = $2"
        await execute_raw_query("maint", update_query, request.radius_ft, trigger_id)
        
        logger.info(f"Trigger {trigger_id} radius updated to: {request.radius_ft}ft")
        return {"message": "Trigger radius updated successfully"}
    except Exception as e:
        logger.error(f"Error updating trigger radius: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/edit_trigger_zone/{trigger_id}")
async def edit_trigger_zone(trigger_id: int, request: TriggerZoneEditRequest):
    """
    Edit the zone assignment of a portable trigger.

    This endpoint updates the zone assignment of an existing portable trigger in the ParcoRTLS system.

    Args:
        trigger_id (int): The ID of the trigger to edit (path parameter, required).
        request (TriggerZoneEditRequest): A Pydantic model containing:
            - zone_id (int): New zone ID (required, must exist).

    Returns:
        dict: JSON response containing:
            - message (str): Success message.

    Raises:
        HTTPException:
            - 400: If validation fails (e.g., invalid zone_id, trigger not portable).
            - 404: If trigger or zone not found.
            - 500: For database or unexpected errors.

    Example:
        ```bash
        curl -X PUT http://192.168.210.226:8000/api/edit_trigger_zone/143 \
             -H "Content-Type: application/json" \
             -d '{"zone_id":425}'
        ```
        Response:
        ```json
        {
            "message": "Trigger zone updated successfully"
        }
        ```

    Use Case:
        Move portable triggers between zones for better operational organization.

    Hint:
        - Only works on portable triggers (is_portable = true).
        - Zone must exist in the zones table.
    """
    logger.debug(f"Received edit_trigger_zone request for trigger {trigger_id}: {request.dict()}")
    try:
        # Check if trigger exists and is portable
        check_query = "SELECT is_portable FROM triggers WHERE i_trg = $1"
        trigger_check = await execute_raw_query("maint", check_query, trigger_id)
        if not trigger_check:
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
        if not trigger_check[0]["is_portable"]:
            raise HTTPException(status_code=400, detail="Only portable triggers can be edited")

        # Validate zone
        zone_query = "SELECT COUNT(*) FROM zones WHERE i_zn = $1"
        zone_count = await execute_raw_query("maint", zone_query, request.zone_id)
        if zone_count[0]["count"] == 0:
            raise HTTPException(status_code=404, detail=f"Zone {request.zone_id} not found")

        # Update trigger zone
        update_query = "UPDATE triggers SET i_zn = $1 WHERE i_trg = $2"
        await execute_raw_query("maint", update_query, request.zone_id, trigger_id)
        
        logger.info(f"Trigger {trigger_id} zone updated to: {request.zone_id}")
        return {"message": "Trigger zone updated successfully"}
    except Exception as e:
        logger.error(f"Error updating trigger zone: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload_triggers")
async def reload_triggers():
    """
    Reload triggers for the ParcoRTLS system.

    This endpoint signals a reload of all triggers in the system. The actual reload is handled by the manager's runtime logic, ensuring the latest trigger configurations are processed.

    Returns:
        dict: JSON response containing:
            - message (str): Success message.

    Raises:
        HTTPException:
            - 500: For unexpected errors.

    Example:
        ```bash
        curl -X POST http://192.168.210.226:8000/api/reload_triggers -H "Content-Type: application/json"
        ```
        Response:
        ```json
        {
            "message": "Triggers reload signaled successfully"
        }
        ```

    Use Case:
        Refresh trigger data after creating or modifying triggers, ensuring the manager processes the latest configurations.

    Hint:
        - Called after adding or updating triggers via /api/add_portable_trigger or /api/add_trigger.
        - Relies on manager runtime to reload triggers (e.g., via parser_data_arrived).
    """
    logger.info("Received reload_triggers request")
    try:
        # No direct call to load_triggers; manager reloads triggers via runtime logic
        logger.info("Triggers reload signaled successfully")
        return {"message": "Triggers reload signaled successfully"}
    except Exception as e:
        logger.error(f"Error signaling trigger reload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))