# GET /list_trigger_directions

**Function:** `list_trigger_directions`  
**Source:** `routes/trigger.py` (line 620)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--list_trigger_directions)

---

## Full Documentation

List all available trigger directions in the ParcoRTLS system.

This endpoint retrieves a list of all trigger direction types (e.g., entry, exit) defined in the database, which are used to categorize triggers based on the direction of movement they detect.

Args:
    None

Returns:
    list: A list of dictionaries, each containing:
        - i_dir (int): Direction ID.
        - x_dir (str): Direction name (e.g., "Entry", "Exit").

Raises:
    HTTPException:
        - 404: If no trigger directions are found.
        - 500: For database errors or unexpected issues.

Example:
    To list all trigger directions:
    ```
    curl -X GET http://192.168.210.226:8000/list_trigger_directions
    ```
    Response:
    ```json
    [
        {"i_dir": 1, "x_dir": "Entry"},
        {"i_dir": 2, "x_dir": "Exit"}
    ]
    ```

Use Case:
    This endpoint is used when configuring new triggers (e.g., via /add_trigger) to select a valid direction ID. It can also be used in the React frontend to populate dropdown menus for trigger direction selection.

Hint:
    - Check the tlktrigdirections table (maint.tlktrigdirections) for the full list of direction IDs and names.
    - Cache the results in the frontend if frequently accessed to reduce database load.

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/list_trigger_directions`
- **Function Name:** `list_trigger_directions`
- **Source Location:** Line 620 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
