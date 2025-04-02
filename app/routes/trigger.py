# VERSION 250325 /home/parcoadmin/parco_fastapi/app/routes/trigger.py 0P.10B.13
# --- CHANGED: Bumped version from 0P.10B.12 to 0P.10B.13
# --- FIXED: Modified /get_zone_vertices/{zone_id} to only return vertices for regions not associated with triggers (i_trg IS NULL)
# 
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

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
        
        logger.debug(f"Received vertices: {request.vertices}")  # Add this line

        # Step 3: Assign a region to the trigger
        region_name = f"Region for Trigger {trigger_id}"

        # Calculate bounding box from vertices
        if request.vertices and len(request.vertices) >= 3:
            # Use provided vertices
            vertices = request.vertices
            min_x = min(v["x"] for v in vertices)
            max_x = max(v["x"] for v in vertices)
            min_y = min(v["y"] for v in vertices)
            max_y = max(v["y"] for v in vertices)
            min_z = min(v.get("z", 0.0) for v in vertices)  # Default to 0 if z is missing
            max_z = max(v.get("z", 0.0) for v in vertices)
        else:
            # Fall back to default triangle
            vertices = [
                {"x": 0.0, "y": 0.0, "z": 0.0},
                {"x": 10.0, "y": 0.0, "z": 0.0},
                {"x": 0.0, "y": 10.0, "z": 0.0},
                {"x": 0.0, "y": 0.0, "z": 0.0}
            ]
            min_x, min_y, min_z = 0.0, 0.0, 0.0
            max_x, max_y, max_z = 10.0, 10.0, 10.0

        # Call usp_region_add with calculated bounding box
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

        # Step 4: Add vertices to the region
        for i, vertex in enumerate(vertices, 1):
            await call_stored_procedure(
                "maint", "usp_vertex_add",
                region_id,  # i_rgn (INTEGER)
                float(vertex["x"]),  # n_x (FLOAT)
                float(vertex["y"]),  # n_y (FLOAT)
                float(vertex.get("z", 0.0)),  # n_z (FLOAT), default to 0 if missing
                i  # n_ord (INTEGER)
            )

        # Step 5: Verify the region has sufficient vertices
        vertices_result = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
        if not vertices_result or len(vertices_result) < 3:
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

# Endpoint to delete a trigger by ID
@router.delete("/delete_trigger/{trigger_id}")
async def delete_trigger(trigger_id: int):
    """Delete a trigger by ID, first removing associated regions and vertices."""
    try:
        # Step 1: Find the region associated with the trigger
        find_region_query = """
            SELECT i_rgn FROM public.regions WHERE i_trg = $1
        """
        region_result = await execute_raw_query("maint", find_region_query, trigger_id)
        
        if region_result:
            region_id = region_result[0]["i_rgn"]
            logger.info(f"Found region {region_id} for trigger {trigger_id}")

            # Step 2: Delete vertices associated with the region
            delete_vertices_query = """
                DELETE FROM public.vertices WHERE i_rgn = $1
            """
            await execute_raw_query("maint", delete_vertices_query, region_id)
            logger.info(f"Deleted vertices for region {region_id}")

            # Step 3: Delete the region
            delete_region_query = """
                DELETE FROM public.regions WHERE i_rgn = $1
            """
            await execute_raw_query("maint", delete_region_query, region_id)
            logger.info(f"Deleted region {region_id} for trigger {trigger_id}")
        else:
            logger.info(f"No region found for trigger {trigger_id}")

        # Step 4: Delete the trigger
        result = await call_stored_procedure("maint", "usp_trigger_delete", trigger_id)

        # If result is TRUE, return success
        if result and result[0]["usp_trigger_delete"] is True:
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

