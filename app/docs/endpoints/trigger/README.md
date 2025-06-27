# Trigger API Documentation

External documentation for `trigger.py` endpoints.

> **Note:** Full docstrings are preserved in the Python source file to maintain FastAPI/Swagger UI integration.
> This documentation provides standalone reference materials.

## Quick Links

- **Live API Documentation:** [Swagger UI](http://192.168.210.226:8000/docs)
- **Source File:** `routes/trigger.py`
- **Total Endpoints:** 17

## Endpoints Overview

| Method | Path | Function | Documentation | Swagger |
|--------|------|----------|---------------|---------|
| POST | `/fire_trigger/{trigger_name}` | `fire_trigger` | [fire_trigger.md](./fire_trigger.md) | [Try it](http://192.168.210.226:8000/docs#post--fire_trigger-trigger_name) |
| POST | `/add_trigger` | `add_trigger` | [add_trigger.md](./add_trigger.md) | [Try it](http://192.168.210.226:8000/docs#post--add_trigger) |
| DELETE | `/delete_trigger/{trigger_id}` | `delete_trigger` | [delete_trigger.md](./delete_trigger.md) | [Try it](http://192.168.210.226:8000/docs#delete--delete_trigger-trigger_id) |
| GET | `/list_triggers` | `list_triggers` | [list_triggers.md](./list_triggers.md) | [Try it](http://192.168.210.226:8000/docs#get--list_triggers) |
| GET | `/list_newtriggers` | `list_newtriggers` | [list_newtriggers.md](./list_newtriggers.md) | [Try it](http://192.168.210.226:8000/docs#get--list_newtriggers) |
| GET | `/list_trigger_directions` | `list_trigger_directions` | [list_trigger_directions.md](./list_trigger_directions.md) | [Try it](http://192.168.210.226:8000/docs#get--list_trigger_directions) |
| GET | `/get_trigger_details/{trigger_id}` | `get_trigger_details` | [get_trigger_details.md](./get_trigger_details.md) | [Try it](http://192.168.210.226:8000/docs#get--get_trigger_details-trigger_id) |
| PUT | `/move_trigger/{trigger_id}` | `move_trigger` | [move_trigger.md](./move_trigger.md) | [Try it](http://192.168.210.226:8000/docs#put--move_trigger-trigger_id) |
| GET | `/get_trigger_state/{trigger_id}/{device_id}` | `get_trigger_state` | [get_trigger_state.md](./get_trigger_state.md) | [Try it](http://192.168.210.226:8000/docs#get--get_trigger_state-trigger_id-device_id) |
| GET | `/get_triggers_by_point` | `get_triggers_by_point` | [get_triggers_by_point.md](./get_triggers_by_point.md) | [Try it](http://192.168.210.226:8000/docs#get--get_triggers_by_point) |
| GET | `/get_triggers_by_zone/{zone_id}` | `get_triggers_by_zone` | [get_triggers_by_zone.md](./get_triggers_by_zone.md) | [Try it](http://192.168.210.226:8000/docs#get--get_triggers_by_zone-zone_id) |
| GET | `/get_triggers_by_zone_with_id/{zone_id}` | `get_triggers_by_zone_with_id` | [get_triggers_by_zone_with_id.md](./get_triggers_by_zone_with_id.md) | [Try it](http://192.168.210.226:8000/docs#get--get_triggers_by_zone_with_id-zone_id) |
| GET | `/trigger_contains_point/{trigger_id}` | `trigger_contains_point` | [trigger_contains_point.md](./trigger_contains_point.md) | [Try it](http://192.168.210.226:8000/docs#get--trigger_contains_point-trigger_id) |
| GET | `/zones_by_point` | `zones_by_point` | [zones_by_point.md](./zones_by_point.md) | [Try it](http://192.168.210.226:8000/docs#get--zones_by_point) |
| GET | `/triggers_by_point` | `triggers_by_point` | [triggers_by_point.md](./triggers_by_point.md) | [Try it](http://192.168.210.226:8000/docs#get--triggers_by_point) |
| GET | `/get_zone_vertices/{zone_id}` | `get_zone_vertices` | [get_zone_vertices.md](./get_zone_vertices.md) | [Try it](http://192.168.210.226:8000/docs#get--get_zone_vertices-zone_id) |
| POST | `/add_trigger_from_zone` | `add_trigger_from_zone` | [add_trigger_from_zone.md](./add_trigger_from_zone.md) | [Try it](http://192.168.210.226:8000/docs#post--add_trigger_from_zone) |


## Documentation Structure

This external documentation approach provides:

### ✅ Preserved Integration
- **FastAPI/Swagger UI:** Full docstrings remain in Python source
- **Interactive Documentation:** Complete API testing interface maintained
- **OpenAPI Schema:** All metadata preserved for client generation

### ✅ External Documentation
- **Standalone Files:** Individual markdown files for each endpoint
- **Cross-References:** Links between markdown and live API documentation
- **Version Control:** Documentation changes tracked separately from code

### ✅ Best of Both Worlds
- **Developers:** Full Swagger UI experience with detailed docstrings
- **Documentation:** Standalone markdown files for wikis, PDFs, etc.
- **Maintenance:** Single source of truth (Python docstrings)

## Usage Examples

### For API Development
Use the [Swagger UI](http://192.168.210.226:8000/docs) for:
- Interactive API testing
- Request/response examples
- Parameter validation
- Authentication testing

### For Documentation
Use these markdown files for:
- Technical documentation
- API reference guides
- Integration planning
- Offline documentation

## Files

- **Python Source:** `routes/trigger.py` (original docstrings preserved)
- **Documentation Directory:** `docs/endpoints/trigger/`
- **Total Documentation Files:** 17 endpoint files + this README

---
Generated on: 2025-06-27 04:20:52  
**Approach:** External documentation with preserved FastAPI integration
