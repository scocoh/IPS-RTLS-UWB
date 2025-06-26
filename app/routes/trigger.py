# /home/parcoadmin/parco_fastapi/app/routes/trigger.py
# Name: trigger.py
# Version: 0.1.61
# Created: 971201
# Modified: 250625
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & Temporal Claude
# Description: FastAPI routes for managing triggers in ParcoRTLS
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: FastAPI
# Status: Active
# Dependent: TRUE
#
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

logger = logging.getLogger(__name__)
router = APIRouter(tags=["triggers"])  # Remove "prefix=/api"

# Endpoint to fire a trigger event by its name
@router.post("/fire_trigger/{trigger_name}")
async def fire_trigger(trigger_name: str):
    """
    Fire a trigger event by its name, publishing an MQTT message to notify the ParcoRTLS system.

    This endpoint triggers an event for a specified trigger, identified by its name, ensuring it is linked to a valid region in the ParcoRTLS system. It publishes the trigger event to an MQTT topic, which can be subscribed to by other system components (e.g., for real-time alerts or actions).

    Args:
        trigger_name (str): The name of the trigger to fire (path parameter, required).

    Returns:
        dict: A JSON response containing:
            - message (str): Confirmation message indicating the trigger was fired.
            - trigger_id (int): The ID of the fired trigger.

    Raises:
        HTTPException:
            - 404: If the trigger name is not found in the database.
            - 400: If the trigger has no valid region assigned.
            - 500: For database errors or unexpected issues during execution.

    Example:
        To fire a trigger named "EntryGate":
        ```
        curl -X POST http://192.168.210.226:8000/fire_trigger/EntryGate
        ```
        Response:
        ```json
        {
            "message": "Trigger EntryGate fired successfully",
            "trigger_id": 123
        }
        ```

    Use Case:
        This endpoint is used in scenarios where an external system or user action needs to manually trigger an event in the ParcoRTLS system. For example, firing a trigger when a gate is opened to log the event or notify security systems via MQTT.

    Hint:
        Ensure the MQTT broker (configured via MQTT_BROKER) is running and accessible at the specified hostname. Check the trigger name in the database (maint.triggers table, column x_nm_trg) to avoid 404 errors. This endpoint is useful for testing trigger integrations or simulating events.
    """
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

        # Fetch vertices for the zone's region
        vertices_query = """
            SELECT n_x AS x, n_y AS y, COALESCE(n_z, 0.0) AS z
            FROM vertices
            WHERE i_rgn = $1
        """
        vertices = await execute_raw_query("maint", vertices_query, region_id)
        if not vertices or len(vertices) < 3:
            raise HTTPException(status_code=400, detail=f"Zone ID {zone_id} has insufficient vertices")

        # Calculate bounding box
        min_x = min(v["x"] for v in vertices)
        max_x = max(v["x"] for v in vertices)
        min_y = min(v["y"] for v in vertices)
        max_y = max(v["y"] for v in vertices)
        min_z = min(v["z"] for v in vertices)
        max_z = max(v["z"] for v in vertices)

        return {
            "min_x": min_x, "max_x": max_x,
            "min_y": min_y, "max_y": max_y,
            "min_z": min_z, "max_z": max_z
        }
    except Exception as e:
        logger.error(f"Error fetching bounding box for zone {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching zone bounding box: {str(e)}")