# Endpoint to list all triggers - 250330 Revised for New Trigger Demo by Grok
@router.get("/list_newtriggers")
async def list_newtriggers():
    """List all triggers with zone information (experimental)."""
    try:
        # Fetch triggers using the stored procedure
        triggers_data = await call_stored_procedure("maint", "usp_trigger_list")
        if not triggers_data:
            raise HTTPException(status_code=404, detail="No triggers found")

        # Fetch zone information using raw SQL query
        trigger_ids = [trigger["i_trg"] for trigger in triggers_data]
        if not trigger_ids:
            return triggers_data

        zone_query = """
            SELECT t.i_trg, r.i_zn AS zone_id, z.x_nm_zn AS zone_name
            FROM triggers t
            LEFT JOIN regions r ON t.i_trg = r.i_trg
            LEFT JOIN zones z ON r.i_zn = z.i_zn
            WHERE t.i_trg = ANY($1)
        """
        zone_data = await execute_raw_query("maint", zone_query, trigger_ids)
        zone_map = {item["i_trg"]: {"zone_id": item["zone_id"], "zone_name": item["zone_name"]} for item in zone_data}

        # Merge zone information into triggers data
        for trigger in triggers_data:
            trigger_id = trigger["i_trg"]
            zone_info = zone_map.get(trigger_id, {"zone_id": None, "zone_name": None})
            trigger["zone_id"] = zone_info["zone_id"]
            trigger["zone_name"] = zone_info["zone_name"]

        return triggers_data
    except Exception as e:
        logger.error(f"Error retrieving new triggers: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving new triggers: {str(e)}")



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
# @router.get("/get_trigger_details/{trigger_id}")
# async def get_trigger_details(trigger_id: int):
#    """Fetch detailed trigger information including regions and zones."""
#    result = await call_stored_procedure("maint", "usp_trigger_select", trigger_id)
#    if result:
#        return result
#    raise HTTPException(status_code=404, detail="Trigger not found")
@router.get("/get_trigger_details/{trigger_id}")
async def get_trigger_details(trigger_id: int):
    """Fetch details of a specific trigger, including its vertices."""
    try:
        # Fetch the region associated with the trigger
        region_query = """
            SELECT i_rgn FROM regions WHERE i_trg = $1
        """
        region = await execute_raw_query("maint", region_query, trigger_id)
        if not region:
            raise HTTPException(status_code=404, detail=f"No region found for trigger ID {trigger_id}")
        region_id = region[0]["i_rgn"]

        # Fetch the vertices for the region
        vertices_query = """
            SELECT n_x AS x, n_y AS y, COALESCE(n_z, 0.0) AS z, n_ord
            FROM vertices
            WHERE i_rgn = $1
            ORDER BY n_ord
        """
        vertices = await execute_raw_query("maint", vertices_query, region_id)
        return {"vertices": vertices}
    except Exception as e:
        logger.error(f"Error fetching trigger details for ID {trigger_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching trigger details: {str(e)}")


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

# Endpoint to fetch triggers by zone ID
@router.get("/get_triggers_by_zone/{zone_id}")
async def get_triggers_by_zone(zone_id: int):
    """Fetch all triggers for a given zone, including direction names."""
    try:
        query = """
            SELECT 
                t.i_trg AS trigger_id, 
                t.x_nm_trg AS name, 
                d.x_dir AS direction_name, 
                r.i_zn AS zone_id
            FROM public.triggers t
            JOIN public.regions r ON t.i_trg = r.i_trg
            JOIN public.tlktrigdirections d ON t.i_dir = d.i_dir
            WHERE r.i_zn = $1
        """
        result = await execute_raw_query("maint", query, zone_id)
        if not result:
            return []
        logger.info(f"Fetched {len(result)} triggers for zone {zone_id}")
        return result
    except DatabaseError as e:
        logger.error(f"Database error fetching triggers for zone {zone_id}: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching triggers for zone {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to fetch vertices for a zone (excluding trigger-related regions)
@router.get("/get_zone_vertices/{zone_id}")
async def get_zone_vertices(zone_id: int):
    """Fetch vertices for a given zone, excluding regions associated with triggers."""
    try:
        query = """
            SELECT v.*
            FROM vertices v
            JOIN regions r ON v.i_rgn = r.i_rgn
            WHERE r.i_zn = $1 AND r.i_trg IS NULL
        """
        vertices = await execute_raw_query("maint", query, zone_id)
        return {"vertices": vertices}
    except DatabaseError as e:
        logger.error(f"Database error fetching zone vertices: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching zone vertices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))