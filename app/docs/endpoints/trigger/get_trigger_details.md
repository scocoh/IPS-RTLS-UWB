# GET /get_trigger_details/{trigger_id}

**Function:** `get_trigger_details`  
**Source:** `routes/trigger.py` (line 674)  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#get--get_trigger_details-trigger_id)

---

## Full Documentation

Fetch details of a specific trigger, including its region vertices.

This endpoint retrieves the vertices defining the region associated with a given trigger, allowing developers to understand the trigger’s spatial boundaries in the ParcoRTLS system.

Args:
    trigger_id (int): The ID of the trigger to fetch details for (path parameter, required).

Returns:
    dict: A JSON response containing:
        - vertices (list): List of dictionaries with vertex details (x, y, z, n_ord).

Raises:
    HTTPException:
        - 404: If no region is found for the trigger.
        - 500: For database errors or unexpected issues.

Example:
    To fetch details for trigger ID 123:
    ```
    curl -X GET http://192.168.210.226:8000/get_trigger_details/123
    ```
    Response:
    ```json
    {
        "vertices": [
            {"x": 0.0, "y": 0.0, "z": 0.0, "n_ord": 1},
            {"x": 5.0, "y": 0.0, "z": 0.0, "n_ord": 2},
            {"x": 0.0, "y": 5.0, "z": 0.0, "n_ord": 3}
        ]
    }
    ```

Use Case:
    This endpoint is used to retrieve the exact geometry of a trigger’s region for visualization in the React frontend (e.g., rendering the trigger area on a map) or for debugging trigger configurations.

Hint:
    - Ensure the trigger has an associated region (maint.regions, i_trg = trigger_id) to avoid a 404 error.
    - The n_ord field indicates the order of vertices, which is important for rendering polygons correctly.

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `GET`
- **Endpoint Path:** `/get_trigger_details/{trigger_id}`
- **Function Name:** `get_trigger_details`
- **Source Location:** Line 674 in `routes/trigger.py`

---
*Generated from trigger.py on 2025-06-27 04:20:52*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
