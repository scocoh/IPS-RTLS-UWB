# GET /get_zone_vertices/{zone_id}

**Function:** `get_zone_vertices`  
**Source:** `routes/trigger.py` (line 1442)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--get_zone_vertices-zone_id)

---

## Full Documentation

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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/get_zone_vertices/{zone_id}`
- **Function Name:** `get_zone_vertices`
- **Source Location:** Line 1442 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
