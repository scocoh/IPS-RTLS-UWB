# PUT /move_trigger/{trigger_id}

**Function:** `move_trigger`  
**Source:** `routes/trigger.py` (line 740)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#put--move_trigger-trigger_id)

---

## Full Documentation

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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `PUT`
- **Endpoint Path:** `/move_trigger/{trigger_id}`
- **Function Name:** `move_trigger`
- **Source Location:** Line 740 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
