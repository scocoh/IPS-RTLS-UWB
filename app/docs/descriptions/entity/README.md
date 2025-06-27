# Entity External Descriptions

External description files for `entity.py` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** 26

## File Structure

Each endpoint has its description in a separate `.txt` file:

- `add_entity.txt` - POST /add_entity
- `list_all_entities.txt` - GET /list_all_entities
- `get_entity_by_id.txt` - GET /get_entity_by_id/{entity_id}
- `get_entities_by_type.txt` - GET /get_entities_by_type/{entity_type}
- `delete_entity.txt` - DELETE /delete_entity/{entity_id}
- `edit_entity.txt` - PUT /edit_entity
- `add_entity_type.txt` - POST /add_entity_type
- `delete_entity_type.txt` - DELETE /delete_entity_type/{type_id}
- `edit_entity_type.txt` - PUT /edit_entity_type
- `list_entity_types.txt` - GET /list_entity_types
- `assign_entity.txt` - POST /assign_entity
- `delete_entity_assignment.txt` - DELETE /delete_entity_assignment/{assignment_id}
- `delete_all_entity_assignments.txt` - DELETE /delete_all_entity_assignments/{entity_id}
- `edit_entity_assignment.txt` - PUT /edit_entity_assignment
- `end_entity_assignment.txt` - POST /end_entity_assignment
- `end_all_entity_assignments.txt` - POST /end_all_entity_assignments/{entity_id}
- `list_entity_assignments.txt` - GET /list_entity_assignments
- `list_entity_assignments_by_child.txt` - GET /list_entity_assignments_by_child/{child_id}
- `list_entity_assignments_by_id.txt` - GET /list_entity_assignments_by_id/{assignment_id}
- `list_entity_assignments_by_parent.txt` - GET /list_entity_assignments_by_parent/{parent_id}
- `list_entity_assignments_by_reason.txt` - GET /list_entity_assignments_by_reason/{reason_id}
- `get_entity_tree.txt` - GET /entitytree/{id}
- `add_assignment_reason.txt` - POST /add_assignment_reason
- `delete_assignment_reason.txt` - DELETE /delete_assignment_reason/{reason_id}
- `edit_assignment_reason.txt` - PUT /edit_assignment_reason
- `list_assignment_reasons.txt` - GET /list_assignment_reasons


## Usage

The `load_description()` function in `entity.py` loads these files:

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
Generated on: 2025-06-27 05:21:18  
Conversion approach: External descriptions with load_description()
