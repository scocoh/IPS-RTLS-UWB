# Name: entity.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
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

from fastapi import APIRouter, HTTPException
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from entity_models import EntityRequest, EntityTypeRequest, EntityAssignRequest, EntityAssignEndRequest, AssignmentReasonRequest
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)
router = APIRouter(tags=["entities"])

# Entity Management
@router.post("/add_entity")
async def add_entity(request: EntityRequest):
    """
    Add a new entity to the ParcoRTLS system.

    This endpoint creates a new entity (e.g., a person, asset, or group) in the ParcoRTLS system by invoking the `usp_entity_add` stored procedure. It is used to register entities that can be tracked or associated with devices (e.g., tags) or other entities in the system.

    Args:
        request (EntityRequest): The request body containing entity details.
            - entity_id (str): Unique identifier for the entity (e.g., "EMP123"). Required.
            - entity_type (int): The type ID of the entity (e.g., 1 for Employee, 2 for Asset). Required.
            - entity_name (str): Descriptive name of the entity (e.g., "John Doe"). Required.

    Returns:
        dict: A JSON response indicating success and the entity ID.
            - message (str): Success message ("Entity added successfully").
            - entity_id (str): The ID of the newly created entity.

    Raises:
        HTTPException:
            - 400: If the entity ID already exists (duplicate key violation).
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/add_entity" \
             -H "Content-Type: application/json" \
             -d '{"entity_id": "EMP123", "entity_type": 1, "entity_name": "John Doe"}'
        ```
        Response:
        ```json
        {"message": "Entity added successfully", "entity_id": "EMP123"}
        ```

    Use Case:
        - Register a new employee ("John Doe") with ID "EMP123" and type 1 (Employee) to track their location on a campus.
        - Add a new asset (e.g., a medical device) to the system for inventory and location tracking.

    Hint:
        - Ensure the `entity_type` corresponds to a valid type ID from the `tlkentitytypes` table, which can be retrieved using the `/list_entity_types` endpoint.
        - The `entity_id` must be unique across the system to avoid duplicate key errors.
    """
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

@router.get("/list_all_entities")
async def list_all_entities():
    """
    Retrieve a list of all entities in the ParcoRTLS system.

    This endpoint fetches all entities (e.g., employees, assets, groups) from the system by invoking the `usp_entity_all` stored procedure. It is useful for generating reports or populating UI elements like dropdowns.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing entity details.
            - x_id_ent (str): Entity ID.
            - i_typ_ent (int): Entity type ID.
            - x_nm_ent (str): Entity name.
            - d_crt (datetime): Creation date.
            - d_udt (datetime): Last update date.

    Raises:
        HTTPException:
            - 404: If no entities are found in the system.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_all_entities"
        ```
        Response:
        ```json
        [
            {"x_id_ent": "EMP123", "i_typ_ent": 1, "x_nm_ent": "John Doe", "d_crt": "2025-04-26T10:00:00", "d_udt": "2025-04-26T10:00:00"},
            {"x_id_ent": "ASSET456", "i_typ_ent": 2, "x_nm_ent": "Medical Device", "d_crt": "2025-04-25T09:00:00", "d_udt": "2025-04-25T09:00:00"}
        ]
        ```

    Use Case:
        - Populate a dropdown in the React frontend to allow users to select an entity for assignment or tracking.
        - Generate a report of all registered entities for auditing purposes.

    Hint:
        - Use this endpoint sparingly in high-traffic scenarios, as it retrieves all entities. Consider filtering by type or ID for better performance.
    """
    result = await call_stored_procedure("maint", "usp_entity_all")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entities found")

