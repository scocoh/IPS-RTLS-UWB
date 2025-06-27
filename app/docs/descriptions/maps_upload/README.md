# Maps_Upload External Descriptions

External description files for `maps_upload.py` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** 7

## File Structure

Each endpoint has its description in a separate `.txt` file:

- `upload_map.txt` - POST /upload_map
- `get_map_image.txt` - GET /map_image/{map_id}
- `edit_map.txt` - PUT /edit_map/{map_id}
- `delete_map.txt` - DELETE /delete_map/{map_id}
- `get_map_zones.txt` - GET /get_map_zones/{map_id}
- `get_map_regions.txt` - GET /get_map_regions/{map_id}
- `get_map_triggers.txt` - GET /get_map_triggers/{map_id}


## Usage

The `load_description()` function in `maps_upload.py` loads these files:

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
Generated on: 2025-06-27 05:32:02  
Conversion approach: External descriptions with load_description()
