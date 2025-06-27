# Device External Descriptions

External description files for `device.py` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** 28

## File Structure

Each endpoint has its description in a separate `.txt` file:

- `get_all_devices.txt` - GET /get_all_devices
- `check_device_id.txt` - GET /check_device_id/{device_id}
- `add_device.txt` - POST /add_device
- `edit_device.txt` - PUT /edit_device/{device_id}
- `delete_device.txt` - DELETE /delete_device/{device_id}
- `get_device_by_id.txt` - GET /get_device_by_id/{device_id}
- `get_device_by_type.txt` - GET /get_device_by_type/{device_type}
- `get_out_of_service_devices.txt` - GET /get_out_of_service_devices
- `set_device_end_date.txt` - POST /set_device_end_date
- `remove_device_end_date.txt` - DELETE /remove_device_end_date/{device_id}
- `set_device_state.txt` - PUT /set_device_state
- `add_device_type.txt` - POST /add_device_type
- `delete_device_type.txt` - DELETE /delete_device_type/{type_id}
- `edit_device_type.txt` - PUT /edit_device_type
- `list_device_types.txt` - GET /list_device_types
- `assign_device_to_zone.txt` - POST /assign_device_to_zone
- `delete_device_assignment.txt` - DELETE /delete_device_assignment/{assignment_id}
- `delete_all_device_assignments.txt` - DELETE /delete_all_device_assignments
- `delete_device_assignments_by_entity.txt` - DELETE /delete_device_assignments_by_entity/{entity_id}
- `edit_device_assignment.txt` - PUT /edit_device_assignment
- `end_device_assignment.txt` - POST /end_device_assignment
- `end_all_device_assignments.txt` - POST /end_all_device_assignments
- `list_device_assignments.txt` - GET /list_device_assignments
- `list_device_assignments_by_entity.txt` - GET /list_device_assignments_by_entity/{entity_id}
- `list_device_assignments_by_device.txt` - GET /list_device_assignments_by_device/{device_id}
- `list_device_assignments_by_reason.txt` - GET /list_device_assignments_by_reason/{reason_id}
- `list_zones.txt` - GET /zone_list
- `get_zones_with_maps.txt` - GET /zones_with_maps


## Usage

The `load_description()` function in `device.py` loads these files:

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
Generated on: 2025-06-27 05:13:22  
Conversion approach: External descriptions with load_description()
