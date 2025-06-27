# GET /get_triggers_by_zone/{zone_id}

**Function:** `get_triggers_by_zone`  
**Source:** `routes/trigger.py` (line 932)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--get_triggers_by_zone-zone_id)

---

## Full Documentation

Fetch all triggers associated with a given zone, including direction names.

This endpoint retrieves all triggers linked to a specific zone, along with their direction names, to provide a comprehensive view of triggers within a zone (e.g., a building or area).

Args:
    zone_id (int): The ID of the zone to fetch triggers for (path parameter, required).

Returns:
    list: A list of dictionaries, each containing:
        - trigger_id (int): Trigger ID.
        - name (str): Trigger name.
        - direction_name (str): Name of the trigger direction (e.g., "Entry").
        - zone_id (int): Zone ID.

Raises:
    HTTPException:
        - 500: For database errors or unexpected issues.

Example:
    To fetch triggers for zone ID 417:
    ```
    curl -X GET http://192.168.210.226:8000/get_triggers_by_zone/417
    ```
    Response:
    ```json
    [
        {
            "trigger_id": 123,
            "name": "EntryGate",
            "direction_name": "Entry",
            "zone_id": 417
        }
    ]
    ```

Use Case:
    This endpoint is used to list all triggers in a specific zone for display in the React frontend or for zone-specific trigger management, such as configuring alerts for a building.

Hint:
    - Ensure the zone_id exists in the zones table (maint.zones, i_zn).
    - The direction_name comes from the tlktrigdirections table; verify its data for accuracy.
    - An empty list is returned if no triggers are found, which is valid and does not raise an error.

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/get_triggers_by_zone/{zone_id}`
- **Function Name:** `get_triggers_by_zone`
- **Source Location:** Line 932 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
