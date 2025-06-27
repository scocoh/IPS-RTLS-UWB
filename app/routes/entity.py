# Name: entity.py
# Version: 0.1.1
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Version 0.1.1 Converted to external descriptions using load_description()
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
routes/entity.py
Entity management endpoints for ParcoRTLS FastAPI application.
// # VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/entity.py 0P.10B.04
// # CHANGED: Fixed syntax errors in get_entity_tree function signature (removed invalid 'odontist'), bumped to 0P.10B.04
// # CHANGED: Fixed syntax errors in get_entity_tree (moe validation), removed invalid 'Decentering' and corrected HTTPException, bumped to 0P.10B.03
// # CHANGED: Enhanced docstrings for all endpoints with detailed descriptions, parameters, returns, examples, use cases, and error handling, bumped to 0P.10B.02
// # CHANGED: Fixed column name in list_entity_types raw query (x_nm_typ to x_dsc_ent), bumped to 0P.10B.01
// # CHANGED: Replaced usp_entity_type_list with raw query to fix 500 error, bumped to 0.1.17
// # CHANGED: Fixed syntax errors by replacing null with None in get_entity_tree, bumped to 0.1.15
// # CHANGED: Added error handling and logging to list_entity_types, bumped to 0.1.14
// # CHANGED: Added tags=["entities"] to APIRouter for Swagger UI grouping, bumped to 0.1.13
// # CHANGED: Added MOE logic to get_entity_tree to alert on eloped progeny tags, bumped to 0.1.12
// # CHANGED: Added location inheritance to get_entity_tree with late binding, bumped to 0.1.11
// # CHANGED: Added duplicate key error handling to add_entity, bumped to 0.1.10
// # CHANGED: Fixed add_entity to handle usp_entity_add return value, bumped to 0.1.9
// # CHANGED: Fixed delete_entity_assignment to handle usp_assign_entity_delete return value, bumped to 0.1.8
// # CHANGED: Fixed get_entity_tree to deduplicate children and tag_ids, bumped to 0.1.7
// # CHANGED: Fixed syntax errors in delete_entity_assignment, kept version at 0.1.6
// # CHANGED: Fixed get_entity_tree to use correct field x_id_chd instead of x_id_ent_chd, bumped to 0.1.6
// # CHANGED: Fixed assign_entity to handle usp_assign_entity_add return value, bumped to 0.1.5
// # CHANGED: Fixed add_assignment_reason to handle usp_assmt_reason_add return value, bumped to 0.1.4
// # CHANGED: Added debugging logs to get_entity_tree to catch TypeError, bumped to 0.1.3
// # CHANGED: Added GET /entitytree/{id} endpoint for recursive entity tree, bumped to 0.1.2
// # CHANGED: Updated imports to use entity_models.py, bumped to 0.1.1
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from entity_models import EntityRequest, EntityTypeRequest, EntityAssignRequest, EntityAssignEndRequest, AssignmentReasonRequest
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)

def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "entity" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter(tags=["entities"])

# Entity Management
@router.post(
    "/add_entity",
    summary="Add a new entity to the ParcoRTLS system",
    description=load_description("add_entity"),
    tags=["triggers"]
)
async def add_entity(request: EntityRequest):
    creation_date = datetime.now()
    update_date = datetime.now()
    try:
        result = await call_stored_procedure(
            "maint", "usp_entity_add",
            request.entity_id, request.entity_type, request.entity_name, creation_date, update_date
        )
        if result and isinstance(result, list) and result:
            return_value = result[0].get("usp_entity_add")
            if return_value == 1:  # Indicates success
                return {"message": "Entity added successfully", "entity_id": request.entity_id}
        raise HTTPException(status_code=500, detail="Failed to add entity")
    except DatabaseError as e:
        logger.error(f"Database error adding entity: {e.message}")
        if "duplicate key value violates unique constraint" in str(e.message):
            raise HTTPException(status_code=400, detail=f"Entity with ID {request.entity_id} already exists")
        raise HTTPException(status_code=500, detail=e.message)

