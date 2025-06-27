# DELETE /delete_trigger/{trigger_id}

**Function:** `delete_trigger`  
**Source:** `routes/trigger.py` (line 394)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#delete--delete_trigger-trigger_id)

---

## Full Documentation

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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `DELETE`
- **Endpoint Path:** `/delete_trigger/{trigger_id}`
- **Function Name:** `delete_trigger`
- **Source Location:** Line 394 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
