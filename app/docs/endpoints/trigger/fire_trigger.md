# POST /fire_trigger/{trigger_name}

**Function:** `fire_trigger`  
**Source:** `routes/trigger.py` (line 50)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#post--fire_trigger-trigger_name)

---

## Full Documentation

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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `POST`
- **Endpoint Path:** `/fire_trigger/{trigger_name}`
- **Function Name:** `fire_trigger`
- **Source Location:** Line 50 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
