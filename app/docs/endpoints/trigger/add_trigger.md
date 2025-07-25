# POST /add_trigger

**Function:** `add_trigger`  
**Source:** `routes/trigger.py` (line 182)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#post--add_trigger)

---

## Full Documentation

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
    curl -X POST http://192.168.210.226:8000/add_trigger              -H "Content-Type: application/json"              -d '{
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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `POST`
- **Endpoint Path:** `/add_trigger`
- **Function Name:** `add_trigger`
- **Source Location:** Line 182 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