@router.get("/get_entity_by_id/{entity_id}")
async def get_entity_by_id(entity_id: str):
    """
    Retrieve details of a specific entity by its ID.

    This endpoint fetches the details of a single entity (e.g., employee, asset) using the `usp_entity_by_id` stored procedure. It is used to display entity information or verify existence before performing operations like assignments.

    Args:
        entity_id (str): The unique identifier of the entity (e.g., "EMP123"). Required.

    Returns:
        dict: A dictionary containing entity details.
            - x_id_ent (str): Entity ID.
            - i_typ_ent (int): Entity type ID.
            - x_nm_ent (str): Entity name.
            - d_crt (datetime): Creation date.
            - d_udt (datetime): Last update date.

    Raises:
        HTTPException:
            - 404: If the entity with the specified ID is not found.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_entity_by_id/EMP123"
        ```
        Response:
        ```json
        {"x_id_ent": "EMP123", "i_typ_ent": 1, "x_nm_ent": "John Doe", "d_crt": "2025-04-26T10:00:00", "d_udt": "2025-04-26T10:00:00"}
        ```

    Use Case:
        - Display detailed information about an employee ("EMP123") in the React frontend.
        - Verify that an entity exists before assigning it to a device or another entity.

    Hint:
        - Use this endpoint to prefetch entity data before rendering forms or dashboards to reduce latency.
    """
    result = await call_stored_procedure("maint", "usp_entity_by_id", entity_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Entity not found")

@router.get("/get_entities_by_type/{entity_type}")
async def get_entities_by_type(entity_type: int):
    """
    Retrieve all entities of a specific type.

    This endpoint fetches all entities of a given type (e.g., all employees or all assets) using the `usp_entity_by_type` stored procedure. It is useful for filtering entities by their category.

    Args:
        entity_type (int): The type ID of the entities to retrieve (e.g., 1 for Employee, 2 for Asset). Required.

    Returns:
        list: A list of dictionaries, each containing entity details.
            - x_id_ent (str): Entity ID.
            - i_typ_ent (int): Entity type ID.
            - x_nm_ent (str): Entity name.
            - d_crt (datetime): Creation date.
            - d_udt (datetime): Last update date.

    Raises:
        HTTPException:
            - 404: If no entities are found for the specified type.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_entities_by_type/1"
        ```
        Response:
        ```json
        [
            {"x_id_ent": "EMP123", "i_typ_ent": 1, "x_nm_ent": "John Doe", "d_crt": "2025-04-26T10:00:00", "d_udt": "2025-04-26T10:00:00"},
            {"x_id_ent": "EMP456", "i_typ_ent": 1, "x_nm_ent": "Jane Smith", "d_crt": "2025-04-25T09:00:00", "d_udt": "2025-04-25T09:00:00"}
        ]
        ```

    Use Case:
        - List all employees (type ID 1) in a dropdown for assigning tags in the React frontend.
        - Generate a report of all assets (type ID 2) for inventory management.

    Hint:
        - Retrieve valid `entity_type` values from the `/list_entity_types` endpoint to ensure accurate filtering.
    """
    result = await call_stored_procedure("maint", "usp_entity_by_type", entity_type)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entities found for this type")

@router.delete("/delete_entity/{entity_id}")
async def delete_entity(entity_id: str):
    """
    Delete an entity from the ParcoRTLS system.

    This endpoint removes an entity (e.g., employee, asset) from the system using the `usp_entity_delete` stored procedure. It is used to decommission entities that are no longer tracked.

    Args:
        entity_id (str): The unique identifier of the entity to delete (e.g., "EMP123"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Entity deleted successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the entity cannot be deleted (e.g., due to existing assignments).

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_entity/EMP123"
        ```
        Response:
        ```json
        {"message": "Entity deleted successfully"}
        ```

    Use Case:
        - Remove a retired employee ("EMP123") from the system after they leave the organization.
        - Decommission an obsolete asset from the inventory.

    Hint:
        - Ensure all assignments (e.g., device or entity assignments) for the entity are removed using `/delete_all_entity_assignments/{entity_id}` or `/end_all_entity_assignments/{entity_id}` before deletion to avoid database constraints.
    """
    result = await call_stored_procedure("maint", "usp_entity_delete", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity")

@router.put("/edit_entity")
async def edit_entity(request: EntityRequest):
    """
    Update an existing entity's details.

    This endpoint modifies the details of an entity (e.g., name or type) using the `usp_entity_edit` stored procedure. It is used to correct or update entity information.

    Args:
        request (EntityRequest): The request body containing updated entity details.
            - entity_id (str): Unique identifier of the entity to update (e.g., "EMP123"). Required.
            - entity_type (int): The updated type ID of the entity (e.g., 1 for Employee). Required.
            - entity_name (str): The updated name of the entity (e.g., "John Smith"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Entity edited successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the entity cannot be updated.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/edit_entity" \
             -H "Content-Type: application/json" \
             -d '{"entity_id": "EMP123", "entity_type": 1, "entity_name": "John Smith"}'
        ```
        Response:
        ```json
        {"message": "Entity edited successfully"}
        ```

    Use Case:
        - Update an employee's name from "John Doe" to "John Smith" after a legal name change.
        - Change an asset's type after reclassification.

    Hint:
        - Verify the `entity_id` exists using `/get_entity_by_id/{entity_id}` before attempting to update.
        - Ensure the `entity_type` is valid by checking `/list_entity_types`.
    """
    result = await call_stored_procedure("maint", "usp_entity_edit", request.entity_id, request.entity_type, request.entity_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity")

# Entity Type Management
@router.post("/add_entity_type")
async def add_entity_type(request: EntityTypeRequest):
    """
    Add a new entity type to the ParcoRTLS system.

    This endpoint creates a new entity type (e.g., Employee, Asset) using the `usp_entity_type_add` stored procedure. Entity types categorize entities for organizational purposes.

    Args:
        request (EntityTypeRequest): The request body containing the entity type details.
            - type_name (str): The name of the new entity type (e.g., "Employee"). Required.

    Returns:
        dict: A JSON response indicating success and the new type ID.
            - message (str): Success message ("Entity type added successfully").
            - type_id (int or str): The ID of the newly created entity type.

    Raises:
        HTTPException:
            - 500: If the database operation fails or the entity type cannot be added.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/add_entity_type" \
             -H "Content-Type: application/json" \
             -d '{"type_name": "Employee"}'
        ```
        Response:
        ```json
        {"message": "Entity type added successfully", "type_id": 1}
        ```

    Use Case:
        - Add a new entity type ("Patient") to support tracking patients in a hospital campus.
        - Create a custom entity type for a specific use case (e.g., "Vehicle").

    Hint:
        - Check existing types with `/list_entity_types` to avoid duplicating type names.
        - The returned `type_id` can be used when adding entities via `/add_entity`.
    """
    result = await call_stored_procedure("maint", "usp_entity_type_add", request.type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type added successfully", "type_id": result[0]["i_typ_ent"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add entity type")

@router.delete("/delete_entity_type/{type_id}")
async def delete_entity_type(type_id: str):
    """
    Delete an entity type from the ParcoRTLS system.

    This endpoint removes an entity type using the `usp_entity_type_delete` stored procedure. It is used to remove obsolete or unused entity types.

    Args:
        type_id (str): The ID of the entity type to delete (e.g., "1"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Entity type deleted successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the entity type cannot be deleted (e.g., due to existing entities of that type).

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_entity_type/1"
        ```
        Response:
        ```json
        {"message": "Entity type deleted successfully"}
        ```

    Use Case:
        - Remove an obsolete entity type ("Temporary Worker") that is no longer needed.
        - Clean up unused entity types during system maintenance.

    Hint:
        - Ensure no entities are using the `type_id` (check `/get_entities_by_type/{entity_type}`) before deletion to avoid database constraints.
    """
    result = await call_stored_procedure("maint", "usp_entity_type_delete", type_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity type")

@router.put("/edit_entity_type")
async def edit_entity_type(type_id: str, request: EntityTypeRequest):
    """
    Update an existing entity type's details.

    This endpoint modifies the name of an entity type using the `usp_entity_type_edit` stored procedure. It is used to correct or update type names.

    Args:
        type_id (str): The ID of the entity type to update (e.g., "1"). Required.
        request (EntityTypeRequest): The request body containing the updated type details.
            - type_name (str): The updated name of the entity type (e.g., "Staff"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Entity type edited successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the entity type cannot be updated.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/edit_entity_type?type_id=1" \
             -H "Content-Type: application/json" \
             -d '{"type_name": "Staff"}'
        ```
        Response:
        ```json
        {"message": "Entity type edited successfully"}
        ```

    Use Case:
        - Rename an entity type from "Employee" to "Staff" for consistency.
        - Update a type name to better reflect its purpose.

    Hint:
        - Verify the `type_id` exists using `/list_entity_types` before attempting to update.
    """
    result = await call_stored_procedure("maint", "usp_entity_type_edit", type_id, request.type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity type")

@router.get("/list_entity_types")
async def list_entity_types():
    """
    Retrieve a list of all entity types in the ParcoRTLS system.

    This endpoint fetches all entity types (e.g., Employee, Asset) using a raw SQL query on the `tlkentitytypes` table. It is useful for populating UI elements or validating entity type IDs.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing entity type details.
            - i_typ_ent (int): Entity type ID.
            - x_nm_typ (str): Entity type name (aliased as x_dsc_ent in the query).
            - d_crt (datetime): Creation date.
            - d_udt (datetime): Last update date.

    Raises:
        HTTPException:
            - 404: If no entity types are found.
            - 500: If a database error occurs or an unexpected error is encountered.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_entity_types"
        ```
        Response:
        ```json
        [
            {"i_typ_ent": 1, "x_nm_typ": "Employee", "d_crt": "2025-04-26T10:00:00", "d_udt": "2025-04-26T10:00:00"},
            {"i_typ_ent": 2, "x_nm_typ": "Asset", "d_crt": "2025-04-25T09:00:00", "d_udt": "2025-04-25T09:00:00"}
        ]
        ```

    Use Case:
        - Populate a dropdown in the React frontend for selecting entity types when adding a new entity.
        - Validate entity type IDs before creating or updating entities.

    Hint:
        - This endpoint uses a raw query instead of a stored procedure (`usp_entity_type_list`) due to previous stability issues (see version 0.1.16 changelog).
        - Log errors are captured for debugging; check logs if a 500 error occurs.
    """
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
@router.post("/assign_entity")
async def assign_entity(request: EntityAssignRequest):
    """
    Assign a child entity to a parent entity with a reason.

    This endpoint creates a hierarchical relationship between two entities (e.g., assigning an employee to a department) using the `usp_assign_entity_add` stored procedure. It is used to build entity hierarchies for organizational or tracking purposes.

    Args:
        request (EntityAssignRequest): The request body containing assignment details.
            - parent_id (str): The ID of the parent entity (e.g., "DEPT001"). Required.
            - child_id (str): The ID of the child entity (e.g., "EMP123"). Required.
            - reason_id (int): The ID of the assignment reason (e.g., 1 for "Employment"). Required.

    Returns:
        dict: A JSON response indicating success and the assignment ID.
            - message (str): Success message ("Entity assignment added successfully").
            - assignment_id (int): The ID of the newly created assignment.

    Raises:
        HTTPException:
            - 500: If the database operation fails or the assignment cannot be created.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/assign_entity" \
             -H "Content-Type: application/json" \
             -d '{"parent_id": "DEPT001", "child_id": "EMP123", "reason_id": 1}'
        ```
        Response:
        ```json
        {"message": "Entity assignment added successfully", "assignment_id": 101}
        ```

    Use Case:
        - Assign an employee ("EMP123") to a department ("DEPT001") with reason ID 1 ("Employment").
        - Link a medical device to a hospital ward for location tracking.

    Hint:
        - Verify `parent_id` and `child_id` exist using `/get_entity_by_id/{entity_id}` before assigning.
        - Retrieve valid `reason_id` values from `/list_assignment_reasons`.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_add", request.parent_id, request.child_id, request.reason_id)
    if result and isinstance(result, list) and result:
        assignment_id = result[0].get("usp_assign_entity_add")
        if assignment_id is not None:
            return {"message": "Entity assignment added successfully", "assignment_id": assignment_id}
    raise HTTPException(status_code=500, detail="Failed to assign entity")

@router.delete("/delete_entity_assignment/{assignment_id}")
async def delete_entity_assignment(assignment_id: int):
    """
    Delete a specific entity assignment.

    This endpoint removes an entity assignment (e.g., an employee from a department) using the `usp_assign_entity_delete` stored procedure. It is used to dissolve hierarchical relationships.

    Args:
        assignment_id (int): The ID of the assignment to delete (e.g., 101). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Entity assignment deleted successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the assignment cannot be deleted.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_entity_assignment/101"
        ```
        Response:
        ```json
        {"message": "Entity assignment deleted successfully"}
        ```

    Use Case:
        - Remove an employee ("EMP123") from a department ("DEPT001") after a transfer.
        - Dissolve an assignment when an asset is reassigned to another entity.

    Hint:
        - Verify the `assignment_id` exists using `/list_entity_assignments_by_id/{assignment_id}` before deletion.
        - A return value of 0 from the stored procedure indicates the assignment was already deleted, which is treated as success.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_delete", assignment_id)
    if result and isinstance(result, list) and result:
        return_value = result[0].get("usp_assign_entity_delete")
        if isinstance(return_value, int) and return_value in (0, 1):  # 0 means already deleted, 1 means successfully deleted
            return {"message": "Entity assignment deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity assignment")

@router.delete("/delete_all_entity_assignments/{entity_id}")
async def delete_all_entity_assignments(entity_id: str):
    """
    Delete all assignments for a specific entity.

    This endpoint removes all assignments (parent or child) for a given entity using the `usp_assign_entity_delete_all` stored procedure. It is used to clear all hierarchical relationships for an entity.

    Args:
        entity_id (str): The ID of the entity whose assignments are to be deleted (e.g., "EMP123"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("All entity assignments deleted successfully for entity").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the assignments cannot be deleted.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_all_entity_assignments/EMP123"
        ```
        Response:
        ```json
        {"message": "All entity assignments deleted successfully for entity"}
        ```

    Use Case:
        - Clear all assignments for an employee ("EMP123") who has left the organization.
        - Reset assignments for an asset before reassigning it to a new entity.

    Hint:
        - Use this endpoint cautiously, as it removes all assignments for the entity, which may affect tracking or reporting.
        - Verify the `entity_id` exists using `/get_entity_by_id/{entity_id}` before deletion.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_delete_all", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "All entity assignments deleted successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to delete all entity assignments")

@router.put("/edit_entity_assignment")
async def edit_entity_assignment(assignment_id: int, request: EntityAssignRequest):
    """
    Update an existing entity assignment.

    This endpoint modifies an entity assignment (e.g., changing the parent or reason) using the `usp_assign_entity_edit` stored procedure. It is used to update hierarchical relationships.

    Args:
        assignment_id (int): The ID of the assignment to update (e.g., 101). Required.
        request (EntityAssignRequest): The request body containing updated assignment details.
            - parent_id (str): The updated parent entity ID (e.g., "DEPT002"). Required.
            - child_id (str): The updated child entity ID (e.g., "EMP123"). Required.
            - reason_id (int): The updated reason ID (e.g., 2 for "Transfer"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Entity assignment edited successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the assignment cannot be updated.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/edit_entity_assignment?assignment_id=101" \
             -H "Content-Type: application/json" \
             -d '{"parent_id": "DEPT002", "child_id": "EMP123", "reason_id": 2}'
        ```
        Response:
        ```json
        {"message": "Entity assignment edited successfully"}
        ```

    Use Case:
        - Transfer an employee ("EMP123") from one department ("DEPT001") to another ("DEPT002").
        - Update the reason for an asset's assignment after a change in usage.

    Hint:
        - Verify the `assignment_id` exists using `/list_entity_assignments_by_id/{assignment_id}` before updating.
        - Ensure `parent_id`, `child_id`, and `reason_id` are valid using appropriate endpoints.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_edit", assignment_id, request.parent_id, request.child_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity assignment")

@router.post("/end_entity_assignment")
async def end_entity_assignment(request: EntityAssignEndRequest):
    """
    End a specific entity assignment.

    This endpoint marks an entity assignment as ended using the `usp_assign_entity_end` stored procedure. It is used to terminate a hierarchical relationship without deleting it, preserving historical data.

    Args:
        request (EntityAssignEndRequest): The request body containing the assignment ID.
            - assignment_id (int): The ID of the assignment to end (e.g., 101). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Entity assignment ended successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the assignment cannot be ended.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/end_entity_assignment" \
             -H "Content-Type: application/json" \
             -d '{"assignment_id": 101}'
        ```
        Response:
        ```json
        {"message": "Entity assignment ended successfully"}
        ```

    Use Case:
        - End an employee's assignment to a department after they leave the organization.
        - Terminate an asset's assignment to a ward when it is moved to storage.

    Hint:
        - Use this endpoint to maintain historical records instead of deleting assignments with `/delete_entity_assignment/{assignment_id}`.
        - Verify the `assignment_id` exists using `/list_entity_assignments_by_id/{assignment_id}`.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_end", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end entity assignment")

@router.post("/end_all_entity_assignments/{entity_id}")
async def end_all_entity_assignments(entity_id: str):
    """
    End all assignments for a specific entity.

    This endpoint marks all assignments (parent or child) for a given entity as ended using the `usp_assign_entity_end_all` stored procedure. It is used to terminate all hierarchical relationships while preserving historical data.

    Args:
        entity_id (str): The ID of the entity whose assignments are to be ended (e.g., "EMP123"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("All entity assignments ended successfully for entity").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the assignments cannot be ended.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/end_all_entity_assignments/EMP123"
        ```
        Response:
        ```json
        {"message": "All entity assignments ended successfully for entity"}
        ```

    Use Case:
        - End all assignments for an employee ("EMP123") who has retired, preserving historical data.
        - Terminate all assignments for an asset before reassigning it.

    Hint:
        - Use this endpoint instead of `/delete_all_entity_assignments/{entity_id}` if historical data needs to be retained.
        - Verify the `entity_id` exists using `/get_entity_by_id/{entity_id}`.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_end_all", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "All entity assignments ended successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to end all entity assignments")

@router.get("/list_entity_assignments")
async def list_entity_assignments(include_ended: bool = False):
    """
    Retrieve a list of all entity assignments.

    This endpoint fetches all entity assignments (active or ended) using the `usp_assign_entity_list` stored procedure. It is useful for auditing or displaying hierarchical relationships.

    Args:
        include_ended (bool, optional): Whether to include ended assignments. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing assignment details.
            - x_id_pnt (str): Parent entity ID.
            - x_id_chd (str): Child entity ID.
            - i_rsn_assmt (int): Assignment reason ID.
            - d_crt (datetime): Creation date.
            - d_end (datetime, optional): End date (null if active).

    Raises:
        HTTPException:
            - 404: If no assignments are found.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_entity_assignments?include_ended=true"
        ```
        Response:
        ```json
        [
            {"x_id_pnt": "DEPT001", "x_id_chd": "EMP123", "i_rsn_assmt": 1, "d_crt": "2025-04-26T10:00:00", "d_end": null},
            {"x_id_pnt": "DEPT002", "x_id_chd": "EMP456", "i_rsn_assmt": 2, "d_crt": "2025-04-25T09:00:00", "d_end": "2025-04-26T12:00:00"}
        ]
        ```

    Use Case:
        - Display all active assignments in the React frontend for administrative oversight.
        - Generate a report of all assignments, including ended ones, for auditing.

    Hint:
        - Set `include_ended=True` to retrieve historical assignments, useful for tracking changes over time.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_list", include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found")

@router.get("/list_entity_assignments_by_child/{child_id}")
async def list_entity_assignments_by_child(child_id: str, include_ended: bool = False):
    """
    Retrieve all assignments for a specific child entity.

    This endpoint fetches all assignments where the specified entity is the child using the `usp_assign_entity_list_by_child` stored procedure. It is used to view an entity's parent relationships.

    Args:
        child_id (str): The ID of the child entity (e.g., "EMP123"). Required.
        include_ended (bool, optional): Whether to include ended assignments. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing assignment details.
            - x_id_pnt (str): Parent entity ID.
            - x_id_chd (str): Child entity ID.
            - i_rsn_assmt (int): Assignment reason ID.
            - d_crt (datetime): Creation date.
            - d_end (datetime, optional): End date (null if active).

    Raises:
        HTTPException:
            - 404: If no assignments are found for the child entity.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_entity_assignments_by_child/EMP123?include_ended=true"
        ```
        Response:
        ```json
        [
            {"x_id_pnt": "DEPT001", "x_id_chd": "EMP123", "i_rsn_assmt": 1, "d_crt": "2025-04-26T10:00:00", "d_end": null}
        ]
        ```

    Use Case:
        - View all departments an employee ("EMP123") is assigned to.
        - Check the assignment history of an asset to understand its usage.

    Hint:
        - Verify the `child_id` exists using `/get_entity_by_id/{entity_id}` before querying.
        - Use `include_ended=True` for historical analysis.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_child", child_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for child")

@router.get("/list_entity_assignments_by_id/{assignment_id}")
async def list_entity_assignments_by_id(assignment_id: int):
    """
    Retrieve details of a specific entity assignment by its ID.

    This endpoint fetches a single assignment using the `usp_assign_entity_list_by_key` stored procedure. It is used to verify or display details of a specific assignment.

    Args:
        assignment_id (int): The ID of the assignment (e.g., 101). Required.

    Returns:
        list: A list containing a single dictionary with assignment details.
            - x_id_pnt (str): Parent entity ID.
            - x_id_chd (str): Child entity ID.
            - i_rsn_assmt (int): Assignment reason ID.
            - d_crt (datetime): Creation date.
            - d_end (datetime, optional): End date (null if active).

    Raises:
        HTTPException:
            - 404: If the assignment is not found.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_entity_assignments_by_id/101"
        ```
        Response:
        ```json
        [
            {"x_id_pnt": "DEPT001", "x_id_chd": "EMP123", "i_rsn_assmt": 1, "d_crt": "2025-04-26T10:00:00", "d_end": null}
        ]
        ```

    Use Case:
        - Display details of a specific assignment in the React frontend.
        - Verify an assignment before editing or ending it.

    Hint:
        - Use this endpoint to prefetch assignment data before rendering forms.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_key", assignment_id)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for ID")

@router.get("/list_entity_assignments_by_parent/{parent_id}")
async def list_entity_assignments_by_parent(parent_id: str, include_ended: bool = False):
    """
    Retrieve all assignments for a specific parent entity.

    This endpoint fetches all assignments where the specified entity is the parent using the `usp_assign_entity_list_by_parent` stored procedure. It is used to view an entity's child relationships.

    Args:
        parent_id (str): The ID of the parent entity (e.g., "DEPT001"). Required.
        include_ended (bool, optional): Whether to include ended assignments. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing assignment details.
            - x_id_pnt (str): Parent entity ID.
            - x_id_chd (str): Child entity ID.
            - i_rsn_assmt (int): Assignment reason ID.
            - d_crt (datetime): Creation date.
            - d_end (datetime, optional): End date (null if active).

    Raises:
        HTTPException:
            - 404: If no assignments are found for the parent entity.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_entity_assignments_by_parent/DEPT001?include_ended=true"
        ```
        Response:
        ```json
        [
            {"x_id_pnt": "DEPT001", "x_id_chd": "EMP123", "i_rsn_assmt": 1, "d_crt": "2025-04-26T10:00:00", "d_end": null},
            {"x_id_pnt": "DEPT001", "x_id_chd": "EMP456", "i_rsn_assmt": 1, "d_crt": "2025-04-25T09:00:00", "d_end": "2025-04-26T12:00:00"}
        ]
        ```

    Use Case:
        - List all employees assigned to a department ("DEPT001") in the React frontend.
        - View all assets assigned to a ward for inventory management.

    Hint:
        - Verify the `parent_id` exists using `/get_entity_by_id/{entity_id}` before querying.
        - Use `include_ended=True` for historical analysis.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_parent", parent_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for parent")

@router.get("/list_entity_assignments_by_reason/{reason_id}")
async def list_entity_assignments_by_reason(reason_id: int, include_ended: bool = False):
    """
    Retrieve all assignments for a specific reason.

    This endpoint fetches all assignments associated with a given reason using the `usp_assign_entity_list_by_reason` stored procedure. It is used to analyze assignments by their purpose.

    Args:
        reason_id (int): The ID of the assignment reason (e.g., 1 for "Employment"). Required.
        include_ended (bool, optional): Whether to include ended assignments. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing assignment details.
            - x_id_pnt (str): Parent entity ID.
            - x_id_chd (str): Child entity ID.
            - i_rsn_assmt (int): Assignment reason ID.
            - d_crt (datetime): Creation date.
            - d_end (datetime, optional): End date (null if active).

    Raises:
        HTTPException:
            - 404: If no assignments are found for the reason.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_entity_assignments_by_reason/1?include_ended=true"
        ```
        Response:
        ```json
        [
            {"x_id_pnt": "DEPT001", "x_id_chd": "EMP123", "i_rsn_assmt": 1, "d_crt": "2025-04-26T10:00:00", "d_end": null}
        ]
        ```

    Use Case:
        - List all assignments with reason "Employment" for HR reporting.
        - Analyze assignments for a specific reason to understand system usage.

    Hint:
        - Retrieve valid `reason_id` values from `/list_assignment_reasons` before querying.
        - Use `include_ended=True` for comprehensive analysis.
    """
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_reason", reason_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for reason")

# Entity Tree Management
@router.get("/entitytree/{id}")
async def get_entity_tree(id: str, location_type: str = "realtime", moe: float = 5.0):
    """
    Fetch the hierarchical entity tree starting from a given entity ID.

    This endpoint recursively builds a tree of entities starting from the specified entity, including all descendants, associated tags, and location data. It uses multiple stored procedures (e.g., `usp_entity_by_id`, `usp_assign_entity_list_by_parent`) to construct the tree and includes margin of error (MOE) checks to alert on tags that are too far from the root entity's tag. It is critical for visualizing organizational hierarchies and tracking entity locations in the ParcoRTLS system.

    Args:
        id (str): The entity ID to start the tree from (e.g., "DEPT001"). Required.
        location_type (str, optional): Type of location data to fetch ("realtime", "near_realtime", "historical"). Defaults to "realtime".
        moe (float, optional): Margin of error in feet for progeny tags (default 5.0 feet). If a progeny tag's distance from the root exceeds this, an alert is triggered.

    Returns:
        dict: A nested dictionary representing the entity tree.
            - id (str): Entity ID.
            - type_id (int): Entity type ID.
            - name (str): Entity name.
            - created_at (datetime): Creation date.
            - updated_at (datetime): Last update date.
            - tag_ids (list): List of associated tag IDs.
            - children (list): List of child entity nodes (recursive structure).
            - alert (str, optional): Alert message if a tag exceeds the MOE.
            - location (dict, optional): Location data for the root or queried entity.
                - x (float): X-coordinate.
                - y (float): Y-coordinate.
                - z_min (float): Minimum Z-coordinate.
                - z_max (float): Maximum Z-coordinate.

    Raises:
        HTTPException:
            - 400: If `location_type` is invalid or `moe` is negative.
            - 404: If the entity is not found or the tree cannot be built.
            - 500: If an unexpected error occurs during tree construction.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/entitytree/DEPT001?location_type=realtime&moe=5.0"
        ```
        Response:
        ```json
        {
            "id": "DEPT001",
            "type_id": 3,
            "name": "Engineering",
            "created_at": "2025-04-26T10:00:00",
            "updated_at": "2025-04-26T10:00:00",
            "tag_ids": [],
            "children": [
                {
                    "id": "EMP123",
                    "type_id": 1,
                    "name": "John Doe",
                    "created_at": "2025-04-26T10:00:00",
                    "updated_at": "2025-04-26T10:00:00",
                    "tag_ids": ["TAG001"],
                    "children": [],
                    "alert": "Tag has eloped from parent (distance: 10.5 feet, MOE: 5.0 feet)"
                }
            ],
            "location": {"x": 100.0, "y": 200.0, "z_min": 0.0, "z_max": 10.0}
        }
        ```

    Use Case:
        - Visualize the hierarchy of a department ("DEPT001") and its employees in the React frontend, including their tag locations.
        - Check if an employee's tag ("TAG001") is within the expected range of their department's tag for Zone L1 campus tracking.
        - Generate a report of all entities and their locations under a specific root entity.

    Hint:
        - This endpoint is computationally intensive due to recursive queries; use it for specific entities rather than frequently polling large trees.
        - The `moe` parameter is critical for campuses with Zone L1 zones, as it triggers alerts for tags that have "eloped" (moved too far from their expected location).
        - If no tags are assigned to the root entity, location data may be incomplete; ensure tags are assigned using device management endpoints.
        - The `location_type` parameter affects which location data is fetched; use "realtime" for live tracking and "historical" for auditing past locations.
    """
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
@router.post("/add_assignment_reason")
async def add_assignment_reason(request: AssignmentReasonRequest):
    """
    Add a new assignment reason to the ParcoRTLS system.

    This endpoint creates a new reason for entity assignments (e.g., "Employment", "Maintenance") using the `usp_assmt_reason_add` stored procedure. Reasons categorize assignments for reporting and analysis.

    Args:
        request (AssignmentReasonRequest): The request body containing the reason details.
            - reason (str): The name of the assignment reason (e.g., "Employment"). Required.

    Returns:
        dict: A JSON response indicating success and the new reason ID.
            - message (str): Success message ("Assignment reason added successfully").
            - reason_id (int): The ID of the newly created reason.

    Raises:
        HTTPException:
            - 500: If the database operation fails or the reason cannot be added.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/add_assignment_reason" \
             -H "Content-Type: application/json" \
             -d '{"reason": "Employment"}'
        ```
        Response:
        ```json
        {"message": "Assignment reason added successfully", "reason_id": 1}
        ```

    Use Case:
        - Add a new reason ("Transfer") for employee reassignments within departments.
        - Create a reason ("Maintenance") for assigning assets to service teams.

    Hint:
        - Check existing reasons with `/list_assignment_reasons` to avoid duplicating reason names.
        - The returned `reason_id` is used in `/assign_entity` and other assignment endpoints.
    """
    result = await call_stored_procedure("maint", "usp_assmt_reason_add", request.reason)
    if result and isinstance(result, list) and result:
        reason_id = result[0].get("usp_assmt_reason_add")
        if reason_id is not None:
            return {"message": "Assignment reason added successfully", "reason_id": reason_id}
    raise HTTPException(status_code=500, detail="Failed to add assignment reason")

@router.delete("/delete_assignment_reason/{reason_id}")
async def delete_assignment_reason(reason_id: int):
    """
    Delete an assignment reason from the ParcoRTLS system.

    This endpoint removes an assignment reason using the `usp_assmt_reason_delete` stored procedure. It is used to remove obsolete or unused reasons.

    Args:
        reason_id (int): The ID of the reason to delete (e.g., 1). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Assignment reason deleted successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the reason cannot be deleted (e.g., due to existing assignments).

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_assignment_reason/1"
        ```
        Response:
        ```json
        {"message": "Assignment reason deleted successfully"}
        ```

    Use Case:
        - Remove an obsolete reason ("Temporary Assignment") that is no longer needed.
        - Clean up unused reasons during system maintenance.

    Hint:
        - Ensure no assignments use the `reason_id` (check `/list_entity_assignments_by_reason/{reason_id}`) before deletion to avoid database constraints.
    """
    result = await call_stored_procedure("maint", "usp_assmt_reason_delete", reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete assignment reason")

@router.put("/edit_assignment_reason")
async def edit_assignment_reason(reason_id: int, request: AssignmentReasonRequest):
    """
    Update an existing assignment reason.

    This endpoint modifies the name of an assignment reason using the `usp_assmt_reason_edit` stored procedure. It is used to correct or update reason names.

    Args:
        reason_id (int): The ID of the reason to update (e.g., 1). Required.
        request (AssignmentReasonRequest): The request body containing the updated reason details.
            - reason (str): The updated name of the reason (e.g., "Permanent Assignment"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Assignment reason edited successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the reason cannot be updated.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/edit_assignment_reason?reason_id=1" \
             -H "Content-Type: application/json" \
             -d '{"reason": "Permanent Assignment"}'
        ```
        Response:
        ```json
        {"message": "Assignment reason edited successfully"}
        ```

    Use Case:
        - Rename a reason from "Employment" to "Permanent Assignment" for clarity.
        - Update a reason to better reflect its purpose.

    Hint:
        - Verify the `reason_id` exists using `/list_assignment_reasons` before updating.
    """
    result = await call_stored_procedure("maint", "usp_assmt_reason_edit", reason_id, request.reason)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit assignment reason")

@router.get("/list_assignment_reasons")
async def list_assignment_reasons():
    """
    Retrieve a list of all assignment reasons in the ParcoRTLS system.

    This endpoint fetches all assignment reasons (e.g., "Employment", "Maintenance") using the `usp_assmt_reason_list` stored procedure. It is useful for populating UI elements or validating reason IDs.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing reason details.
            - i_rsn_assmt (int): Reason ID.
            - x_rsn_assmt (str): Reason name.
            - d_crt (datetime): Creation date.
            - d_udt (datetime): Last update date.

    Raises:
        HTTPException:
            - 404: If no assignment reasons are found.
            - 500: If the database operation fails.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_assignment_reasons"
        ```
        Response:
        ```json
        [
            {"i_rsn_assmt": 1, "x_rsn_assmt": "Employment", "d_crt": "2025-04-26T10:00:00", "d_udt": "2025-04-26T10:00:00"},
            {"i_rsn_assmt": 2, "x_rsn_assmt": "Maintenance", "d_crt": "2025-04-25T09:00:00", "d_udt": "2025-04-25T09:00:00"}
        ]
        ```

    Use Case:
        - Populate a dropdown in the React frontend for selecting reasons when assigning entities.
        - Validate reason IDs before creating or updating assignments.

    Hint:
        - Use this endpoint to ensure valid `reason_id` values are used in assignment endpoints.
    """
    result = await call_stored_procedure("maint", "usp_assmt_reason_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No assignment reasons found")