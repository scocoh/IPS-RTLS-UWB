# /home/parcoadmin/parco_fastapi/app/routes/trigger.py
# Name: trigger.py
# Version: 0.1.70
# Created: 971201
# Modified: 250725
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & Claude AI
# Version 0.1.70 Fixed trigger coordinate precision by replacing raw trigger queries with stored procedure calls for 6 decimal place rounding on radius_ft, z_min, z_max
# Version 0.1.69 Fixed coordinate precision by replacing raw vertex queries with stored procedure calls for 6 decimal place rounding
# Version 0.1.68 Enhanced error messages for boundary violations with detailed coordinate information
# Version 0.1.67 updated add_trigger endpoint for z coordinate bug on 250718
# Version: 0.1.66 - Uses dynamic bounding box calculation from vertices (like get_zone_bounding_box)
# Version: 0.1.65 - changed vertices to tuples
# Version: 0.1.64 - Added hybrid polygon containment while preserving bounding box logic, bumped from 0.1.63
# Version 0.1.62 Fixed zone 425 trigger creation by auto-correcting Z-coordinates to fit within zone boundaries, bumped from 0.1.61
# Version 0.1.61 - Added explicit type casting for usp_region_add to fix zone 425 trigger creation bug
# Version 0.1.61 Added in endpoint for add_trigger_from_zone data
# Version 0.1.60 Changed version added endpoint add_portable_trigger
# CHANGED: Fixed column name in list_newtriggers from f_portable to is_portable, bumped to 0P.10B.21
# PREVIOUS: Updated list_newtriggers to set zone_id from triggers.i_zn or regions.i_zn, bumped to 0P.10B.20-250427
# --- PREVIOUS: Enhanced docstrings for all endpoints, bumped to 0P.10B.19-250426
# --- CHANGED: Bumped version from 0P.10B.18-250423 to 0P.10B.19-250426
# --- ADDED: Enhanced docstrings for all endpoints with detailed descriptions, parameters, return values, examples, use cases, hints, and error handling
# --- PREVIOUS: Restored get_triggers_by_zone endpoint, changed t.zone_id to t.i_zn in get_triggers_by_zone_with_id, trigger_contains_point, triggers_by_point
# --- PREVIOUS: Added endpoints for trigger_contains_point, zones_by_point, triggers_by_point
# --- PREVIOUS: Noted get_triggers_by_zone_with_id requires i_zn column in triggers table
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
from manager.region import Region3D, Region3DCollection
from manager.portable_trigger import PortableTrigger
from manager.enums import TriggerDirections
import paho.mqtt.publish as publish
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "trigger" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter(tags=["triggers"])  # Remove "prefix=/api"

# Endpoint to fire a trigger event by its name
@router.post(
    "/fire_trigger/{trigger_name}",
    summary="Fire a trigger event by its name, publishing an MQTT message to notify the ParcoRTLS system",
    description=load_description("fire_trigger"),
    tags=["triggers"]
)
async def fire_trigger(trigger_name: str):
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

# Helper function to fetch zone bounding box
async def get_zone_bounding_box(zone_id: int):
    """
    Fetch the bounding box of a zone by aggregating its region vertices.

    This internal helper function retrieves the minimum and maximum x, y, z coordinates of a zone's region vertices to define its bounding box. It is used to validate trigger regions during addition.

    Args:
        zone_id (int): The ID of the zone to fetch the bounding box for.

    Returns:
        dict: A dictionary containing:
            - min_x (float): Minimum x-coordinate.
            - max_x (float): Maximum x-coordinate.
            - min_y (float): Minimum y-coordinate.
            - max_y (float): Maximum y-coordinate.
            - min_z (float): Minimum z-coordinate.
            - max_z (float): Maximum z-coordinate.

    Raises:
        HTTPException:
            - 404: If no region is found for the zone.
            - 400: If the zone has insufficient vertices (< 3).
            - 500: For database or unexpected errors.
    """
    try:
        # Fetch the zone's region (excluding trigger regions)
        query = """
            SELECT r.i_rgn
            FROM regions r
            WHERE r.i_zn = $1 AND r.i_trg IS NULL
        """
        region_result = await execute_raw_query("maint", query, zone_id)
        if not region_result:
            raise HTTPException(status_code=404, detail=f"No region found for zone ID {zone_id}")

        region_id = region_result[0]["i_rgn"]

        # Use stored procedure for rounded coordinates instead of raw query
        vertices = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
        if not vertices or len(vertices) < 3:
            raise HTTPException(status_code=400, detail=f"Zone ID {zone_id} has insufficient vertices")

        # Calculate bounding box from rounded coordinates
        min_x = min(float(v["n_x"]) for v in vertices)
        max_x = max(float(v["n_x"]) for v in vertices)
        min_y = min(float(v["n_y"]) for v in vertices)
        max_y = max(float(v["n_y"]) for v in vertices)
        min_z = min(float(v["n_z"]) for v in vertices)
        max_z = max(float(v["n_z"]) for v in vertices)

        return {
            "min_x": min_x, "max_x": max_x,
            "min_y": min_y, "max_y": max_y,
            "min_z": min_z, "max_z": max_z
        }
    except Exception as e:
        logger.error(f"Error fetching bounding box for zone {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching zone bounding box: {str(e)}")

