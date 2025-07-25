# POST /add_trigger_from_zone

**Function:** `add_trigger_from_zone`  
**Source:** `routes/trigger.py` (line 1501)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#post--add_trigger_from_zone)

---

## Full Documentation

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
    curl -X POST http://192.168.210.226:8000/api/add_trigger_from_zone              -H "Content-Type: application/x-www-form-urlencoded"              -d "name=zone_425_entry&direction=4&zone_id=425&ignore=false"
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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `POST`
- **Endpoint Path:** `/add_trigger_from_zone`
- **Function Name:** `add_trigger_from_zone`
- **Source Location:** Line 1501 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
