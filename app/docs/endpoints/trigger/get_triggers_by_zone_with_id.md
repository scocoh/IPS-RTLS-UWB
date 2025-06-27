# GET /get_triggers_by_zone_with_id/{zone_id}

**Function:** `get_triggers_by_zone_with_id`  
**Source:** `routes/trigger.py` (line 1003)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--get_triggers_by_zone_with_id-zone_id)

---

## Full Documentation

Fetch all triggers for a given zone, including direction IDs and portable trigger details.

This endpoint retrieves triggers associated with a zone, including their direction IDs and attributes specific to portable triggers (e.g., radius, z bounds). It supports both portable and non-portable triggers.

Args:
    zone_id (int): The ID of the zone to fetch triggers for (path parameter, required).

Returns:
    list: A list of dictionaries, each containing:
        - trigger_id (int): Trigger ID.
        - name (str): Trigger name.
        - direction_id (int): Direction ID.
        - zone_id (int): Zone ID.
        - is_portable (bool): Whether the trigger is portable.
        - assigned_tag_id (str or None): ID of the assigned tag (for portable triggers).
        - radius_ft (float or None): Radius in feet (for portable triggers).
        - z_min (float or None): Minimum z-coordinate (for portable triggers).
        - z_max (float or None): Maximum z-coordinate (for portable triggers).

Raises:
    HTTPException:
        - 500: For database errors or unexpected issues.

Example:
    To fetch triggers for zone ID 417:
    ```
    curl -X GET http://192.168.210.226:8000/get_triggers_by_zone_with_id/417
    ```
    Response:
    ```json
    [
        {
            "trigger_id": 123,
            "name": "EntryGate",
            "direction_id": 1,
            "zone_id": 417,
            "is_portable": false,
            "assigned_tag_id": null,
            "radius_ft": null,
            "z_min": null,
            "z_max": null
        }
    ]
    ```

Use Case:
    This endpoint is used to retrieve detailed trigger information for a zone, including portable trigger specifics, for advanced trigger management or integration with real-time tracking systems.

Hint:
    - Portable triggers may not have a region (i_zn from triggers table is used instead of regions.i_zn).
    - An empty list is returned if no triggers are found, which is valid.
    - Use this endpoint when you need direction_id instead of direction_name (unlike /get_triggers_by_zone).

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/get_triggers_by_zone_with_id/{zone_id}`
- **Function Name:** `get_triggers_by_zone_with_id`
- **Source Location:** Line 1003 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