# Enhanced helper function to create detailed boundary violation error messages
def create_boundary_error_message(coordinate_type: str, trigger_min: float, trigger_max: float, 
                                 zone_min: float, zone_max: float) -> str:
    """
    Create a detailed, user-friendly error message for coordinate boundary violations.
    
    Args:
        coordinate_type (str): Type of coordinate (X, Y, or Z)
        trigger_min (float): Minimum trigger coordinate
        trigger_max (float): Maximum trigger coordinate
        zone_min (float): Minimum zone boundary
        zone_max (float): Maximum zone boundary
    
    Returns:
        str: Formatted error message with specific guidance
    """
    return (
        f"Trigger {coordinate_type} coordinates (min: {trigger_min:.1f}, max: {trigger_max:.1f}) "
        f"exceed zone boundaries (min: {zone_min:.1f}, max: {zone_max:.1f}). "
        f"Please adjust trigger placement to fit within the zone {coordinate_type} range "
        f"{zone_min:.1f} to {zone_max:.1f}."
    )

# Endpoint to add a new trigger
@router.post(
    "/add_trigger",
    summary="Add a new trigger to the ParcoRTLS system and assign it to a region with vertices. (if applicable)",
    description=load_description("add_trigger"),
    tags=["triggers"]
)
async def add_trigger(request: TriggerAddRequest):
    try:
        # Step 1: Add the trigger with explicit type casts
        result = await call_stored_procedure(
            "maint", "usp_trigger_add",
            int(request.direction), str(request.name), bool(request.ignore), int(request.zone_id) if request.zone_id is not None else None
        )

        logger.debug(f"DEBUG: usp_trigger_add result: {result}")

        if isinstance(result, list) and result and isinstance(result[0], dict) and "usp_trigger_add" in result[0]:
            trigger_id = int(result[0]["usp_trigger_add"])
        elif isinstance(result, int):
            trigger_id = int(result)
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected result format: {result}")

        # Step 2: Handle zone association
        zone_id = request.zone_id
        region_id = None
        if zone_id:
            # Step 3: Fetch zone boundaries for validation (FIXED - use region boundaries not vertices)
            try:
                zone_boundaries = await get_zone_boundaries(zone_id)
                zone_bbox = {
                    "min_x": zone_boundaries["min_x"],
                    "max_x": zone_boundaries["max_x"], 
                    "min_y": zone_boundaries["min_y"],
                    "max_y": zone_boundaries["max_y"],
                    "min_z": zone_boundaries["min_z"], 
                    "max_z": zone_boundaries["max_z"]
                }
                logger.debug(f"Using region boundaries for zone {zone_id}: {zone_bbox}")
            except HTTPException as e:
                # Fallback to vertex-based calculation if region boundaries not available
                logger.warning(f"Could not get region boundaries for zone {zone_id}, falling back to vertex calculation")
                zone_bbox = await get_zone_bounding_box(zone_id)

            # Step 4: Calculate trigger bounding box from vertices
            logger.debug(f"Received vertices: {request.vertices}")
            if request.vertices and len(request.vertices) >= 3:
                vertices = request.vertices
                min_x = min(v["x"] for v in vertices)
                max_x = max(v["x"] for v in vertices)
                min_y = min(v["y"] for v in vertices)
                max_y = max(v["y"] for v in vertices)
                min_z = min(v.get("z", 0.0) for v in vertices)
                max_z = max(v.get("z", 0.0) for v in vertices)
            else:
                # Default triangle
                vertices = [
                    {"x": 0.0, "y": 0.0, "z": 0.0},
                    {"x": 10.0, "y": 0.0, "z": 0.0},
                    {"x": 0.0, "y": 10.0, "z": 0.0},
                    {"x": 0.0, "y": 0.0, "z": 0.0}
                ]
                min_x, min_y, min_z = 0.0, 0.0, 0.0
                max_x, max_y, max_z = 10.0, 10.0, 10.0

            # Step 5: Enhanced coordinate validation with detailed error messages
            corrections_made = []
            
            # Check X coordinates with detailed error message
            if min_x < zone_bbox["min_x"] or max_x > zone_bbox["max_x"]:
                error_message = create_boundary_error_message(
                    "X", min_x, max_x, zone_bbox["min_x"], zone_bbox["max_x"]
                )
                raise HTTPException(status_code=400, detail=error_message)
            
            # Check Y coordinates with detailed error message
            if min_y < zone_bbox["min_y"] or max_y > zone_bbox["max_y"]:
                error_message = create_boundary_error_message(
                    "Y", min_y, max_y, zone_bbox["min_y"], zone_bbox["max_y"]
                )
                raise HTTPException(status_code=400, detail=error_message)
            
            # Auto-correct Z coordinates to fit within zone boundaries
            original_min_z, original_max_z = min_z, max_z
            
            if min_z < zone_bbox["min_z"]:
                min_z = zone_bbox["min_z"]
                corrections_made.append(f"min_z corrected from {original_min_z:.2f} to {min_z:.2f}")
                # Update vertices with corrected Z
                for vertex in vertices:
                    if vertex.get("z", 0.0) < zone_bbox["min_z"]:
                        vertex["z"] = zone_bbox["min_z"]
                        
            if max_z > zone_bbox["max_z"]:
                max_z = zone_bbox["max_z"]
                corrections_made.append(f"max_z corrected from {original_max_z:.2f} to {max_z:.2f}")
                # Update vertices with corrected Z
                for vertex in vertices:
                    if vertex.get("z", 0.0) > zone_bbox["max_z"]:
                        vertex["z"] = zone_bbox["max_z"]

            # Step 6: Assign a region to the trigger
            region_name = f"Region for Trigger {trigger_id}"
            region_result = await call_stored_procedure(
                "maint", "usp_region_add",
                trigger_id, zone_id, str(region_name),
                float(max_x), float(max_y), float(max_z),
                float(min_x), float(min_y), float(min_z),
                trigger_id
            )

            if not region_result:
                logger.warning(f"Trigger {trigger_id} created, but no region was assigned.")
                return {
                    "message": "Trigger added successfully, but no region was assigned",
                    "trigger_id": trigger_id
                }

            region_id = int(region_result[0]["usp_region_add"])

            # Step 7: Add vertices to the region
            for i, vertex in enumerate(vertices, 1):
                await call_stored_procedure(
                    "maint", "usp_vertex_add",
                    region_id, float(vertex["x"]), float(vertex["y"]), float(vertex.get("z", 0.0)), i
                )

            # Step 8: Verify the region has sufficient vertices
            vertices_result = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
            if not vertices_result or len(vertices_result) < 3:
                logger.warning(f"Region {region_id} assigned to trigger {trigger_id}, but has insufficient vertices.")
                return {
                    "message": "Trigger added successfully, but region lacks sufficient vertices",
                    "trigger_id": trigger_id,
                    "region_id": region_id
                }

        # Return enhanced response with detailed correction information
        base_message = "Trigger added successfully and assigned to a region"
        if corrections_made:
            correction_details = "; ".join(corrections_made)
            message = f"{base_message}. Auto-corrections applied: {correction_details}"
        else:
            message = base_message

        return {
            "message": message,
            "trigger_id": trigger_id,
            "region_id": region_id,
            "corrections_applied": corrections_made,
            "zone_boundaries": {
                "x_range": f"{zone_bbox['min_x']:.1f} to {zone_bbox['max_x']:.1f}",
                "y_range": f"{zone_bbox['min_y']:.1f} to {zone_bbox['max_y']:.1f}",
                "z_range": f"{zone_bbox['min_z']:.1f} to {zone_bbox['max_z']:.1f}"
            } if zone_id else None
        }

    except DatabaseError as e:
        logger.error(f"Database error adding trigger: {e.message}")
        if "already exists" in e.message:
            raise HTTPException(status_code=400, detail=f"Trigger name '{request.name}' already exists. Please choose a different name.")
        raise HTTPException(status_code=500, detail=f"Database error: {e.message}")
    except Exception as e:
        logger.error(f"Error adding trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ... (rest of the endpoints remain unchanged) ...

# Endpoint to delete a trigger by ID
@router.delete(
    "/delete_trigger/{trigger_id}",
    summary="Delete a trigger by its ID, removing associated regions and vertices",
    description=load_description("delete_trigger"),
    tags=["triggers"]
)
async def delete_trigger(trigger_id: int):
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
@router.get(
    "/list_triggers",
    summary="List all triggers in the ParcoRTLS system",
    description=load_description("list_triggers"),
    tags=["triggers"]
)
async def list_triggers():
    result = await call_stored_procedure("maint", "usp_trigger_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No triggers found")

# Endpoint to list all triggers with zone information
@router.get(
    "/list_newtriggers",
    summary="List all triggers with associated zone information (experimental)",
    description=load_description("list_newtriggers"),
    tags=["triggers"]
)
async def list_newtriggers():
    try:
        # Fetch triggers with position data placeholders
        query = """
            SELECT 
                t.i_trg, t.x_nm_trg, t.i_zn, t.i_dir, t.is_portable, 
                t.assigned_tag_id, t.radius_ft, t.z_min, t.z_max,
                NULL AS pos_x, NULL AS pos_y, NULL AS pos_z
            FROM triggers t
        """
        triggers_data = await execute_raw_query("maint", query)
        if not triggers_data:
            logger.warning("No triggers found")
            raise HTTPException(status_code=404, detail="No triggers found")

        # Fetch zone information
        trigger_ids = [trigger["i_trg"] for trigger in triggers_data]
        zone_query = """
            SELECT t.i_trg, t.i_zn AS trigger_zone_id, r.i_zn AS region_zone_id, z.x_nm_zn AS zone_name
            FROM triggers t
            LEFT JOIN regions r ON t.i_trg = r.i_trg
            LEFT JOIN zones z ON COALESCE(t.i_zn, r.i_zn) = z.i_zn
            WHERE t.i_trg = ANY($1)
        """
        zone_data = await execute_raw_query("maint", zone_query, trigger_ids)
        zone_map = {item["i_trg"]: {"trigger_zone_id": item["trigger_zone_id"], "region_zone_id": item["region_zone_id"], "zone_name": item["zone_name"]} for item in zone_data}

        # Merge zone information
        for trigger in triggers_data:
            trigger_id = trigger["i_trg"]
            zone_info = zone_map.get(trigger_id, {"trigger_zone_id": None, "region_zone_id": None, "zone_name": None})
            # Prefer trigger_zone_id, fallback to region_zone_id
            trigger["zone_id"] = zone_info["trigger_zone_id"] if zone_info["trigger_zone_id"] is not None else zone_info["region_zone_id"]
            trigger["zone_name"] = zone_info["zone_name"]

        logger.info(f"Fetched {len(triggers_data)} triggers")
        return triggers_data
    except Exception as e:
        logger.error(f"Error retrieving new triggers: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving new triggers: {str(e)}")

# Endpoint to list all trigger directions
@router.get(
    "/list_trigger_directions",
    summary="List all available trigger directions in the ParcoRTLS system",
    description=load_description("list_trigger_directions"),
    tags=["triggers"]
)
async def list_trigger_directions():
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
@router.get(
    "/get_trigger_details/{trigger_id}",
    summary="Fetch details of a specific trigger, including its region vertices",
    description=load_description("get_trigger_details"),
    tags=["triggers"]
)
async def get_trigger_details(trigger_id: int):
    try:
        # Fetch the region associated with the trigger
        region_query = """
            SELECT i_rgn FROM regions WHERE i_trg = $1
        """
        region = await execute_raw_query("maint", region_query, trigger_id)
        if not region:
            raise HTTPException(status_code=404, detail=f"No region found for trigger ID {trigger_id}")
        region_id = region[0]["i_rgn"]

        # Use stored procedure for rounded coordinates instead of raw query
        vertices = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
        
        # Convert stored procedure result to expected format
        formatted_vertices = []
        for vertex in vertices:
            formatted_vertices.append({
                "x": float(vertex["n_x"]),
                "y": float(vertex["n_y"]),
                "z": float(vertex["n_z"]),
                "n_ord": vertex["n_ord"]
            })
        
        return {"vertices": formatted_vertices}
    except Exception as e:
        logger.error(f"Error fetching trigger details for ID {trigger_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching trigger details: {str(e)}")

# Endpoint to move a trigger to a new position
@router.put(
    "/move_trigger/{trigger_id}",
    summary="Move a trigger to a new position in the ParcoRTLS system",
    description=load_description("move_trigger"),
    tags=["triggers"]
)
async def move_trigger(trigger_id: int, new_x: float, new_y: float, new_z: float):
    try:
        result = await call_stored_procedure("maint", "usp_trigger_move", trigger_id, new_x, new_y, new_z)
        if result is None:
            return {"message": f"Trigger {trigger_id} moved by ({new_x}, {new_y}, {new_z})"}
        raise HTTPException(status_code=500, detail="Failed to move trigger")
    except DatabaseError as e:
        logger.error(f"Database error moving trigger: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error moving trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to fetch the last known state of a device for a given trigger
@router.get(
    "/get_trigger_state/{trigger_id}/{device_id}",
    summary="Fetch the last known state of a device for a given trigger",
    description=load_description("get_trigger_state"),
    tags=["triggers"]
)
async def get_trigger_state(trigger_id: int, device_id: str):
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
@router.get(
    "/get_triggers_by_point",
    summary="Fetch triggers whose regions contain the specified point coordinates",
    description=load_description("get_triggers_by_point"),
    tags=["triggers"]
)
async def get_triggers_by_point(x: float, y: float, z: float):
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
@router.get(
    "/get_triggers_by_zone/{zone_id}",
    summary="Fetch all triggers associated with a given zone, including direction names",
    description=load_description("get_triggers_by_zone"),
    tags=["triggers"]
)
async def get_triggers_by_zone(zone_id: int):
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

# Endpoint to fetch triggers by zone ID with direction_id
@router.get(
    "/get_triggers_by_zone_with_id/{zone_id}",
    summary="Fetch all triggers for a given zone, including direction IDs and portable trigger details",
    description=load_description("get_triggers_by_zone_with_id"),
    tags=["triggers"]
)
async def get_triggers_by_zone_with_id(zone_id: int):
    try:
        # Use stored procedure for rounded coordinates instead of raw query
        result = await call_stored_procedure("maint", "usp_triggers_select_by_zone_with_rounded_coords", zone_id)
        if not result:
            return []
        logger.info(f"Fetched {len(result)} triggers for zone {zone_id} with direction_id")
        return result
    except DatabaseError as e:
        logger.error(f"Database error fetching triggers for zone {zone_id}: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching triggers for zone {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to check if a point is within a trigger's region
@router.get(
    "/trigger_contains_point/{trigger_id}",
    summary="Check if a point is within a trigger's region (2D or 3D) with hybrid containment",
    description=load_description("trigger_contains_point"),
    tags=["triggers"]
)
async def trigger_contains_point(trigger_id: int, x: float, y: float, z: float = None): # type: ignore
    try:
        # Use stored procedure for rounded coordinates instead of raw query for trigger data
        trigger_data = await call_stored_procedure("maint", "usp_trigger_select_with_rounded_coords", trigger_id)
        logger.debug(f"Trigger data result: {trigger_data}")
        if not trigger_data:
            logger.error(f"Trigger {trigger_id} not found in triggers table")
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
        
        trigger = trigger_data[0]
        logger.debug(f"Trigger details: {trigger}")
        
        if trigger["is_portable"]:
            # Portable trigger: Use radius and z bounds (existing logic preserved)
            if not all([trigger["radius_ft"], trigger["z_min"] is not None, trigger["z_max"] is not None]):
                logger.error(f"Portable trigger {trigger_id} missing radius or z bounds: {trigger}")
                raise HTTPException(status_code=400, detail="Portable trigger missing radius or z bounds")
            
            # For portable triggers, we need the position of the assigned tag as the center
            if not trigger["assigned_tag_id"]:
                logger.error(f"Portable trigger {trigger_id} missing assigned tag ID")
                raise HTTPException(status_code=400, detail="Portable trigger missing assigned tag ID")
            
            # The WebSocket server provides x, y, z as the tag's position (e.g., SIM1's position)
            # For portable triggers, this position is the center of the trigger
            center_x, center_y, center_z = x, y, z if z is not None else 0
            radius = float(trigger["radius_ft"])
            
            # Fetch the zone's vertices to determine a reference point to check against
            # We'll use the centroid of the zone as the point to check
            zone_id = trigger["i_zn"]
            if not zone_id:
                logger.error(f"Portable trigger {trigger_id} missing zone ID")
                raise HTTPException(status_code=400, detail="Portable trigger missing zone ID")
            
            # Use stored procedure for rounded coordinates
            zone_vertices = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", zone_id)
            if not zone_vertices:
                logger.error(f"No vertices found for zone {zone_id} of trigger {trigger_id}")
                return {"contains": False}
            
            # Calculate the centroid of the zone as the point to check
            avg_x = sum(float(v["n_x"]) for v in zone_vertices) / len(zone_vertices)
            avg_y = sum(float(v["n_y"]) for v in zone_vertices) / len(zone_vertices)
            avg_z = sum(float(v["n_z"]) for v in zone_vertices) / len(zone_vertices)
            
            # Check if the zone centroid is within the trigger's radius centered at the tag's position
            distance = ((avg_x - center_x) ** 2 + (avg_y - center_y) ** 2) ** 0.5
            logger.debug(f"Portable trigger {trigger_id}: distance from zone centroid [{avg_x}, {avg_y}] to tag position [{center_x}, {center_y}] = {distance}, radius = {radius}")
            if z is not None:
                if not (float(trigger["z_min"]) <= z <= float(trigger["z_max"])):
                    logger.debug(f"Portable trigger {trigger_id}: z={z} outside bounds [{trigger['z_min']}, {trigger['z_max']}]")
                    return {"contains": False}
            contains = distance <= radius
            logger.debug(f"Portable trigger {trigger_id}: contains = {contains}")
            return {"contains": contains}
        else:
            # Non-portable trigger: Enhanced hybrid containment check
            region_query = """
                SELECT i_rgn FROM regions WHERE i_trg = $1
            """
            region = await execute_raw_query("maint", region_query, trigger_id)
            if not region:
                logger.error(f"No region found for trigger {trigger_id}")
                raise HTTPException(status_code=404, detail=f"No region found for trigger {trigger_id}")
            region_id = region[0]["i_rgn"]
            
            # Use stored procedure for rounded coordinates
            vertices = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
            if len(vertices) < 3:
                logger.error(f"Region for trigger {trigger_id} has insufficient vertices: {len(vertices)}")
                raise HTTPException(status_code=400, detail="Region has insufficient vertices")
            
            # NEW: Create region with vertices for hybrid containment
            regions = Region3DCollection()
            x_coords = [float(v["n_x"]) for v in vertices]
            y_coords = [float(v["n_y"]) for v in vertices]
            z_coords = [float(v["n_z"]) for v in vertices]
            
            # Create Region3D with vertices for polygon containment
            region_3d = Region3D(
                min_x=min(x_coords),
                max_x=max(x_coords),
                min_y=min(y_coords),
                max_y=max(y_coords),
                min_z=min(z_coords),
                max_z=max(z_coords),
                vertices=[(float(v["n_x"]), float(v["n_y"]), float(v["n_z"])) for v in vertices]  # NEW: Pass vertices as tuples for polygon containment
            )
            regions.add(region_3d)
            
            # NEW: Use hybrid containment (bounding box + polygon)
            if z is None:
                contains = any(region.contains_point_hybrid(x, y) for region in regions.regions)
                logger.debug(f"Non-portable trigger {trigger_id}: 2D hybrid containment = {contains}")
            else:
                contains = any(region.contains_point_hybrid(x, y, z) for region in regions.regions)
                logger.debug(f"Non-portable trigger {trigger_id}: 3D hybrid containment = {contains}")
            
            # OPTIONAL: For debugging, also show original bounding box result
            if z is None:
                bbox_contains = any(region.contains_point_in_2d(x, y) for region in regions.regions)
            else:
                bbox_contains = any(region.contains_point(x, y, z) for region in regions.regions)
            
            logger.debug(f"Trigger {trigger_id}: Bounding box result: {bbox_contains}, Hybrid result: {contains}")
            
            return {"contains": contains}
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error checking trigger containment: {e}")
        return {"contains": False}  # Return a default response to avoid frontend error
    
# Endpoint to fetch zones that may contain a point
@router.get(
    "/zones_by_point",
    summary="Fetch zones that may contain a given point (x, y, z) based on their bounding box",
    description=load_description("zones_by_point"),
    tags=["triggers"]
)
async def zones_by_point(x: float, y: float, z: float, zone_type: int = 0):
    try:
        # Get all zones (with optional type filter)
        zone_query = "SELECT i_zn, x_nm_zn FROM zones"
        if zone_type > 0:
            zone_query += " WHERE i_typ_zn = $1"
            zones = await execute_raw_query("maint", zone_query, zone_type)
        else:
            zones = await execute_raw_query("maint", zone_query)
        
        result = []
        for zone in zones:
            zone_id = zone["i_zn"]
            zone_name = zone["x_nm_zn"]
            
            try:
                # Use the same dynamic bounding box logic as get_zone_bounding_box
                bbox_query = """
                    SELECT r.i_rgn
                    FROM regions r
                    WHERE r.i_zn = $1 AND r.i_trg IS NULL
                """
                region_result = await execute_raw_query("maint", bbox_query, zone_id)
                if not region_result:
                    continue  # Skip zones without regions
                
                region_id = region_result[0]["i_rgn"]
                
                # Use stored procedure for rounded coordinates
                vertices = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
                if not vertices or len(vertices) < 3:
                    continue  # Skip zones with insufficient vertices
                
                # Calculate dynamic bounding box from rounded coordinates
                min_x = min(float(v["n_x"]) for v in vertices)
                max_x = max(float(v["n_x"]) for v in vertices)
                min_y = min(float(v["n_y"]) for v in vertices)
                max_y = max(float(v["n_y"]) for v in vertices)
                min_z = min(float(v["n_z"]) for v in vertices)
                max_z = max(float(v["n_z"]) for v in vertices)
                
                # Check if point is within calculated bounding box
                contains = (
                    min_x <= x <= max_x and
                    min_y <= y <= max_y and
                    min_z <= z <= max_z
                )
                
                # Only include zones that actually contain the point
                if contains:
                    result.append({
                        "zone_id": zone_id,
                        "zone_name": zone_name,
                        "contains": True
                    })
                    
            except Exception as zone_error:
                # Skip zones with errors (missing regions, etc.)
                logger.debug(f"Skipping zone {zone_id} due to error: {zone_error}")
                continue
        
        return result
        
    except DatabaseError as e:
        logger.error(f"Database error fetching zones by point: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching zones by point: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint to fetch triggers that may contain a point
@router.get(
    "/triggers_by_point",
    summary="Fetch triggers whose regions may contain a given point (x, y, z) with hybrid containment",
    description=load_description("triggers_by_point"),
    tags=["triggers"]
)
async def triggers_by_point(x: float, y: float, z: float):
    try:
        query = """
            SELECT 
                t.i_trg, t.x_nm_trg, t.i_dir, t.is_portable, t.assigned_tag_id,
                t.radius_ft, t.z_min, t.z_max, t.i_zn AS zone_id
            FROM triggers t
            LEFT JOIN regions r ON t.i_trg = r.i_trg
            WHERE (r.i_trg IS NOT NULL
                   AND $1 BETWEEN r.n_min_x AND r.n_max_x
                   AND $2 BETWEEN r.n_min_y AND r.n_max_y
                   AND $3 BETWEEN r.n_min_z AND r.n_max_z)
               OR t.is_portable = true
        """
        triggers = await execute_raw_query("maint", query, x, y, z)
        result = []
        
        for trigger in triggers:
            if trigger["is_portable"]:
                tag_query = """
                    SELECT n_x, n_y, n_z
                    FROM positionhistory
                    WHERE x_id_dev = $1
                    ORDER BY d_pos_bgn DESC
                    LIMIT 1
                """
                tag_data = await execute_raw_query("hist_r", tag_query, trigger["assigned_tag_id"])
                if tag_data:
                    tag_pos = tag_data[0]
                    center_x, center_y, center_z = tag_pos["n_x"], tag_pos["n_y"], tag_pos["n_z"]
                    radius = trigger["radius_ft"]
                    distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    contains = distance <= radius and (trigger["z_min"] <= z <= trigger["z_max"])
                else:
                    contains = False
            else:
                region_query = """
                    SELECT i_rgn FROM regions WHERE i_trg = $1
                """
                region = await execute_raw_query("maint", region_query, trigger["i_trg"])
                if region:
                    region_id = region[0]["i_rgn"]
                    # Use stored procedure for rounded coordinates
                    vertices = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
                    if len(vertices) >= 3:
                        regions = Region3DCollection()
                        x_coords = [float(v["n_x"]) for v in vertices]
                        y_coords = [float(v["n_y"]) for v in vertices]
                        z_coords = [float(v["n_z"]) for v in vertices]
                        # NEW: Create Region3D with vertices for hybrid containment
                        region_3d = Region3D(
                            min_x=min(x_coords),
                            max_x=max(x_coords),
                            min_y=min(y_coords),
                            max_y=max(y_coords),
                            min_z=min(z_coords),
                            max_z=max(z_coords),
                           vertices=[(float(v["n_x"]), float(v["n_y"]), float(v["n_z"])) for v in vertices]  # This passes tuples  # NEW: Pass vertices for polygon containment
                        )
                        regions.add(region_3d)
                        # NEW: Use hybrid containment instead of basic bounding box
                        contains = any(region.contains_point_hybrid(x, y, z) for region in regions.regions)
                    else:
                        contains = False
                else:
                    contains = False
            
            result.append({
                "trigger_id": trigger["i_trg"],
                "name": trigger["x_nm_trg"],
                "contains": contains
            })
        
        return result
    except DatabaseError as e:
        logger.error(f"Database error fetching triggers by point: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching triggers by point: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint to fetch vertices for a zone (excluding trigger-related regions)
@router.get(
    "/get_zone_vertices/{zone_id}",
    summary="Fetch vertices for a given zone, excluding regions associated with triggers",
    description=load_description("get_zone_vertices"),
    tags=["triggers"]
)
async def get_zone_vertices(zone_id: int):
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
    
# Endpoint to creat a trigger from a zone
@router.post(
    "/add_trigger_from_zone",
    summary="Create a static trigger using all vertices from the specified zone",
    description=load_description("add_trigger_from_zone"),
    tags=["triggers"]
)
async def add_trigger_from_zone(
    name: str = Form(...),
    direction: int = Form(...),
    zone_id: int = Form(...),
    ignore: bool = Form(False)
):
    try:
        # Step 1: Validate zone exists
        zone_check_query = "SELECT i_zn FROM zones WHERE i_zn = $1"
        zone_exists = await execute_raw_query("maint", zone_check_query, zone_id)
        if not zone_exists:
            raise HTTPException(status_code=400, detail=f"Zone {zone_id} does not exist")
        
        # Step 2: Fetch zone region ID
        region_query = """
            SELECT r.i_rgn
            FROM regions r
            WHERE r.i_zn = $1 AND r.i_trg IS NULL
        """
        region_result = await execute_raw_query("maint", region_query, zone_id)
        if not region_result:
            raise HTTPException(status_code=404, detail=f"No region found for zone {zone_id}")
        
        region_id = region_result[0]["i_rgn"]
        
        # Step 3: Use stored procedure for rounded coordinates
        vertices = await call_stored_procedure("maint", "usp_zone_vertices_select_by_region", region_id)
        
        if not vertices:
            raise HTTPException(status_code=404, detail=f"No vertices found for zone {zone_id}")
        
        if len(vertices) < 3:
            raise HTTPException(status_code=400, detail=f"Zone {zone_id} has insufficient vertices ({len(vertices)} found, minimum 3 required)")
        
        logger.info(f"Found {len(vertices)} vertices for zone {zone_id}")
        
        # Step 4: Create trigger request using existing TriggerAddRequest model
        trigger_request = TriggerAddRequest(
            name=str(name),
            direction=int(direction),
            zone_id=int(zone_id),
            ignore=bool(ignore),
            vertices=[{"x": float(v["n_x"]), "y": float(v["n_y"]), "z": float(v["n_z"])} for v in vertices]
        )
        
        # Step 5: Use existing add_trigger logic
        result = await add_trigger(trigger_request)
        
        # Step 6: Enhance response with vertex count
        if isinstance(result, dict) and "trigger_id" in result:
            result["vertices_count"] = len(vertices)
            result["message"] = "Trigger created successfully from zone vertices"
        
        logger.info(f"Successfully created trigger from zone {zone_id} with {len(vertices)} vertices")
        return result
        
    except HTTPException as e:
        # Re-raise HTTP exceptions as-is
        raise e
    except DatabaseError as e:
        logger.error(f"Database error creating trigger from zone {zone_id}: {e.message}")
        if "already exists" in e.message.lower():
            raise HTTPException(status_code=400, detail=f"Trigger name '{name}' already exists. Please choose a different name.")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error creating trigger from zone {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create trigger from zone: {str(e)}")
    
# Endpoint to fetch zone boundaries directly from regions table
@router.get(
    "/get_zone_boundaries/{zone_id}",
    summary="Get zone boundaries directly from the regions table for reliable boundary data",
    description=load_description("get_zone_boundaries"),
    tags=["triggers"]
)
async def get_zone_boundaries(zone_id: int):
    """
    Fetch zone boundaries directly from the regions table instead of calculating from vertices.

    This endpoint retrieves the actual min/max coordinates stored in the regions table,
    which contain the proper Z boundaries (unlike vertices which may all have z=0).
    This is the authoritative source for zone boundary validation during trigger creation.

    Args:
        zone_id (int): The ID of the zone to fetch boundaries for.

    Returns:
        dict: A dictionary containing:
            - zone_id (int): The requested zone ID.
            - min_x (float): Minimum x-coordinate from regions table.
            - max_x (float): Maximum x-coordinate from regions table.
            - min_y (float): Minimum y-coordinate from regions table.
            - max_y (float): Maximum y-coordinate from regions table.
            - min_z (float): Minimum z-coordinate from regions table.
            - max_z (float): Maximum z-coordinate from regions table.
            - region_id (int): The region ID used for the boundaries.
            - region_name (str): The name of the region.

    Raises:
        HTTPException:
            - 404: If no region is found for the zone.
            - 500: For database or unexpected errors.
    """
    try:
        # Fetch the zone's region (excluding trigger regions)
        query = """
            SELECT r.i_rgn, r.x_nm_rgn, r.n_min_x, r.n_max_x, 
                   r.n_min_y, r.n_max_y, r.n_min_z, r.n_max_z
            FROM regions r
            WHERE r.i_zn = $1 AND r.i_trg IS NULL
            LIMIT 1
        """
        region_result = await execute_raw_query("maint", query, zone_id)
        
        if not region_result:
            raise HTTPException(
                status_code=404, 
                detail=f"No region found for zone ID {zone_id}"
            )

        region = region_result[0]
        
        # Return the boundaries directly from the regions table
        return {
            "zone_id": zone_id,
            "min_x": float(region["n_min_x"]),
            "max_x": float(region["n_max_x"]),
            "min_y": float(region["n_min_y"]),
            "max_y": float(region["n_max_y"]),
            "min_z": float(region["n_min_z"]),
            "max_z": float(region["n_max_z"]),
            "region_id": region["i_rgn"],
            "region_name": region["x_nm_rgn"]
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions as-is
        raise e
    except Exception as e:
        logger.error(f"Error fetching zone boundaries for zone {zone_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching zone boundaries: {str(e)}"
        )