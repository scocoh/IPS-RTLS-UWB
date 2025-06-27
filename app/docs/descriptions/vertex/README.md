# Vertex External Descriptions

External description files for `vertex.py` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** 6

## File Structure

Each endpoint has its description in a separate `.txt` file:

- `delete_vertex.txt` - DELETE /delete_vertex/{vertex_id}
- `edit_vertex.txt` - PUT /edit_vertex
- `get_vertex_by_id.txt` - GET /get_vertex_by_id/{vertex_id}
- `list_vertices.txt` - GET /list_vertices
- `add_vertex.txt` - POST /add_vertex
- `update_vertices.txt` - POST /update_vertices


## Usage

The `load_description()` function in `vertex.py` loads these files:

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
Generated on: 2025-06-27 05:28:17  
Conversion approach: External descriptions with load_description()
