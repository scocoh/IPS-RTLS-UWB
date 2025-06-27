# GET /list_triggers

**Function:** `list_triggers`  
**Source:** `routes/trigger.py` (line 477)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--list_triggers)

---

## Full Documentation

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

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/list_triggers`
- **Function Name:** `list_triggers`
- **Source Location:** Line 477 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
