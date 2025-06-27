# Zoneviewer_Routes External Descriptions

External description files for `zoneviewer_routes.py` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** 11

## File Structure

Each endpoint has its description in a separate `.txt` file:

- `get_campus_zones.txt` - GET /get_campus_zones
- `get_map.txt` - GET /get_map/{map_id}
- `get_map_metadata.txt` - GET /get_map_metadata/{map_id}
- `get_map_data.txt` - GET /get_map_data/{map_id}
- `get_maps_with_zone_types.txt` - GET /get_maps_with_zone_types
- `get_all_zones_for_campus.txt` - GET /get_all_zones_for_campus/{campus_id}
- `get_vertices_for_campus.txt` - GET /get_vertices_for_campus/{campus_id}
- `update_vertices.txt` - POST /update_vertices
- `delete_vertex.txt` - DELETE /delete_vertex/{vertex_id}
- `add_vertex.txt` - POST /add_vertex
- `delete_zone_recursive.txt` - DELETE /delete_zone_recursive/{zone_id}


## Usage

The `load_description()` function in `zoneviewer_routes.py` loads these files:

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
Generated on: 2025-06-27 05:26:55  
Conversion approach: External descriptions with load_description()