@router.get(
    "/list_all_entities",
    summary="Retrieve a list of all entities in the ParcoRTLS system",
    description=load_description("list_all_entities"),
    tags=["triggers"]
)
async def list_all_entities():
    result = await call_stored_procedure("maint", "usp_entity_all")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entities found")

@router.get(
    "/get_entity_by_id/{entity_id}",
    summary="Retrieve details of a specific entity by its ID",
    description=load_description("get_entity_by_id"),
    tags=["triggers"]
)
async def get_entity_by_id(entity_id: str):
    result = await call_stored_procedure("maint", "usp_entity_by_id", entity_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Entity not found")

@router.get(
    "/get_entities_by_type/{entity_type}",
    summary="Retrieve all entities of a specific type",
    description=load_description("get_entities_by_type"),
    tags=["triggers"]
)
async def get_entities_by_type(entity_type: int):
    result = await call_stored_procedure("maint", "usp_entity_by_type", entity_type)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entities found for this type")

@router.delete(
    "/delete_entity/{entity_id}",
    summary="Delete an entity from the ParcoRTLS system",
    description=load_description("delete_entity"),
    tags=["triggers"]
)
async def delete_entity(entity_id: str):
    result = await call_stored_procedure("maint", "usp_entity_delete", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity")

@router.put(
    "/edit_entity",
    summary="Update an existing entity's details",
    description=load_description("edit_entity"),
    tags=["triggers"]
)
async def edit_entity(request: EntityRequest):
    result = await call_stored_procedure("maint", "usp_entity_edit", request.entity_id, request.entity_type, request.entity_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity")

# Entity Type Management
@router.post(
    "/add_entity_type",
    summary="Add a new entity type to the ParcoRTLS system",
    description=load_description("add_entity_type"),
    tags=["triggers"]
)
async def add_entity_type(request: EntityTypeRequest):
    result = await call_stored_procedure("maint", "usp_entity_type_add", request.type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type added successfully", "type_id": result[0]["i_typ_ent"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add entity type")

@router.delete(
    "/delete_entity_type/{type_id}",
    summary="Delete an entity type from the ParcoRTLS system",
    description=load_description("delete_entity_type"),
    tags=["triggers"]
)
async def delete_entity_type(type_id: str):
    result = await call_stored_procedure("maint", "usp_entity_type_delete", type_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity type")

@router.put(
    "/edit_entity_type",
    summary="Update an existing entity type's details",
    description=load_description("edit_entity_type"),
    tags=["triggers"]
)
async def edit_entity_type(type_id: str, request: EntityTypeRequest):
    result = await call_stored_procedure("maint", "usp_entity_type_edit", type_id, request.type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity type")

@router.get(
    "/list_entity_types",
    summary="Retrieve a list of all entity types in the ParcoRTLS system",
    description=load_description("list_entity_types"),
    tags=["triggers"]
)
async def list_entity_types():
    try:
        query = "SELECT i_typ_ent, x_dsc_ent AS x_nm_typ, d_crt, d_udt FROM public.tlkentitytypes ORDER BY i_typ_ent;"
        result = await execute_raw_query("maint", query)
        logger.info(f"list_entity_types result: {result}")
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No entity types found")
    except DatabaseError as e:
        logger.error(f"Database error in list_entity_types: {e.message}")
        raise HTTPException(status_code=500, detail=f"Database error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error in list_entity_types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Entity Assignment Management
@router.post(
    "/assign_entity",
    summary="Assign a child entity to a parent entity with a reason",
    description=load_description("assign_entity"),
    tags=["triggers"]
)
async def assign_entity(request: EntityAssignRequest):
    result = await call_stored_procedure("maint", "usp_assign_entity_add", request.parent_id, request.child_id, request.reason_id)
    if result and isinstance(result, list) and result:
        assignment_id = result[0].get("usp_assign_entity_add")
        if assignment_id is not None:
            return {"message": "Entity assignment added successfully", "assignment_id": assignment_id}
    raise HTTPException(status_code=500, detail="Failed to assign entity")

@router.delete(
    "/delete_entity_assignment/{assignment_id}",
    summary="Delete a specific entity assignment",
    description=load_description("delete_entity_assignment"),
    tags=["triggers"]
)
async def delete_entity_assignment(assignment_id: int):
    result = await call_stored_procedure("maint", "usp_assign_entity_delete", assignment_id)
    if result and isinstance(result, list) and result:
        return_value = result[0].get("usp_assign_entity_delete")
        if isinstance(return_value, int) and return_value in (0, 1):  # 0 means already deleted, 1 means successfully deleted
            return {"message": "Entity assignment deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity assignment")

@router.delete(
    "/delete_all_entity_assignments/{entity_id}",
    summary="Delete all assignments for a specific entity",
    description=load_description("delete_all_entity_assignments"),
    tags=["triggers"]
)
async def delete_all_entity_assignments(entity_id: str):
    result = await call_stored_procedure("maint", "usp_assign_entity_delete_all", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "All entity assignments deleted successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to delete all entity assignments")

@router.put(
    "/edit_entity_assignment",
    summary="Update an existing entity assignment",
    description=load_description("edit_entity_assignment"),
    tags=["triggers"]
)
async def edit_entity_assignment(assignment_id: int, request: EntityAssignRequest):
    result = await call_stored_procedure("maint", "usp_assign_entity_edit", assignment_id, request.parent_id, request.child_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity assignment")

@router.post(
    "/end_entity_assignment",
    summary="End a specific entity assignment",
    description=load_description("end_entity_assignment"),
    tags=["triggers"]
)
async def end_entity_assignment(request: EntityAssignEndRequest):
    result = await call_stored_procedure("maint", "usp_assign_entity_end", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end entity assignment")

@router.post(
    "/end_all_entity_assignments/{entity_id}",
    summary="End all assignments for a specific entity",
    description=load_description("end_all_entity_assignments"),
    tags=["triggers"]
)
async def end_all_entity_assignments(entity_id: str):
    result = await call_stored_procedure("maint", "usp_assign_entity_end_all", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "All entity assignments ended successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to end all entity assignments")

@router.get(
    "/list_entity_assignments",
    summary="Retrieve a list of all entity assignments",
    description=load_description("list_entity_assignments"),
    tags=["triggers"]
)
async def list_entity_assignments(include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_entity_list", include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found")

@router.get(
    "/list_entity_assignments_by_child/{child_id}",
    summary="Retrieve all assignments for a specific child entity",
    description=load_description("list_entity_assignments_by_child"),
    tags=["triggers"]
)
async def list_entity_assignments_by_child(child_id: str, include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_child", child_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for child")

@router.get(
    "/list_entity_assignments_by_id/{assignment_id}",
    summary="Retrieve details of a specific entity assignment by its ID",
    description=load_description("list_entity_assignments_by_id"),
    tags=["triggers"]
)
async def list_entity_assignments_by_id(assignment_id: int):
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_key", assignment_id)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for ID")

@router.get(
    "/list_entity_assignments_by_parent/{parent_id}",
    summary="Retrieve all assignments for a specific parent entity",
    description=load_description("list_entity_assignments_by_parent"),
    tags=["triggers"]
)
async def list_entity_assignments_by_parent(parent_id: str, include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_parent", parent_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for parent")

@router.get(
    "/list_entity_assignments_by_reason/{reason_id}",
    summary="Retrieve all assignments for a specific reason",
    description=load_description("list_entity_assignments_by_reason"),
    tags=["triggers"]
)
async def list_entity_assignments_by_reason(reason_id: int, include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_reason", reason_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for reason")

# Entity Tree Management
@router.get(
    "/entitytree/{id}",
    summary="Fetch the hierarchical entity tree starting from a given entity ID",
    description=load_description("get_entity_tree"),
    tags=["triggers"]
)
async def get_entity_tree(id: str, location_type: str = "realtime", moe: float = 5.0):
    try:
        # Validate location_type parameter
        valid_location_types = ["realtime", "near_realtime", "historical"]
        if location_type not in valid_location_types:
            raise HTTPException(status_code=400, detail=f"Invalid location_type. Must be one of: {valid_location_types}")

        # Validate moe parameter
        if moe < 0:
            raise HTTPException(status_code=400, detail="Margin of error (moe) must be non-negative")

        # Step 1: Fetch the entity and find the root entity
        logger.debug(f"Fetching entity for ID: {id}")
        entity = await call_stored_procedure("maint", "usp_entity_by_id", id)
        logger.debug(f"Entity result: {entity}")
        if not entity or not isinstance(entity, list) or not entity:
            raise HTTPException(status_code=404, detail="Entity not found")

        # Step 2: Traverse up to find the root entity
        async def find_root_entity(entity_id: str) -> str:
            """Traverse up the entity tree to find the root entity ID."""
            current_id = entity_id
            while True:
                parent_assignments = await call_stored_procedure("maint", "usp_assign_entity_list_by_child", current_id, False)
                if not parent_assignments or not isinstance(parent_assignments, list) or not parent_assignments:
                    return current_id
                parent_id = parent_assignments[0]["x_id_pnt"]
                current_id = parent_id

        root_entity_id = await find_root_entity(id)
        logger.debug(f"Root entity ID: {root_entity_id}")

        # Step 3: Fetch the root entity's tag and location
        root_tag_assignments = await call_stored_procedure("maint", "usp_assign_dev_list_by_entity", root_entity_id, False)
        root_tag_ids = list(set(tag["x_id_dev"] for tag in root_tag_assignments)) if root_tag_assignments and isinstance(root_tag_assignments, list) else []
        logger.debug(f"Root tag IDs: {root_tag_ids}")

        # Fetch location for the first root tag (simulating manager lookup)
        root_location = {"x": None, "y": None, "z_min": 0, "z_max": None}
        if root_tag_ids:
            device_id = root_tag_ids[0]
            logger.debug(f"Fetching location for root tag: {device_id} with location_type: {location_type}")
            device_details = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
            if device_details and isinstance(device_details, list) and device_details:
                device = device_details[0]
                root_location["x"] = float(device["n_moe_x"]) if device["n_moe_x"] is not None else None
                root_location["y"] = float(device["n_moe_y"]) if device["n_moe_y"] is not None else None
                root_location["z_min"] = 0  # Assuming z_min=0 as per discussion
                root_location["z_max"] = float(device["n_moe_z"]) if device["n_moe_z"] is not None else None
            logger.debug(f"Root tag location: {root_location}")
        else:
            logger.warning(f"No tags found for root entity {root_entity_id}")

        # Step 4: Recursively build the entity tree with MOE checks
        async def build_tree(entity_id: str, is_root: bool = False) -> dict:
            logger.debug(f"Building tree for entity ID: {entity_id}")
            # Fetch entity details
            entity = await call_stored_procedure("maint", "usp_entity_by_id", entity_id)
            logger.debug(f"Entity result: {entity}")
            if not entity:
                return None

            entity_data = entity[0]
            logger.debug(f"Entity data: {entity_data}")
            # Fetch associated tag IDs
            logger.debug(f"Fetching device assignments for entity ID: {entity_id}")
            tag_assignments = await call_stored_procedure("maint", "usp_assign_dev_list_by_entity", entity_id, False)
            logger.debug(f"Tag assignments result: {tag_assignments}")
            tag_ids = list(set(tag["x_id_dev"] for tag in tag_assignments)) if tag_assignments and isinstance(tag_assignments, list) else []
            logger.debug(f"Tag IDs: {tag_ids}")

            # Check MOE for this entity's tag (if any)
            alert = None
            if tag_ids and not is_root:  # Skip MOE check for the root entity
                device_id = tag_ids[0]
                logger.debug(f"Checking MOE for tag: {device_id}")
                device_details = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
                if device_details and isinstance(device_details, list) and device_details:
                    device = device_details[0]
                    tag_x = float(device["n_moe_x"]) if device["n_moe_x"] is not None else None
                    tag_y = float(device["n_moe_y"]) if device["n_moe_y"] is not None else None
                    if tag_x is not None and tag_y is not None and root_location["x"] is not None and root_location["y"] is not None:
                        distance = math.sqrt((tag_x - root_location["x"])**2 + (tag_y - root_location["y"])**2)
                        if distance > moe:
                            alert = f"Tag has eloped from parent (distance: {distance:.6f} feet, MOE: {moe} feet)"
                            logger.debug(f"MOE alert for tag {device_id}: {alert}")

            # Fetch children
            logger.debug(f"Fetching child assignments for entity ID: {entity_id}")
            children_assignments = await call_stored_procedure("maint", "usp_assign_entity_list_by_parent", entity_id, False)
            logger.debug(f"Children assignments result: {children_assignments}")
            children = []
            processed_child_ids = set()
            if children_assignments and isinstance(children_assignments, list):
                for assignment in children_assignments:
                    child_id = assignment["x_id_chd"]
                    if child_id not in processed_child_ids:
                        logger.debug(f"Processing child ID: {child_id}")
                        processed_child_ids.add(child_id)
                        child_tree = await build_tree(child_id)
                        if child_tree:
                            children.append(child_tree)

            # Build the entity node
            entity_node = {
                "id": entity_data["x_id_ent"],
                "type_id": entity_data["i_typ_ent"],
                "name": entity_data["x_nm_ent"],
                "created_at": entity_data["d_crt"],
                "updated_at": entity_data["d_udt"],
                "tag_ids": tag_ids,
                "children": children
            }
            # Include alert if applicable
            if alert:
                entity_node["alert"] = alert
            # Include location at the root or for direct child queries
            if is_root or entity_id == id:
                entity_node["location"] = root_location

            return entity_node

        # Build and return the tree
        logger.debug("Building the entity tree")
        tree = await build_tree(id, is_root=(id == root_entity_id))
        logger.debug(f"Final tree: {tree}")
        if not tree:
            raise HTTPException(status_code=404, detail="Failed to build entity tree")
        return tree
    except Exception as e:
        logger.error(f"Error in get_entity_tree for ID {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error building entity tree: {str(e)}")

# Assignment Reason Management
@router.post(
    "/add_assignment_reason",
    summary="Add a new assignment reason to the ParcoRTLS system",
    description=load_description("add_assignment_reason"),
    tags=["triggers"]
)
async def add_assignment_reason(request: AssignmentReasonRequest):
    result = await call_stored_procedure("maint", "usp_assmt_reason_add", request.reason)
    if result and isinstance(result, list) and result:
        reason_id = result[0].get("usp_assmt_reason_add")
        if reason_id is not None:
            return {"message": "Assignment reason added successfully", "reason_id": reason_id}
    raise HTTPException(status_code=500, detail="Failed to add assignment reason")

@router.delete(
    "/delete_assignment_reason/{reason_id}",
    summary="Delete an assignment reason from the ParcoRTLS system",
    description=load_description("delete_assignment_reason"),
    tags=["triggers"]
)
async def delete_assignment_reason(reason_id: int):
    result = await call_stored_procedure("maint", "usp_assmt_reason_delete", reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete assignment reason")

@router.put(
    "/edit_assignment_reason",
    summary="Update an existing assignment reason",
    description=load_description("edit_assignment_reason"),
    tags=["triggers"]
)
async def edit_assignment_reason(reason_id: int, request: AssignmentReasonRequest):
    result = await call_stored_procedure("maint", "usp_assmt_reason_edit", reason_id, request.reason)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit assignment reason")

@router.get(
    "/list_assignment_reasons",
    summary="Retrieve a list of all assignment reasons in the ParcoRTLS system",
    description=load_description("list_assignment_reasons"),
    tags=["triggers"]
)
async def list_assignment_reasons():
    result = await call_stored_procedure("maint", "usp_assmt_reason_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No assignment reasons found")