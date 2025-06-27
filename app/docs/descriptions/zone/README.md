# Zone External Descriptions

External description files for `zone.py` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** 7

## File Structure

Each endpoint has its description in a separate `.txt` file:

- `get_parents.txt` - GET /get_parents
- `get_children.txt` - GET /get_children/{parent_id}
- `get_map.txt` - GET /get_map/{zone_id}
- `get_map.txt` - HEAD /get_map/{zone_id}
- `get_zone_vertices.txt` - GET /get_zone_vertices/{zone_id}
- `get_zone_types.txt` - GET /get_zone_types
- `get_parent_zones.txt` - GET /get_parent_zones


## Usage

The `load_description()` function in `zone.py` loads these files:

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
Generated on: 2025-06-27 05:19:29  
Conversion approach: External descriptions with load_description()
