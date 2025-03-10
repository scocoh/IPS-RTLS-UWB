"""
Version: 0.3.1 (Added trigger management for FastAPI with real-time updates via WebSocket, improved data validation)
Trigger management endpoints for ParcoRTLS FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from config import MQTT_BROKER
from models import TriggerAddRequest, TriggerMoveRequest
import paho.mqtt.publish as publish
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["triggers"])  # Remove "prefix=/api"

# Endpoint to fire a trigger event by its name
@router.post("/fire_trigger/{trigger_name}")
async def fire_trigger(trigger_name: str):
    """Fire a trigger event using a path parameter, ensuring it is linked to a valid region."""
    try:
        triggers = await call_stored_procedure("maint", "usp_trigger_list")
        trigger = next((t for t in triggers if t["x_nm_trg"] == trigger_name), None)

        if not trigger:
            raise HTTPException(status_code=404, detail=f"Trigger '{trigger_name}' not found")

        trigger_id = trigger["i_trg"]

        # Ensure the trigger has a valid region
        regions = await call_stored_procedure("maint", "usp_trigger_select", trigger_id)
        if not regions or not isinstance(regions, list) or len(regions) == 0:
            raise HTTPException(status_code=400, detail=f"Trigger '{trigger_name}' has no valid region assigned")

        # Publish MQTT event
        publish.single("home/rtls/trigger", trigger_name, hostname=MQTT_BROKER)

        return {"message": f"Trigger {trigger_name} fired successfully", "trigger_id": trigger_id}

    except DatabaseError as e:
        logger.error(f"Database error firing trigger: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error firing trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to add a new trigger
@router.post("/add_trigger")
async def add_trigger(request: TriggerAddRequest):
    """Add a new trigger and ensure it is assigned to a region with proper vertices."""
    try:
        # Step 1: Add the trigger
        result = await call_stored_procedure(
            "maint", "usp_trigger_add", request.direction, request.name, request.ignore
        )

        logger.debug(f"DEBUG: usp_trigger_add result: {result}")

        if isinstance(result, list) and result and isinstance(result[0], dict) and "usp_trigger_add" in result[0]:
            trigger_id = int(result[0]["usp_trigger_add"])  # Ensure INTEGER type
        elif isinstance(result, int):
            trigger_id = int(result)
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected result format: {result}")

        # Step 2: Fetch the available zone (or pass zone_id in the request)
        zone_id = request.zone_id  # Assume zone_id is provided in the request
        if not zone_id:
            raise HTTPException(status_code=400, detail="Zone ID must be provided")

        # Step 3: Assign a region to the trigger
        region_name = f"Region for Trigger {trigger_id}"
        min_x, min_y, min_z = 0.0, 0.0, 0.0
        max_x, max_y, max_z = 10.0, 10.0, 10.0

        # Call usp_region_add with proper zone_id
        region_result = await call_stored_procedure(
            "maint", "usp_region_add",
            trigger_id,  # i_trg (INTEGER)
            zone_id,  # i_zn (INTEGER)
            str(region_name),  # x_nm_rgn (VARCHAR)
            float(max_x), float(max_y), float(max_z),  # n_max_x, n_max_y, n_max_z (FLOAT)
            float(min_x), float(min_y), float(min_z),  # n_min_x, n_min_y, n_min_z (FLOAT)
            trigger_id  # Extra INTEGER parameter at the end
        )

        if not region_result:
            logger.warning(f"Trigger {trigger_id} created, but no region was assigned.")
            return {
                "message": "Trigger added successfully, but no region was assigned",
                "trigger_id": trigger_id
            }

        region_id = int(region_result[0]["usp_region_add"])  # Correctly extract region ID from dictionary

        # Step 4: Verify the region has sufficient vertices
        vertices = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
        if not vertices or len(vertices) < 3:
            logger.warning(f"Region {region_id} assigned to trigger {trigger_id}, but has insufficient vertices.")
            return {
                "message": "Trigger added successfully, but region lacks sufficient vertices",
                "trigger_id": trigger_id,
                "region_id": region_id
            }

        return {
            "message": "Trigger added successfully and assigned to a region",
            "trigger_id": trigger_id,
            "region_id": region_id
        }

    except DatabaseError as e:
        logger.error(f"Database error adding trigger: {e.message}")
        if "already exists" in e.message:
            raise HTTPException(status_code=400, detail=f"Trigger name '{request.name}' already exists")
        raise HTTPException(status_code=500, detail=f"Database error: {e.message}")

    except Exception as e:
        logger.error(f"Error adding trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


    except DatabaseError as e:
        logger.error(f"Database error adding trigger: {e.message}")
        if "already exists" in e.message:
            raise HTTPException(status_code=400, detail=f"Trigger name '{request.name}' already exists")
        raise HTTPException(status_code=500, detail=f"Database error: {e.message}")

    except Exception as e:
        logger.error(f"Error adding trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to delete a trigger by ID
@router.delete("/delete_trigger/{trigger_id}")
async def delete_trigger(trigger_id: int):
    """Delete a trigger by ID."""
    try:
        result = await call_stored_procedure("maint", "usp_trigger_delete", trigger_id)

        # If result is TRUE, return success
        if result and result[0] is True:
            return {"message": f"Trigger {trigger_id} deleted successfully"}

        # If result is FALSE, trigger was not found
        return {"message": f"Trigger {trigger_id} does not exist or was already deleted"}

    except DatabaseError as e:
        logger.error(f"Database error deleting trigger: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error deleting trigger: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error deleting trigger")


# Endpoint to list all triggers
@router.get("/list_triggers")
async def list_triggers():
    """List all triggers."""
    result = await call_stored_procedure("maint", "usp_trigger_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No triggers found")


# Endpoint to list all trigger directions
@router.get("/list_trigger_directions")
async def list_trigger_directions():
    """List all trigger directions."""
    try:
        result = await call_stored_procedure("maint", "usp_trigger_direction_list")
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No trigger directions found")

    except DatabaseError as e:
        logger.error(f"Database error fetching trigger directions: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching trigger directions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to fetch trigger details by ID
@router.get("/get_trigger_details/{trigger_id}")
async def get_trigger_details(trigger_id: int):
    """Fetch detailed trigger information including regions and zones."""
    result = await call_stored_procedure("maint", "usp_trigger_select", trigger_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Trigger not found")


# Endpoint to move a trigger to a new position
@router.put("/move_trigger/{trigger_id}")
async def move_trigger(trigger_id: int, new_x: float, new_y: float, new_z: float):
    """Move a trigger to a new position."""
    result = await call_stored_procedure("maint", "usp_trigger_move", trigger_id, new_x, new_y, new_z)
    if result is None:
        return {"message": f"Trigger {trigger_id} moved by ({new_x}, {new_y}, {new_z})"}
    raise HTTPException(status_code=500, detail="Failed to move trigger")


# Endpoint to fetch the last known state of a device for a given trigger
@router.get("/get_trigger_state/{trigger_id}/{device_id}")
async def get_trigger_state(trigger_id: int, device_id: str):
    """Fetch the last known state of a device for a given trigger."""
    try:
        query = "SELECT last_state FROM trigger_states WHERE i_trg = $1 AND x_id_dev = $2;"
        result = await execute_raw_query("maint", query, trigger_id, device_id)
        
        if result:
            return {"trigger_id": trigger_id, "device_id": device_id, "last_state": result[0]["last_state"]}

        raise HTTPException(status_code=404, detail="No state data found for this trigger and device")

    except DatabaseError as e:
        logger.error(f"Database error fetching trigger state: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching trigger state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to fetch triggers by point coordinates
@router.get("/get_triggers_by_point")
async def get_triggers_by_point(x: float, y: float, z: float):
    """Fetch triggers by point coordinates."""
    try:
        query = """
            SELECT t.i_trg, t.x_nm_trg, t.i_dir, t.f_ign, r.i_rgn, v.n_x, v.n_y, v.n_z
            FROM public.triggers t
            JOIN public.regions r ON t.i_trg = r.i_trg
            JOIN public.vertices v ON r.i_rgn = v.i_rgn
            WHERE v.n_x = $1 AND v.n_y = $2 AND v.n_z = $3;
        """
        result = await execute_raw_query("maint", query, x, y, z)
        if result:
            return result
        raise HTTPException(status_code=404, detail="No triggers found for point")

    except DatabaseError as e:
        logger.error(f"Database error fetching triggers by point: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching triggers by point: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
