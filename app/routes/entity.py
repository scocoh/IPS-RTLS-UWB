"""
routes/entity.py
Entity management endpoints for ParcoRTLS FastAPI application.
"""

from fastapi import APIRouter, HTTPException
from database.db import call_stored_procedure, DatabaseError
from models import EntityRequest, EntityTypeRequest, EntityAssignRequest, EntityAssignEndRequest, AssignmentReasonRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Entity Management
@router.post("/add_entity")
async def add_entity(request: EntityRequest):
    creation_date = datetime.now()
    update_date = datetime.now()
    try:
        result = await call_stored_procedure(
            "maint", "usp_entity_add",
            request.entity_id, request.entity_type, request.entity_name, creation_date, update_date
        )
        if result and isinstance(result, (int, str)):
            return {"message": "Entity added successfully", "entity_id": result[0]["x_id_ent"] if isinstance(result, list) and result else result}
        raise HTTPException(status_code=500, detail="Failed to add entity")
    except DatabaseError as e:
        logger.error(f"Database error adding entity: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/list_all_entities")
async def list_all_entities():
    result = await call_stored_procedure("maint", "usp_entity_all")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entities found")

@router.get("/get_entity_by_id/{entity_id}")
async def get_entity_by_id(entity_id: str):
    result = await call_stored_procedure("maint", "usp_entity_by_id", entity_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Entity not found")

@router.get("/get_entities_by_type/{entity_type}")
async def get_entities_by_type(entity_type: int):
    result = await call_stored_procedure("maint", "usp_entity_by_type", entity_type)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entities found for this type")

@router.delete("/delete_entity/{entity_id}")
async def delete_entity(entity_id: str):
    result = await call_stored_procedure("maint", "usp_entity_delete", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity")

@router.put("/edit_entity")
async def edit_entity(request: EntityRequest):
    result = await call_stored_procedure("maint", "usp_entity_edit", request.entity_id, request.entity_type, request.entity_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity")

# Entity Type Management
@router.post("/add_entity_type")
async def add_entity_type(request: EntityTypeRequest):
    result = await call_stored_procedure("maint", "usp_entity_type_add", request.type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type added successfully", "type_id": result[0]["i_typ_ent"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add entity type")

@router.delete("/delete_entity_type/{type_id}")
async def delete_entity_type(type_id: str):
    result = await call_stored_procedure("maint", "usp_entity_type_delete", type_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity type")

@router.put("/edit_entity_type")
async def edit_entity_type(type_id: str, request: EntityTypeRequest):
    result = await call_stored_procedure("maint", "usp_entity_type_edit", type_id, request.type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity type")

@router.get("/list_entity_types")
async def list_entity_types():
    result = await call_stored_procedure("maint", "usp_entity_type_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity types found")

# Entity Assignment Management
@router.post("/assign_entity")
async def assign_entity(request: EntityAssignRequest):
    result = await call_stored_procedure("maint", "usp_assign_entity_add", request.parent_id, request.child_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment added successfully", "assignment_id": result[0]["i_asn_ent"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to assign entity")

@router.delete("/delete_entity_assignment/{assignment_id}")
async def delete_entity_assignment(assignment_id: int):
    result = await call_stored_procedure("maint", "usp_assign_entity_delete", assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity assignment")

@router.delete("/delete_all_entity_assignments/{entity_id}")
async def delete_all_entity_assignments(entity_id: str):
    result = await call_stored_procedure("maint", "usp_assign_entity_delete_all", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "All entity assignments deleted successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to delete all entity assignments")

@router.put("/edit_entity_assignment")
async def edit_entity_assignment(assignment_id: int, request: EntityAssignRequest):
    result = await call_stored_procedure("maint", "usp_assign_entity_edit", assignment_id, request.parent_id, request.child_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity assignment")

@router.post("/end_entity_assignment")
async def end_entity_assignment(request: EntityAssignEndRequest):
    result = await call_stored_procedure("maint", "usp_assign_entity_end", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end entity assignment")

@router.post("/end_all_entity_assignments/{entity_id}")
async def end_all_entity_assignments(entity_id: str):
    result = await call_stored_procedure("maint", "usp_assign_entity_end_all", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "All entity assignments ended successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to end all entity assignments")

@router.get("/list_entity_assignments")
async def list_entity_assignments(include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_entity_list", include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found")

@router.get("/list_entity_assignments_by_child/{child_id}")
async def list_entity_assignments_by_child(child_id: str, include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_child", child_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for child")

@router.get("/list_entity_assignments_by_id/{assignment_id}")
async def list_entity_assignments_by_id(assignment_id: int):
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_key", assignment_id)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for ID")

@router.get("/list_entity_assignments_by_parent/{parent_id}")
async def list_entity_assignments_by_parent(parent_id: str, include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_parent", parent_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for parent")

@router.get("/list_entity_assignments_by_reason/{reason_id}")
async def list_entity_assignments_by_reason(reason_id: int, include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_reason", reason_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for reason")

# Assignment Reason Management
@router.post("/add_assignment_reason")
async def add_assignment_reason(request: AssignmentReasonRequest):
    result = await call_stored_procedure("maint", "usp_assmt_reason_add", request.reason)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason added successfully", "reason_id": result[0]["i_rsn"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add assignment reason")

@router.delete("/delete_assignment_reason/{reason_id}")
async def delete_assignment_reason(reason_id: int):
    result = await call_stored_procedure("maint", "usp_assmt_reason_delete", reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete assignment reason")

@router.put("/edit_assignment_reason")
async def edit_assignment_reason(reason_id: int, request: AssignmentReasonRequest):
    result = await call_stored_procedure("maint", "usp_assmt_reason_edit", reason_id, request.reason)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit assignment reason")

@router.get("/list_assignment_reasons")
async def list_assignment_reasons():
    result = await call_stored_procedure("maint", "usp_assmt_reason_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No assignment reasons found")