# Endpoint to add a new trigger
@router.post("/add_trigger")
async def add_trigger(request: TriggerAddRequest):
    """
    Add a new trigger to the ParcoRTLS system and assign it to a region with vertices. (if applicable).
    Args:
        request (TriggerAddRequest): A Pydantic model containing:
            - direction (int): The trigger direction ID (required).
            - name (str): The name of the trigger (required, must be unique).
            - ignore (bool): Whether to ignore the trigger (required).
            - zone_id (int): The ID of the zone to associate the trigger with.
            - vertices (list[dict], optional): List of vertex dictionaries with x, y, z coordinates.

    This endpoint creates a new trigger with the specified properties, assigns it to a zone, and defines its region using provided or default vertices. It ensures the trigger’s region is contained within the zone’s boundaries (for non-portable triggers) and stores the region and vertices in the database.

    Args:
        request (TriggerAddRequest): A Pydantic model containing:
            - direction (int): The trigger direction ID (required, references tlktrigdirections table).
            - name (str): The name of the trigger (required, must be unique).
            - ignore (bool): Whether to ignore the trigger for certain operations (required).
            - zone_id (int): The ID of the zone to associate the trigger with (required).
            - vertices (list[dict], optional): List of vertex dictionaries with x, y, z coordinates (e.g., [{"x": 0.0, "y": 0.0, "z": 0.0}, ...]). Must have at least 3 vertices if provided.

    Returns:
        dict: A JSON response containing:
            - message (str): Status message indicating success or partial success (e.g., trigger added but region not assigned).
            - trigger_id (int): The ID of the newly created trigger.
            - region_id (int, optional): The ID of the assigned region, if created.

    Raises:
        HTTPException:
            - 400: If zone_id is missing, the trigger name already exists, vertices are insufficient, or the trigger region is not contained within the zone.
            - 404: If no region is found for the zone.
            - 500: For database errors or unexpected issues.

    Example:
        To add a trigger named "DoorSensor" in zone 417 with custom vertices:
        ```
        curl -X POST http://192.168.210.226:8000/add_trigger \
             -H "Content-Type: application/json" \
             -d '{
                 "direction": 1,
                 "name": "DoorSensor",
                 "ignore": false,
                 "zone_id": 417,
                 "vertices": [
                     {"x": 0.0, "y": 0.0, "z": 0.0},
                     {"x": 5.0, "y": 0.0, "z": 0.0},
                     {"x": 0.0, "y": 5.0, "z": 0.0}
                 ]
             }'
        ```
        Response:
        ```json
        {
            "message": "Trigger added successfully and assigned to a region",
            "trigger_id": 124,
            "region_id": 567
        }
        ```

    Use Case:
        This endpoint is used when setting up new triggers in the ParcoRTLS system, such as defining a trigger for a specific area (e.g., a doorway) within a zone (e.g., a building). For example, a trigger can be added to detect when a tag enters a restricted area, with vertices defining the exact region.

    Hint:
        - Ensure the zone_id exists in the zones table (maint.zones, column i_zn) and has a valid region with at least 3 vertices.
        - If vertices are not provided, a default triangular region is used, which may not suit all use cases. Provide custom vertices for precise trigger regions.
        - Check the tlktrigdirections table for valid direction IDs.
        - For non-portable triggers, the region must be fully contained within the zone’s bounding box to avoid a 400 error.
    """
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
            # Step 3: Fetch zone bounding box for validation
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

            # Step 5: Validate that the trigger is inside the zone
            if (min_x < zone_bbox["min_x"] or max_x > zone_bbox["max_x"] or
                min_y < zone_bbox["min_y"] or max_y > zone_bbox["max_y"] or
                min_z < zone_bbox["min_z"] or max_z > zone_bbox["max_z"]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Trigger region (min: ({min_x}, {min_y}, {min_z}), max: ({max_x}, {max_y}, {max_z})) "
                           f"is not fully contained within zone {zone_id} boundaries "
                           f"(min: ({zone_bbox['min_x']}, {zone_bbox['min_y']}, {zone_bbox['min_z']}), "
                           f"max: ({zone_bbox['max_x']}, {zone_bbox['max_y']}, {zone_bbox['max_z']}))"
                )

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

        # Return response
        message = "Trigger added successfully"
        if zone_id and region_id:
            message += " and assigned to a region"
        response = {"message": message, "trigger_id": trigger_id}
        if region_id:
            response["region_id"] = region_id
        return response

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
    """
    Delete a trigger by its ID, removing associated regions and vertices.

    This endpoint deletes a trigger from the ParcoRTLS system, ensuring that any associated regions and vertices are also removed to maintain database consistency. It checks for the existence of the trigger and handles cases where the trigger or its region does not exist.

    Args:
        trigger_id (int): The ID of the trigger to delete (path parameter, required).

    Returns:
        dict: A JSON response containing:
            - message (str): Confirmation message indicating whether the trigger was deleted or did not exist.

    Raises:
        HTTPException:
            - 500: For database errors or unexpected issues during deletion.

    Example:
        To delete a trigger with ID 123:
        ```
        curl -X DELETE http://192.168.210.226:8000/delete_trigger/123
        ```
        Response:
        ```json
        {
            "message": "Trigger 123 deleted successfully"
        }
        ```

    Use Case:
        This endpoint is used when removing obsolete or incorrectly configured triggers from the system, such as when a physical trigger area (e.g., a doorway sensor) is no longer needed or was set up incorrectly.

    Hint:
        - Verify the trigger_id exists in the triggers table (maint.triggers, column i_trg) to avoid unnecessary calls.
        - The endpoint safely handles cases where the trigger or its region does not exist, returning an appropriate message.
        - Ensure database permissions allow deletion of triggers, regions, and vertices.
    """
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
    """
    List all triggers in the ParcoRTLS system.

    This endpoint retrieves a list of all triggers stored in the database, including their IDs, names, and other attributes. It is useful for auditing or displaying available triggers in the system.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing trigger details (e.g., i_trg, x_nm_trg, i_dir, f_ign).

    Raises:
        HTTPException:
            - 404: If no triggers are found in the database.
            - 500: For database errors or unexpected issues.

    Example:
        To list all triggers:
        ```
        curl -X GET http://192.168.210.226:8000/list_triggers
        ```
        Response:
        ```json
        [
            {"i_trg": 123, "x_nm_trg": "EntryGate", "i_dir": 1, "f_ign": false},
            {"i_trg": 124, "x_nm_trg": "DoorSensor", "i_dir": 2, "f_ign": true}
        ]
        ```

    Use Case:
        This endpoint is used by administrators or developers to retrieve a complete list of triggers for system monitoring, debugging, or integration with the React frontend to display trigger information.

    Hint:
        - The response format depends on the usp_trigger_list stored procedure output. Check the maint.triggers table schema for exact fields.
        - Use this endpoint sparingly in high-traffic systems, as it retrieves all triggers.
    """
    result = await call_stored_procedure("maint", "usp_trigger_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No triggers found")

