# GET /list_newtriggers

**Function:** `list_newtriggers`  
**Source:** `routes/trigger.py` (line 521)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--list_newtriggers)

---

## Full Documentation

List all triggers with associated zone information (experimental).

This endpoint retrieves all triggers and enriches them with zone IDs and names by joining the triggers, regions, and zones tables. It is an experimental endpoint designed for enhanced trigger management in the ParcoRTLS system.

Args:
    None

Returns:
    list: A list of dictionaries, each containing:
        - i_trg (int): Trigger ID.
        - x_nm_trg (str): Trigger name.
        - Other trigger fields (from usp_trigger_list).
        - zone_id (int or None): Associated zone ID, if any.
        - zone_name (str or None): Associated zone name, if any.

Raises:
    HTTPException:
        - 404: If no triggers are found.
        - 500: For database errors or unexpected issues.

Example:
    To list all triggers with zone information:
    ```
    curl -X GET http://192.168.210.226:8000/list_newtriggers
    ```
    Response:
    ```json
    [
        {
            "i_trg": 123,
            "x_nm_trg": "EntryGate",
            "i_dir": 1,
            "f_ign": false,
            "zone_id": 417,
            "zone_name": "2303251508CL1"
        },
        {
            "i_trg": 124,
            "x_nm_trg": "DoorSensor",
            "i_dir": 2,
            "f_ign": true,
            "zone_id": null,
            "zone_name": null
        }
    ]
    ```

Use Case:
    This endpoint is useful for generating reports or visualizations in the React frontend that show triggers alongside their associated zones, such as mapping triggers to specific buildings or areas.

Hint:
    - This is an experimental endpoint; verify its stability before production use.
    - Triggers without associated regions will have null zone_id and zone_name.
    - Use the zone_id to fetch additional zone details via other endpoints (e.g., /get_zone_vertices).

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/list_newtriggers`
- **Function Name:** `list_newtriggers`
- **Source Location:** Line 521 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
