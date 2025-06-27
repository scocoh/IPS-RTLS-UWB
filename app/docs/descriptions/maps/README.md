# Maps External Descriptions

External description files for `maps.py` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** 9

## File Structure

Each endpoint has its description in a separate `.txt` file:

- `update_map_name.txt` - POST /update_map_name
- `get_maps.txt` - GET /get_maps
- `get_map.txt` - GET /get_map/{map_id}
- `get_map_data.txt` - GET /get_map_data/{zone_id}
- `add_map.txt` - POST /add_map
- `delete_map.txt` - DELETE /delete_map/{map_id}
- `get_map_metadata.txt` - GET /get_map_metadata/{map_id}
- `update_map_metadata.txt` - PUT /update_map_metadata
- `get_campus_zones.txt` - GET /get_campus_zones/{campus_id}


## Usage

The `load_description()` function in `maps.py` loads these files:

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
Generated on: 2025-06-27 05:30:46  
Conversion approach: External descriptions with load_description()