# Endpoint to list all triggers with zone information
@router.get("/list_newtriggers")
async def list_newtriggers():
    """
    List all triggers with associated zone information (experimental).

    This endpoint retrieves all triggers and enriches them with zone IDs and names by joining the triggers, regions, and zones tables. It is an experimental endpoint designed for enhanced trigger management in the ParcoRTLS system.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing:
            - i_trg (int): Trigger ID.
            - x_nm_trg (str): Trigger name.
            - Other trigger fields (from usp_trigger_list).
            - zone_id (int or None): Associated zone ID, if any.
            - zone_name (str or None): Associated zone name, if any.

    Raises:
        HTTPException:
            - 404: If no triggers are found.
            - 500: For database errors or unexpected issues.

    Example:
        To list all triggers with zone information:
        ```
        curl -X GET http://192.168.210.226:8000/list_newtriggers
        ```
        Response:
        ```json
        [
            {
                "i_trg": 123,
                "x_nm_trg": "EntryGate",
                "i_dir": 1,
                "f_ign": false,
                "zone_id": 417,
                "zone_name": "2303251508CL1"
            },
            {
                "i_trg": 124,
                "x_nm_trg": "DoorSensor",
                "i_dir": 2,
                "f_ign": true,
                "zone_id": null,
                "zone_name": null
            }
        ]
        ```

    Use Case:
        This endpoint is useful for generating reports or visualizations in the React frontend that show triggers alongside their associated zones, such as mapping triggers to specific buildings or areas.

    Hint:
        - This is an experimental endpoint; verify its stability before production use.
        - Triggers without associated regions will have null zone_id and zone_name.
        - Use the zone_id to fetch additional zone details via other endpoints (e.g., /get_zone_vertices).
    """
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
@router.get("/list_trigger_directions")
async def list_trigger_directions():
    """
    List all available trigger directions in the ParcoRTLS system.

    This endpoint retrieves a list of all trigger direction types (e.g., entry, exit) defined in the database, which are used to categorize triggers based on the direction of movement they detect.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing:
            - i_dir (int): Direction ID.
            - x_dir (str): Direction name (e.g., "Entry", "Exit").

    Raises:
        HTTPException:
            - 404: If no trigger directions are found.
            - 500: For database errors or unexpected issues.

    Example:
        To list all trigger directions:
        ```
        curl -X GET http://192.168.210.226:8000/list_trigger_directions
        ```
        Response:
        ```json
        [
            {"i_dir": 1, "x_dir": "Entry"},
            {"i_dir": 2, "x_dir": "Exit"}
        ]
        ```

    Use Case:
        This endpoint is used when configuring new triggers (e.g., via /add_trigger) to select a valid direction ID. It can also be used in the React frontend to populate dropdown menus for trigger direction selection.

    Hint:
        - Check the tlktrigdirections table (maint.tlktrigdirections) for the full list of direction IDs and names.
        - Cache the results in the frontend if frequently accessed to reduce database load.
    """
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
    """
    Fetch details of a specific trigger, including its region vertices.

    This endpoint retrieves the vertices defining the region associated with a given trigger, allowing developers to understand the trigger’s spatial boundaries in the ParcoRTLS system.

    Args:
        trigger_id (int): The ID of the trigger to fetch details for (path parameter, required).

    Returns:
        dict: A JSON response containing:
            - vertices (list): List of dictionaries with vertex details (x, y, z, n_ord).

    Raises:
        HTTPException:
            - 404: If no region is found for the trigger.
            - 500: For database errors or unexpected issues.

    Example:
        To fetch details for trigger ID 123:
        ```
        curl -X GET http://192.168.210.226:8000/get_trigger_details/123
        ```
        Response:
        ```json
        {
            "vertices": [
                {"x": 0.0, "y": 0.0, "z": 0.0, "n_ord": 1},
                {"x": 5.0, "y": 0.0, "z": 0.0, "n_ord": 2},
                {"x": 0.0, "y": 5.0, "z": 0.0, "n_ord": 3}
            ]
        }
        ```

    Use Case:
        This endpoint is used to retrieve the exact geometry of a trigger’s region for visualization in the React frontend (e.g., rendering the trigger area on a map) or for debugging trigger configurations.

    Hint:
        - Ensure the trigger has an associated region (maint.regions, i_trg = trigger_id) to avoid a 404 error.
        - The n_ord field indicates the order of vertices, which is important for rendering polygons correctly.
    """
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
    """
    Move a trigger to a new position in the ParcoRTLS system.

    This endpoint updates the position of a trigger by modifying its coordinates (x, y, z) in the database, typically used for adjusting the location of portable triggers or correcting trigger placements.

    Args:
        trigger_id (int): The ID of the trigger to move (path parameter, required).
        new_x (float): The new x-coordinate (query parameter, required).
        new_y (float): The new y-coordinate (query parameter, required).
        new_z (float): The new z-coordinate (query parameter, required).

    Returns:
        dict: A JSON response containing:
            - message (str): Confirmation message indicating the trigger was moved.

    Raises:
        HTTPException:
            - 500: For database errors, failure to move the trigger, or unexpected issues.

    Example:
        To move trigger ID 123 to position (10.0, 20.0, 0.0):
        ```
        curl -X PUT "http://192.168.210.226:8000/move_trigger/123?new_x=10.0&new_y=20.0&new_z=0.0"
        ```
        Response:
        ```json
        {
            "message": "Trigger 123 moved by (10.0, 20.0, 0.0)"
        }
        ```

    Use Case:
        This endpoint is used to reposition triggers, such as when a portable trigger’s associated tag moves or when a trigger’s initial placement needs correction (e.g., aligning with a new doorway location).

    Hint:
        - Verify the trigger_id exists and is movable (e.g., check is_portable in maint.triggers).
        - The usp_trigger_move stored procedure handles the actual coordinate update; ensure it is correctly implemented.
        - Coordinates should be within the zone’s boundaries for non-portable triggers to avoid logical errors.
    """
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
@router.get("/get_trigger_state/{trigger_id}/{device_id}")
async def get_trigger_state(trigger_id: int, device_id: str):
    """
    Fetch the last known state of a device for a given trigger.

    This endpoint retrieves the most recent state (e.g., inside or outside) of a device (identified by device_id) relative to a specific trigger’s region, useful for tracking device interactions with trigger areas.

    Args:
        trigger_id (int): The ID of the trigger (path parameter, required).
        device_id (str): The ID of the device (path parameter, required).

    Returns:
        dict: A JSON response containing:
            - trigger_id (int): The ID of the trigger.
            - device_id (str): The ID of the device.
            - last_state (str): The last known state (e.g., "inside", "outside").

    Raises:
        HTTPException:
            - 404: If no state data is found for the trigger and device.
            - 500: For database errors or unexpected issues.

    Example:
        To fetch the state of device "TAG001" for trigger ID 123:
        ```
        curl -X GET http://192.168.210.226:8000/get_trigger_state/123/TAG001
        ```
        Response:
        ```json
        {
            "trigger_id": 123,
            "device_id": "TAG001",
            "last_state": "inside"
        }
        ```

    Use Case:
        This endpoint is used to monitor whether a device (e.g., a tag on a person or asset) is currently within a trigger’s region, such as checking if a worker is in a restricted area.

    Hint:
        - Ensure the trigger_id and device_id exist in the trigger_states table (maint.trigger_states).
        - The last_state value depends on the system’s state tracking logic; verify the trigger_states table schema.
        - Use this endpoint in conjunction with /trigger_contains_point for real-time position checks.
    """
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
    """
    Fetch triggers whose regions contain the specified point coordinates.

    This endpoint identifies triggers whose associated regions (defined by vertices) include the given (x, y, z) point. It is used to determine which triggers a device at a specific location might activate.

    Args:
        x (float): The x-coordinate of the point (query parameter, required).
        y (float): The y-coordinate of the point (query parameter, required).
        z (float): The z-coordinate of the point (query parameter, required).

    Returns:
        list: A list of dictionaries, each containing:
            - i_trg (int): Trigger ID.
            - x_nm_trg (str): Trigger name.
            - i_dir (int): Direction ID.
            - f_ign (bool): Ignore flag.
            - i_rgn (int): Region ID.
            - n_x (float): Vertex x-coordinate.
            - n_y (float): Vertex y-coordinate.
            - n_z (float): Vertex z-coordinate.

    Raises:
        HTTPException:
            - 404: If no triggers are found for the point.
            - 500: For database errors or unexpected issues.

    Example:
        To fetch triggers for point (0.0, 0.0, 0.0):
        ```
        curl -X GET "http://192.168.210.226:8000/get_triggers_by_point?x=0.0&y=0.0&z=0.0"
        ```
        Response:
        ```json
        [
            {
                "i_trg": 123,
                "x_nm_trg": "EntryGate",
                "i_dir": 1,
                "f_ign": false,
                "i_rgn": 567,
                "n_x": 0.0,
                "n_y": 0.0,
                "n_z": 0.0
            }
        ]
        ```

    Use Case:
        This endpoint is used to check which triggers a device at a specific location might interact with, such as determining if a tag is within a trigger region for access control or alerts.

    Hint:
        - The query checks exact vertex matches, which may not always return expected results for regions. Consider using /trigger_contains_point for more accurate containment checks.
        - Ensure the point coordinates are within the system’s coordinate system (e.g., matching the units used in maint.vertices).
    """
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
    """
    Fetch all triggers associated with a given zone, including direction names.

    This endpoint retrieves all triggers linked to a specific zone, along with their direction names, to provide a comprehensive view of triggers within a zone (e.g., a building or area).

    Args:
        zone_id (int): The ID of the zone to fetch triggers for (path parameter, required).

    Returns:
        list: A list of dictionaries, each containing:
            - trigger_id (int): Trigger ID.
            - name (str): Trigger name.
            - direction_name (str): Name of the trigger direction (e.g., "Entry").
            - zone_id (int): Zone ID.

    Raises:
        HTTPException:
            - 500: For database errors or unexpected issues.

    Example:
        To fetch triggers for zone ID 417:
        ```
        curl -X GET http://192.168.210.226:8000/get_triggers_by_zone/417
        ```
        Response:
        ```json
        [
            {
                "trigger_id": 123,
                "name": "EntryGate",
                "direction_name": "Entry",
                "zone_id": 417
            }
        ]
        ```

    Use Case:
        This endpoint is used to list all triggers in a specific zone for display in the React frontend or for zone-specific trigger management, such as configuring alerts for a building.

    Hint:
        - Ensure the zone_id exists in the zones table (maint.zones, i_zn).
        - The direction_name comes from the tlktrigdirections table; verify its data for accuracy.
        - An empty list is returned if no triggers are found, which is valid and does not raise an error.
    """
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
@router.get("/get_triggers_by_zone_with_id/{zone_id}")
async def get_triggers_by_zone_with_id(zone_id: int):
    """
    Fetch all triggers for a given zone, including direction IDs and portable trigger details.

    This endpoint retrieves triggers associated with a zone, including their direction IDs and attributes specific to portable triggers (e.g., radius, z bounds). It supports both portable and non-portable triggers.

    Args:
        zone_id (int): The ID of the zone to fetch triggers for (path parameter, required).

    Returns:
        list: A list of dictionaries, each containing:
            - trigger_id (int): Trigger ID.
            - name (str): Trigger name.
            - direction_id (int): Direction ID.
            - zone_id (int): Zone ID.
            - is_portable (bool): Whether the trigger is portable.
            - assigned_tag_id (str or None): ID of the assigned tag (for portable triggers).
            - radius_ft (float or None): Radius in feet (for portable triggers).
            - z_min (float or None): Minimum z-coordinate (for portable triggers).
            - z_max (float or None): Maximum z-coordinate (for portable triggers).

    Raises:
        HTTPException:
            - 500: For database errors or unexpected issues.

    Example:
        To fetch triggers for zone ID 417:
        ```
        curl -X GET http://192.168.210.226:8000/get_triggers_by_zone_with_id/417
        ```
        Response:
        ```json
        [
            {
                "trigger_id": 123,
                "name": "EntryGate",
                "direction_id": 1,
                "zone_id": 417,
                "is_portable": false,
                "assigned_tag_id": null,
                "radius_ft": null,
                "z_min": null,
                "z_max": null
            }
        ]
        ```

    Use Case:
        This endpoint is used to retrieve detailed trigger information for a zone, including portable trigger specifics, for advanced trigger management or integration with real-time tracking systems.

    Hint:
        - Portable triggers may not have a region (i_zn from triggers table is used instead of regions.i_zn).
        - An empty list is returned if no triggers are found, which is valid.
        - Use this endpoint when you need direction_id instead of direction_name (unlike /get_triggers_by_zone).
    """
    try:
        query = """
            SELECT 
                t.i_trg AS trigger_id, 
                t.x_nm_trg AS name, 
                t.i_dir AS direction_id, 
                COALESCE(r.i_zn, t.i_zn) AS zone_id,
                t.is_portable,
                t.assigned_tag_id,
                t.radius_ft,
                t.z_min,
                t.z_max
            FROM public.triggers t
            LEFT JOIN public.regions r ON t.i_trg = r.i_trg
            WHERE COALESCE(r.i_zn, t.i_zn) = $1 OR t.is_portable = true
        """
        result = await execute_raw_query("maint", query, zone_id)
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
@router.get("/trigger_contains_point/{trigger_id}")
async def trigger_contains_point(trigger_id: int, x: float, y: float, z: float = None): # type: ignore
    """
    Check if a point is within a trigger’s region (2D or 3D).

    This endpoint determines whether a given point (x, y, z) is contained within the region of a specified trigger, supporting both portable (radius-based) and non-portable (vertex-based) triggers. For 2D checks, z can be omitted.

    Args:
        trigger_id (int): The ID of the trigger to check (path parameter, required).
        x (float): The x-coordinate of the point (query parameter, required).
        y (float): The y-coordinate of the point (query parameter, required).
        z (float, optional): The z-coordinate of the point (query parameter, optional for 2D checks).

    Returns:
        dict: A JSON response containing:
            - contains (bool): True if the point is within the trigger’s region, False otherwise.

    Raises:
        HTTPException:
            - 404: If the trigger or its region/tag position is not found.
            - 400: If a portable trigger is missing required attributes (radius, z bounds) or the region has insufficient vertices.
            - 500: For database errors or unexpected issues.
    """
    try:
        # Fetch trigger data
        query = """
            SELECT 
                t.i_trg, t.x_nm_trg, t.i_dir, t.is_portable, t.assigned_tag_id,
                t.radius_ft, t.z_min, t.z_max, t.i_zn AS zone_id
            FROM triggers t
            WHERE t.i_trg = $1
        """
        logger.debug(f"Executing query for trigger {trigger_id}: {query}")
        trigger_data = await execute_raw_query("maint", query, trigger_id)
        logger.debug(f"Trigger data result: {trigger_data}")
        if not trigger_data:
            logger.error(f"Trigger {trigger_id} not found in triggers table")
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
        
        trigger = trigger_data[0]
        logger.debug(f"Trigger details: {trigger}")
        
        if trigger["is_portable"]:
            # Portable trigger: Use radius and z bounds
            if not all([trigger["radius_ft"], trigger["z_min"] is not None, trigger["z_max"] is not None]):
                logger.error(f"Portable trigger {trigger_id} missing radius or z bounds: {trigger}")
                raise HTTPException(status_code=400, detail="Portable trigger missing radius or z bounds")
            
            # For portable triggers, we need the position of the assigned tag as the center
            if not trigger["assigned_tag_id"]:
                logger.error(f"Portable trigger {trigger_id} missing assigned tag ID")
                raise HTTPException(status_code=400, detail="Portable trigger missing assigned tag ID")
            
            # The WebSocket server provides x, y, z as the tag’s position (e.g., SIM1’s position)
            # For portable triggers, this position is the center of the trigger
            center_x, center_y, center_z = x, y, z if z is not None else 0
            radius = trigger["radius_ft"]
            
            # Fetch the zone’s vertices to determine a reference point to check against
            # We’ll use the centroid of the zone as the point to check
            zone_id = trigger["zone_id"]
            if not zone_id:
                logger.error(f"Portable trigger {trigger_id} missing zone ID")
                raise HTTPException(status_code=400, detail="Portable trigger missing zone ID")
            
            zone_query = """
                SELECT v.n_x AS x, v.n_y AS y, COALESCE(v.n_z, 0.0) AS z
                FROM vertices v
                JOIN regions r ON v.i_rgn = r.i_rgn
                WHERE r.i_zn = $1 AND r.i_trg IS NULL
                ORDER BY v.n_ord
            """
            zone_vertices = await execute_raw_query("maint", zone_query, zone_id)
            if not zone_vertices:
                logger.error(f"No vertices found for zone {zone_id} of trigger {trigger_id}")
                return {"contains": False}
            
            # Calculate the centroid of the zone as the point to check
            avg_x = sum(v["x"] for v in zone_vertices) / len(zone_vertices)
            avg_y = sum(v["y"] for v in zone_vertices) / len(zone_vertices)
            avg_z = sum(v["z"] for v in zone_vertices) / len(zone_vertices)
            
            # Check if the zone centroid is within the trigger’s radius centered at the tag’s position
            distance = ((avg_x - center_x) ** 2 + (avg_y - center_y) ** 2) ** 0.5
            logger.debug(f"Portable trigger {trigger_id}: distance from zone centroid [{avg_x}, {avg_y}] to tag position [{center_x}, {center_y}] = {distance}, radius = {radius}")
            if z is not None:
                if not (trigger["z_min"] <= z <= trigger["z_max"]):
                    logger.debug(f"Portable trigger {trigger_id}: z={z} outside bounds [{trigger['z_min']}, {trigger['z_max']}]")
                    return {"contains": False}
            contains = distance <= radius
            logger.debug(f"Portable trigger {trigger_id}: contains = {contains}")
            return {"contains": contains}
        else:
            # Non-portable trigger: Fetch region vertices
            region_query = """
                SELECT i_rgn FROM regions WHERE i_trg = $1
            """
            region = await execute_raw_query("maint", region_query, trigger_id)
            if not region:
                logger.error(f"No region found for trigger {trigger_id}")
                raise HTTPException(status_code=404, detail=f"No region found for trigger {trigger_id}")
            region_id = region[0]["i_rgn"]
            
            vertices_query = """
                SELECT n_x AS x, n_y AS y, COALESCE(n_z, 0.0) AS z, n_ord
                FROM vertices
                WHERE i_rgn = $1
                ORDER BY n_ord
            """
            vertices = await execute_raw_query("maint", vertices_query, region_id)
            if len(vertices) < 3:
                logger.error(f"Region for trigger {trigger_id} has insufficient vertices: {len(vertices)}")
                raise HTTPException(status_code=400, detail="Region has insufficient vertices")
            
            regions = Region3DCollection()
            x_coords = [v["x"] for v in vertices]
            y_coords = [v["y"] for v in vertices]
            z_coords = [v["z"] for v in vertices]
            regions.add(Region3D(
                min_x=min(x_coords),
                max_x=max(x_coords),
                min_y=min(y_coords),
                max_y=max(y_coords),
                min_z=min(z_coords),
                max_z=max(z_coords)
            ))
            
            # Check containment
            if z is None:
                contains = any(region.contains_point_in_2d(x, y) for region in regions.regions)
            else:
                contains = any(region.contains_point(x, y, z) for region in regions.regions)
            logger.debug(f"Non-portable trigger {trigger_id}: contains = {contains}")
            return {"contains": contains}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error checking trigger containment: {e}")
        return {"contains": False}  # Return a default response to avoid frontend error
    
