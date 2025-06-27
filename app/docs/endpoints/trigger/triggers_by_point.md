# GET /triggers_by_point

**Function:** `triggers_by_point`  
**Source:** `routes/trigger.py` (line 1313)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--triggers_by_point)

---

## Full Documentation

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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/triggers_by_point`
- **Function Name:** `triggers_by_point`
- **Source Location:** Line 1313 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
