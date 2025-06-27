# GET /get_trigger_state/{trigger_id}/{device_id}

**Function:** `get_trigger_state`  
**Source:** `routes/trigger.py` (line 794)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--get_trigger_state-trigger_id-device_id)

---

## Full Documentation

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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/get_trigger_state/{trigger_id}/{device_id}`
- **Function Name:** `get_trigger_state`
- **Source Location:** Line 794 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