# Endpoint to fetch zones that may contain a point
@router.get("/zones_by_point")
async def zones_by_point(x: float, y: float, z: float, zone_type: int = 0):
    """Fetch zones that may contain a given point (x, y, z) based on their bounding box.

    This endpoint retrieves zones whose bounding boxes (defined by regions) contain the specified
    point coordinates. It supports filtering by zone type (e.g., zone_type=1 for Level 1 zones,
    typically campuses). The response includes whether the point is definitively within the zone's
    bounding box.

    Args:
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.
        z (float): The z-coordinate of the point.
        zone_type (int, optional): Filter by zone type (e.g., 1 for Level 1 zones). Defaults to 0 (no filter).

    Returns:
        list: A list of dictionaries containing:
            - zone_id (int): The ID of the zone.
            - zone_name (str): The name of the zone.
            - contains (bool): True if the point is within the zone's bounding box, False otherwise.

    Raises:
        HTTPException: 500 if the database query fails.

    Example:
        To check if a point (x=0, y=0, z=0) is within any Level 1 zones (campuses):
        ```
        GET /api/zones_by_point?x=0&y=0&z=0&zone_type=1
        ```
        Response:
        ```json
        [
            {"zone_id": 417, "zone_name": "2303251508CL1", "contains": true},
            {"zone_id": 419, "zone_name": "ib2503251653cl1", "contains": true}
        ]
        ```

    Hint (Use Case):
        This endpoint can be used to answer questions like "is a tag on campus?" where the tag is identified
        by a tag number (e.g., 'TAG001') and the campus is a bounding box created with a Zone L1 associated
        with a map. To use it for this purpose:
        1. Fetch the tag's position (x, y, z) using `/api/get_recent_device_positions/{device_id}`.
        2. Call this endpoint with the tag's coordinates and `zone_type=1` to filter for Level 1 zones (campuses).
        3. Check the response to see if the specific campus (by zone_id) contains the tag.
        Example: If checking if 'TAG001' is on campus with zone_id=417, fetch its position, then call this endpoint
        and look for zone_id=417 in the response with `"contains": true`."""
    try:
        query = """
            SELECT z.i_zn, z.x_nm_zn, r.n_min_x, r.n_max_x, r.n_min_y, r.n_max_y, r.n_min_z, r.n_max_z
            FROM zones z
            JOIN regions r ON z.i_zn = r.i_zn
            WHERE r.i_trg IS NULL
              AND $1 BETWEEN r.n_min_x AND r.n_max_x
              AND $2 BETWEEN r.n_min_y AND r.n_max_y
              AND $3 BETWEEN r.n_min_z AND r.n_max_z
        """
        if zone_type > 0:
            query += " AND z.i_typ_zn = $4"
            args = (x, y, z, zone_type)
        else:
            args = (x, y, z)
        
        zones = await execute_raw_query("maint", query, *args)
        result = [
            {
                "zone_id": zone["i_zn"],
                "zone_name": zone["x_nm_zn"],
                "contains": (
                    x >= zone["n_min_x"] and x <= zone["n_max_x"] and
                    y >= zone["n_min_y"] and y <= zone["n_max_y"] and
                    z >= zone["n_min_z"] and z <= zone["n_max_z"]
                )
            }
            for zone in zones
        ]
        return result
    except DatabaseError as e:
        logger.error(f"Database error fetching zones by point: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching zones by point: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to fetch triggers that may contain a point
@router.get("/triggers_by_point")
async def triggers_by_point(x: float, y: float, z: float):
    """
    Fetch triggers whose regions may contain a given point (x, y, z).

    This endpoint identifies triggers (both portable and non-portable) whose regions or bounding areas contain the specified point coordinates. It checks portable triggers using their radius and z bounds and non-portable triggers using their region vertices.

    Args:
        x (float): The x-coordinate of the point (query parameter, required).
        y (float): The y-coordinate of the point (query parameter, required).
        z (float): The z-coordinate of the point (query parameter, required).

    Returns:
        list: A list of dictionaries, each containing:
            - trigger_id (int): Trigger ID.
            - name (str): Trigger name.
            - contains (bool): True if the point is within the trigger’s region, False otherwise.

    Raises:
        HTTPException:
            - 500: For database errors or unexpected issues.

    Example:
        To fetch triggers for point (0.0, 0.0, 0.0):
        ```
        curl -X GET "http://192.168.210.226:8000/triggers_by_point?x=0.0&y=0.0&z=0.0"
        ```
        Response:
        ```json
        [
            {
                "trigger_id": 123,
                "name": "EntryGate",
                "contains": true
            }
        ]
        ```

    Use Case:
        This endpoint is used to determine which triggers a device at a specific location might activate, such as checking if a tag is within multiple trigger regions for access control or safety alerts.

    Hint:
        - For portable triggers, ensure the assigned_tag_id has recent position data (hist_r.positionhistory).
        - Non-portable triggers require at least 3 vertices for valid containment checks.
        - Use this endpoint with /get_recent_device_positions to check real-time tag positions against multiple triggers.
        - The containment check is more precise than /get_triggers_by_point, as it evaluates the full region geometry.
    """
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
                    vertices_query = """
                        SELECT n_x AS x, n_y AS y, COALESCE(n_z, 0.0) AS z, n_ord
                        FROM vertices
                        WHERE i_rgn = $1
                        ORDER BY n_ord
                    """
                    vertices = await execute_raw_query("maint", vertices_query, region_id)
                    if len(vertices) >= 3:
                        regions = Region3DCollection()
                        x_coords = [v["x"] for v in vertices]
                        y_coords = [v["y"] for v in vertices]
                        z_coords = [v["z"] for v in vertices]
                        regions.add(Region3D(
                            min_x=min(x_coords),
                            max_x=max(x_coords),
                            min_y=min(y_coords),
                            max_y=max(y_coords),
                            min_z=min(z_coords),
                            max_z=max(z_coords)
                        ))
                        contains = any(region.contains_point(x, y, z) for region in regions.regions)
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
@router.get("/get_zone_vertices/{zone_id}")
async def get_zone_vertices(zone_id: int):
    """
    Fetch vertices for a given zone, excluding regions associated with triggers.

    This endpoint retrieves the vertices defining a zone’s region (not trigger regions), useful for rendering the zone’s geometry in the ParcoRTLS system.

    Args:
        zone_id (int): The ID of the zone to fetch vertices for (path parameter, required).

    Returns:
        dict: A JSON response containing:
            - vertices (list): List of dictionaries with vertex details (e.g., n_x, n_y, n_z, n_ord).

    Raises:
        HTTPException:
            - 500: For database errors or unexpected issues.

    Example:
        To fetch vertices for zone ID 417:
        ```
        curl -X GET http://192.168.210.226:8000/get_zone_vertices/417
        ```
        Response:
        ```json
        {
            "vertices": [
                {"n_x": 0.0, "n_y": 0.0, "n_z": 0.0, "n_ord": 1},
                {"n_x": 100.0, "n_y": 0.0, "n_z": 0.0, "n_ord": 2},
                {"n_x": 0.0, "n_y": 100.0, "n_z": 0.0, "n_ord": 3}
            ]
        }
        ```

    Use Case:
        This endpoint is used to retrieve zone geometry for visualization in the React frontend, such as rendering a building’s boundaries on a map, excluding trigger-specific regions.

    Hint:
        - Ensure the zone_id has a region without a trigger association (maint.regions, i_trg IS NULL).
        - The n_ord field indicates vertex order, critical for correct polygon rendering.
        - Use this endpoint with /get_trigger_details to compare zone and trigger geometries.
    """
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
@router.post("/add_trigger_from_zone")
async def add_trigger_from_zone(
    name: str = Form(...),
    direction: int = Form(...),
    zone_id: int = Form(...),
    ignore: bool = Form(False)
):
    """
    Create a static trigger using all vertices from the specified zone.
    
    This endpoint automatically fetches the zone's vertices and creates a static trigger
    that covers the entire zone area. It's designed for converting TETSE rules to triggers
    where you want the trigger to match the zone boundaries exactly.
    
    Args:
        name (str): Name of the trigger (required, must be unique).
        direction (int): Trigger direction ID (required, references tlktrigdirections table).
        zone_id (int): Zone ID to copy vertices from (required).
        ignore (bool): Whether to ignore the trigger for certain operations (optional, defaults to False).
    
    Returns:
        dict: A JSON response containing:
            - message (str): Status message indicating success.
            - trigger_id (int): The ID of the newly created trigger.
            - region_id (int): The ID of the assigned region.
            - vertices_count (int): Number of vertices copied from the zone.
    
    Raises:
        HTTPException:
            - 400: If zone_id doesn't exist, has insufficient vertices, or trigger name already exists.
            - 404: If no vertices are found for the zone.
            - 500: For database errors or unexpected issues.
    
    Example:
        To create a trigger that covers the entire zone 425:
        ```
        curl -X POST http://192.168.210.226:8000/api/add_trigger_from_zone \
             -H "Content-Type: application/x-www-form-urlencoded" \
             -d "name=zone_425_entry&direction=4&zone_id=425&ignore=false"
        ```
        Response:
        ```json
        {
            "message": "Trigger created successfully from zone vertices",
            "trigger_id": 162,
            "region_id": 489,
            "vertices_count": 15
        }
        ```
    
    Use Case:
        This endpoint is specifically designed for TETSE rule conversion where you need
        to create static triggers that exactly match zone boundaries. It eliminates the
        need for frontend coordinate calculations and ensures trigger regions are always
        valid within their parent zone.
    
    Hint:
        - The endpoint fetches vertices from the zone's region (where i_trg IS NULL).
        - Vertices are automatically sorted by n_ord to maintain proper polygon order.
        - The trigger region will have the same boundaries as the source zone.
        - Use direction=4 (OnEnter) for zone entry monitoring conversions.
    """
    try:
        # Step 1: Validate zone exists
        zone_check_query = "SELECT i_zn FROM zones WHERE i_zn = $1"
        zone_exists = await execute_raw_query("maint", zone_check_query, zone_id)
        if not zone_exists:
            raise HTTPException(status_code=400, detail=f"Zone {zone_id} does not exist")
        
        # Step 2: Fetch zone vertices
        vertices_query = """
            SELECT v.n_x AS x, v.n_y AS y, COALESCE(v.n_z, 0.0) AS z, v.n_ord
            FROM vertices v
            JOIN regions r ON v.i_rgn = r.i_rgn
            WHERE r.i_zn = $1 AND r.i_trg IS NULL
            ORDER BY v.n_ord
        """
        vertices = await execute_raw_query("maint", vertices_query, zone_id)
        
        if not vertices:
            raise HTTPException(status_code=404, detail=f"No vertices found for zone {zone_id}")
        
        if len(vertices) < 3:
            raise HTTPException(status_code=400, detail=f"Zone {zone_id} has insufficient vertices ({len(vertices)} found, minimum 3 required)")
        
        logger.info(f"Found {len(vertices)} vertices for zone {zone_id}")
        
        # Step 3: Create trigger request using existing TriggerAddRequest model
        trigger_request = TriggerAddRequest(
            name=str(name),
            direction=int(direction),
            zone_id=int(zone_id),
            ignore=bool(ignore),
            vertices=[{"x": float(v["x"]), "y": float(v["y"]), "z": float(v["z"])} for v in vertices]
        )
        
        # Step 4: Use existing add_trigger logic
        result = await add_trigger(trigger_request)
        
        # Step 5: Enhance response with vertex count
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
            raise HTTPException(status_code=400, detail=f"Trigger name '{name}' already exists")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error creating trigger from zone {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create trigger from zone: {str(e)}")