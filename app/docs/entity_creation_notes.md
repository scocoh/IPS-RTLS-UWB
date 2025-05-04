# 📁 /docs/entity_creation_notes.md

---

# Entity Creation Notes (ParcoRTLS v0.1.4)

## ✨ Overview

This document summarizes the Entity Management development completed for **ParcoRTLS v0.1.4**.
It includes backend FastAPI CRUD endpoints, recursive entity tree fetching, MOE alerts, and frontend visual tools.

All changes were designed to be:
- Modular and non-breaking
- ADA-compliant (for TBI accessibility)
- Methodical, version-controlled, and clearly documented


## 🔍 Purpose of Entities

Entities model real-world logical groupings of devices (tags) inside ParcoRTLS.
They enable:
- Hierarchical grouping (Parent -> Child -> Grandchild relationships)
- Location inheritance from root tags
- MOE (Margin of Error) alerting if child devices drift too far
- Cleaner historical tracking and playback


## 🔖 Backend Changes

### Location: `/app/routes/entity.py`

Implemented:
- **/api/add_entity**: Create a new entity
- **/api/edit_entity**: Edit an entity's name/type
- **/api/delete_entity**: Delete an entity
- **/api/list_all_entities**: Retrieve all entities
- **/api/assign_entity**: Assign a device to an entity
- **/api/end_entity_assignment**: End an assignment cleanly
- **/api/entitytree/{id}**: Recursively fetch an entity's hierarchy and associated devices

### Key Features:
- Async PostgreSQL access using asyncpg and stored procedures.
- MOE (Margin of Error) logic: distance-based alerts for child devices.
- Location inheritance: root tag locations populate parent entity coordinates.
- Git versioning and in-file changelogs preserved (e.g., `# v0.1.17 - 2025-04-27`).


## 📉 Frontend Changes

### Location: `/app/src/components/`

- **EntityMap.js** (v0.1.1)
  - Leaflet map for displaying devices and entity clusters.

- **EntityMergeDemo.js** (v0.0.9)
  - Drag-and-drop UI allowing users to visually group tags into entities.
  - Merge tags based on proximity or manual selection.


## 📄 Swagger / OpenAPI Improvements

- FastAPI `APIRouter` now uses `tags=["entities"]` for clean grouping.
- Entity endpoints now visible and testable under their own section at `/docs` (Swagger UI).


## 🔧 Next Steps

- Expand frontend Entity Management with full create/edit/delete forms.
- Add WebSocket updates for entity location movements.
- Build Home Assistant integrations based on entity trees.
- Implement historical playback using entity assignments.


## 📆 Version History

- **v0.1.4** - Entity CRUD, Recursive Tree Fetch, MOE Alerts, Frontend Merge Demo


---

# ✅ Summary

Entities in ParcoRTLS now support:
- Creation, editing, and deletion.
- Parent-child device grouping.
- Real-time margin-of-error distance alerts.
- Visual merging of tags into new entities.

This lays a solid foundation for smarter, semantic RTLS workflows moving forward.

