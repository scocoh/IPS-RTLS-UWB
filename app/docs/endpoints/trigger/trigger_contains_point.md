# GET /trigger_contains_point/{trigger_id}

**Function:** `trigger_contains_point`  
**Source:** `routes/trigger.py` (line 1088)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--trigger_contains_point-trigger_id)

---

## Full Documentation

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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/trigger_contains_point/{trigger_id}`
- **Function Name:** `trigger_contains_point`
- **Source Location:** Line 1088 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
