# Trigger External Descriptions

External description files for `trigger.py` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** 17

## File Structure

Each endpoint has its description in a separate `.txt` file:

- `fire_trigger.txt` - POST /fire_trigger/{trigger_name}
- `add_trigger.txt` - POST /add_trigger
- `delete_trigger.txt` - DELETE /delete_trigger/{trigger_id}
- `list_triggers.txt` - GET /list_triggers
- `list_newtriggers.txt` - GET /list_newtriggers
- `list_trigger_directions.txt` - GET /list_trigger_directions
- `get_trigger_details.txt` - GET /get_trigger_details/{trigger_id}
- `move_trigger.txt` - PUT /move_trigger/{trigger_id}
- `get_trigger_state.txt` - GET /get_trigger_state/{trigger_id}/{device_id}
- `get_triggers_by_point.txt` - GET /get_triggers_by_point
- `get_triggers_by_zone.txt` - GET /get_triggers_by_zone/{zone_id}
- `get_triggers_by_zone_with_id.txt` - GET /get_triggers_by_zone_with_id/{zone_id}
- `trigger_contains_point.txt` - GET /trigger_contains_point/{trigger_id}
- `zones_by_point.txt` - GET /zones_by_point
- `triggers_by_point.txt` - GET /triggers_by_point
- `get_zone_vertices.txt` - GET /get_zone_vertices/{zone_id}
- `add_trigger_from_zone.txt` - POST /add_trigger_from_zone


## Usage

The `load_description()` function in `trigger.py` loads these files:

```python
@router.post(
    "/endpoint_path",
    summary="Brief summary",
    description=load_description("function_name"),
    tags=["triggers"]
)
```

## Benefits

- ✅ **Reduced file size:** Much easier to work with in editors and AI tools
- ✅ **Maintained functionality:** Swagger UI shows full descriptions
- ✅ **External management:** Descriptions can be edited separately
- ✅ **Version control:** Code changes don't mix with documentation changes

---
Generated on: 2025-06-27 04:56:52  
Conversion approach: External descriptions with load_description()
