# Name: device.py
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
routes/device.py
Device management endpoints for ParcoRTLS FastAPI application.
// # VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/device.py 0P.10B.03
// # CHANGED: Fixed unterminated string literal in get_zones_with_maps docstring, completed JSON example, bumped to 0P.10B.03
// # CHANGED: Enhanced docstrings for all endpoints with detailed descriptions, parameters, returns, examples, use cases, and error handling, bumped to 0P.10B.02
// # CHANGED: Modified get_device_by_type and list_device_assignments_by_entity to return empty list instead of 404, bumped to 0.1.38
// # CHANGED: Added tags=["devices"] to APIRouter for Swagger UI grouping, bumped to 0.1.37
// # CHANGED: Fixed delete_device_assignment to handle usp_assign_dev_delete return value, bumped to 0.1.36
// # CHANGED: Fixed delete_device_assignment to use path parameter instead of body, bumped to 0.1.35
// # CHANGED: Updated assign_device_to_zone to use usp_assign_dev_list_by_id instead of usp_assign_dev_list_by_device, bumped to 0.1.34
// # CHANGED: Fixed assign_device_to_zone to handle usp_assign_dev_add return value, bumped to 0.1.33
// # CHANGED: Reverted add_device to accept multipart/form-data using Form parameters, bumped to 0.1.32
// # CHANGED: Updated add_device to accept JSON body using DeviceAddRequest, bumped to 0.1.31
// # CHANGED: Bumped version from 0.1.29 to 0.1.30 to fix handling of usp_device_type_delete return value
// Device management endpoints for ParcoRTLS FastAPI application.
//
// ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// Invented by Scott Cohen & Bertrand Dugal.
// Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
//
// Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from models import DeviceAddRequest, DeviceStateRequest, DeviceTypeRequest, DeviceEndDateRequest, AssignDeviceRequest, AssignDeviceDeleteRequest, AssignDeviceEditRequest, AssignDeviceEndRequest
from datetime import datetime
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "device" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter(tags=["devices"])

@router.get(
    "/get_all_devices",
    summary="Retrieve a list of all devices in the ParcoRTLS system, including their associated zone IDs",
    description=load_description("get_all_devices"),
    tags=["triggers"]
)
async def get_all_devices():
    try:
        devices_data = await execute_raw_query(
            "maint",
            "SELECT x_id_dev, i_typ_dev, x_nm_dev, n_moe_x, n_moe_y, n_moe_z, zone_id FROM devices"
        )
        # Ensure devices_data is a list; fallback to [] if not
        if not isinstance(devices_data, list):
            logger.warning(f"execute_raw_query returned non-list type: {type(devices_data)}. Forcing to empty list.")
            devices_data = []
        
        # Format the response to match frontend expectations
        response = [
            {
                "x_id_dev": d["x_id_dev"],
                "i_typ_dev": d["i_typ_dev"],
                "x_nm_dev": d["x_nm_dev"],
                "n_moe_x": float(d["n_moe_x"]) if d["n_moe_x"] is not None else None,
                "n_moe_y": float(d["n_moe_y"]) if d["n_moe_y"] is not None else None,
                "n_moe_z": float(d["n_moe_z"]) if d["n_moe_z"] is not None else None,
                "zone_id": d["zone_id"]
            } for d in devices_data
        ]
        logger.info(f"Fetched {len(devices_data)} devices: {response}")
        return response
    except Exception as e:
        logger.error(f"Error retrieving devices: {e}")
        # Return an empty array on error to prevent frontend crashes
        return []

@router.get(
    "/check_device_id/{device_id}",
    summary="Check if a device ID exists in the ParcoRTLS system",
    description=load_description("check_device_id"),
    tags=["triggers"]
)
async def check_device_id(device_id: str):
    try:
        result = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
        exists = result and isinstance(result, list) and result
        return {"exists": exists}
    except Exception as e:
        logger.error(f"Error checking device ID {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking device ID: {str(e)}")

@router.post(
    "/add_device",
    summary="Add a new device to the ParcoRTLS system using form data",
    description=load_description("add_device"),
    tags=["triggers"]
)
async def add_device(
    device_id: str = Form(...),
    device_type: int = Form(...),
    device_name: str = Form(None),
    n_moe_x: float = Form(None),
    n_moe_y: float = Form(None),
    n_moe_z: float = Form(0),
    zone_id: int = Form(None)
):
    try:
        logger.debug(f"Adding device: {device_id}, type: {device_type}, name: {device_name}")
        result = await execute_raw_query(
            "maint",
            """
            SELECT * FROM usp_device_add(
                $1::VARCHAR,
                $2::INTEGER,
                $3::VARCHAR,
                $4::TIMESTAMP WITHOUT TIME ZONE,
                $5::REAL,
                $6::REAL,
                $7::REAL,
                $8::INTEGER
            )
            """,
            device_id,
            device_type,
            device_name,
            datetime.now(),
            n_moe_x,
            n_moe_y,
            n_moe_z,
            zone_id
        )
        if not result or result[0]["usp_device_add"] != 1:
            raise HTTPException(status_code=500, detail="Failed to add device")
        logger.info(f"Successfully added device: {device_id}")
        return {"x_id_dev": device_id, "message": "Device added successfully"}
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding device: {str(e)}")

@router.put(
    "/edit_device/{device_id}",
    summary="Update an existing device's details in the ParcoRTLS system",
    description=load_description("edit_device"),
    tags=["triggers"]
)
async def edit_device(
    device_id: str,
    new_device_id: str = Form(...),
    device_type: int = Form(None),
    device_name: str = Form(None),
    n_moe_x: float = Form(None),
    n_moe_y: float = Form(None),
    n_moe_z: float = Form(None),
    zone_id: int = Form(None),
    d_srv_bgn: str = Form(None),
    d_srv_end: str = Form(None),
    f_log: bool = Form(None)
):
    try:
        logger.info(f"Received edit_device request: device_id={device_id}, new_device_id={new_device_id}, device_type={device_type}, device_name={device_name}, n_moe_x={n_moe_x}, n_moe_y={n_moe_y}, n_moe_z={n_moe_z}, zone_id={zone_id}, d_srv_bgn={d_srv_bgn}, d_srv_end={d_srv_end}, f_log={f_log}")
        
        d_srv_bgn_timestamp = datetime.fromisoformat(d_srv_bgn.replace('Z', '+00:00')) if d_srv_bgn else None
        d_srv_end_timestamp = datetime.fromisoformat(d_srv_end.replace('Z', '+00:00')) if d_srv_end else None

        result = await execute_raw_query(
            "maint",
            """
            SELECT * FROM public.usp_device_edit(
                $1::VARCHAR,
                $2::VARCHAR,
                $3::INTEGER,
                $4::VARCHAR,
                $5::TIMESTAMP WITHOUT TIME ZONE,
                $6::TIMESTAMP WITHOUT TIME ZONE,
                $7::REAL,
                $8::REAL,
                $9::REAL,
                $10::BOOLEAN,
                $11::INTEGER
            )
            """,
            device_id,
            new_device_id,
            device_type,
            device_name,
            d_srv_bgn_timestamp,
            d_srv_end_timestamp,
            n_moe_x,
            n_moe_y,
            n_moe_z,
            f_log,
            zone_id
        )
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        if result[0]["usp_device_edit"] == 1:
            logger.info(f"Updated device: {device_id} to new ID: {new_device_id}, result: {result}")
            return {"x_id_dev": new_device_id, "message": "Device updated successfully"}
        elif result[0]["usp_device_edit"] == 0:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        else:
            raise HTTPException(status_code=500, detail="Failed to update device")
    except Exception as e:
        logger.error(f"Error editing device: {e}")
        raise HTTPException(status_code=500, detail=f"Error editing device: {str(e)}")

@router.delete(
    "/delete_device/{device_id}",
    summary="Delete a device from the ParcoRTLS system",
    description=load_description("delete_device"),
    tags=["triggers"]
)
async def delete_device(device_id: str):
    try:
        result = await call_stored_procedure("maint", "usp_device_delete", device_id)
        if isinstance(result, list) and result and result[0]["usp_device_delete"] in (0, 1):
            logger.info(f"Device {device_id} deleted successfully or already absent")
            return {"message": "Device deleted successfully"}
        raise HTTPException(status_code=500, detail="Failed to delete device")
    except DatabaseError as e:
        logger.error(f"Database error deleting device: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_device_by_id/{device_id}",
    summary="Retrieve details of a specific device by its ID",
    description=load_description("get_device_by_id"),
    tags=["triggers"]
)
async def get_device_by_id(device_id: str):
    result = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Device not found")

@router.get(
    "/get_device_by_type/{device_type}",
    summary="Retrieve all devices of a specific type",
    description=load_description("get_device_by_type"),
    tags=["triggers"]
)
async def get_device_by_type(device_type: int):
    try:
        result = await call_stored_procedure("maint", "usp_device_select_by_type", device_type)
        if result and isinstance(result, list) and result:
            return result
        return []  # Return empty list instead of 404
    except DatabaseError as e:
        logger.error(f"Database error in get_device_by_type: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in get_device_by_type: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get(
    "/get_out_of_service_devices",
    summary="Retrieve all out-of-service devices in the ParcoRTLS system",
    description=load_description("get_out_of_service_devices"),
    tags=["triggers"]
)
async def get_out_of_service_devices():
    result = await call_stored_procedure("maint", "usp_device_select_outofservice")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No out-of-service devices found")

@router.post(
    "/set_device_end_date",
    summary="Set or update the end date for a device, marking it as out-of-service",
    description=load_description("set_device_end_date"),
    tags=["triggers"]
)
async def set_device_end_date(request: DeviceEndDateRequest):
    end_date = request.end_date or None
    result = await call_stored_procedure("maint", "usp_device_set_end_date", request.device_id, end_date)
    if result and isinstance(result, (int, str)):
        return {"message": "Device end date updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update device end date")

@router.delete(
    "/remove_device_end_date/{device_id}",
    summary="Remove the end date for a device, restoring it to active status",
    description=load_description("remove_device_end_date"),
    tags=["triggers"]
)
async def remove_device_end_date(device_id: str):
    result = await call_stored_procedure("maint", "usp_device_remove_end_date", device_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device end date removed successfully"}
    raise HTTPException(status_code=500, detail="Failed to remove device end date")

@router.put(
    "/set_device_state",
    summary="Update a device's state (active or inactive) in the ParcoRTLS system",
    description=load_description("set_device_state"),
    tags=["triggers"]
)
async def set_device_state(device_id: str = Form(...), new_state: str = Form(...)):
    request = DeviceStateRequest(device_id=device_id, new_state=new_state)
    try:
        device = await call_stored_procedure("maint", "usp_device_select_by_id", request.device_id)
        if not device or not isinstance(device, list) or not device:
            raise HTTPException(status_code=404, detail="Device not found")
        result = await call_stored_procedure(
            "maint", "usp_device_set_end_date" if request.new_state != "active" else "usp_device_remove_end_date",
            request.device_id,
            datetime.now() if request.new_state != "active" else None
        )
        if result and isinstance(result, (int, str)):
            return {"message": "Device state updated successfully"}
        raise HTTPException(status_code=500, detail="Device state update failed")
    except DatabaseError as e:
        logger.error(f"Database error updating device state: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error updating device state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/add_device_type",
    summary="Add a new device type to the ParcoRTLS system",
    description=load_description("add_device_type"),
    tags=["triggers"]
)
async def add_device_type(request: DeviceTypeRequest):
    try:
        result = await call_stored_procedure("maint", "usp_device_type_add", request.description)
        if isinstance(result, list) and result:
            return_value = result[0].get("usp_device_type_add")
            if isinstance(return_value, int):
                if return_value == -2:
                    raise HTTPException(status_code=400, detail=f"Device type description '{request.description}' already exists")
                elif return_value == -1:
                    raise HTTPException(status_code=500, detail="Failed to add device type due to a database error")
                else:
                    return {"message": "Device type added successfully", "type_id": return_value}
        raise HTTPException(status_code=500, detail="Failed to add device type: Invalid response from database")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error adding device type: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding device type: {str(e)}")

@router.delete(
    "/delete_device_type/{type_id}",
    summary="Delete a device type from the ParcoRTLS system",
    description=load_description("delete_device_type"),
    tags=["triggers"]
)
async def delete_device_type(type_id: int):
    try:
        result = await call_stored_procedure("maint", "usp_device_type_delete", type_id)
        if isinstance(result, list) and result:
            return_value = result[0].get("usp_device_type_delete")
            if isinstance(return_value, int):
                if return_value in (0, 1):  # 0 means already deleted, 1 means successfully deleted
                    return {"message": "Device type deleted successfully"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to delete device type: Unexpected return value")
        raise HTTPException(status_code=500, detail="Failed to delete device type: Invalid response from database")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting device type: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting device type: {str(e)}")

@router.put(
    "/edit_device_type",
    summary="Update an existing device type's description",
    description=load_description("edit_device_type"),
    tags=["triggers"]
)
async def edit_device_type(type_id: int, request: DeviceTypeRequest):
    result = await call_stored_procedure("maint", "usp_device_type_edit", type_id, request.description)
    if result and isinstance(result, (int, str)):
        return {"message": "Device type edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit device type")

@router.get(
    "/list_device_types",
    summary="Retrieve a list of all device types in the ParcoRTLS system",
    description=load_description("list_device_types"),
    tags=["triggers"]
)
async def list_device_types():
    result = await call_stored_procedure("maint", "usp_device_type_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device types found")

@router.post(
    "/assign_device_to_zone",
    summary="Assign a device to a zone or entity in the ParcoRTLS system",
    description=load_description("assign_device_to_zone"),
    tags=["triggers"]
)
async def assign_device_to_zone(device_id: str = Form(...), entity_id: str = Form(...), reason_id: int = Form(...)):
    request = AssignDeviceRequest(device_id=device_id, entity_id=entity_id, reason_id=reason_id)
    try:
        device = await call_stored_procedure("maint", "usp_device_select_by_id", request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        entity = await call_stored_procedure("maint", "usp_entity_by_id", request.entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        reasons = await call_stored_procedure("maint", "usp_assmt_reason_list")
        if not any(r["i_rsn"] == request.reason_id for r in reasons):
            raise HTTPException(status_code=400, detail="Invalid reason ID")
        start_date = datetime.now()
        result = await call_stored_procedure(
            "maint", "usp_assign_dev_add",
            request.device_id, request.entity_id, request.reason_id, start_date, None
        )
        if isinstance(result, list) and result:
            # Check if the result contains a message indicating success
            message = result[0].get("usp_assign_dev_add")
            if message == "Assignment added successfully":
                # Fetch the latest assignment ID for this device
                assignments = await call_stored_procedure("maint", "usp_assign_dev_list_by_id", request.device_id, False)
                if assignments and isinstance(assignments, list) and assignments:
                    assignment_id = assignments[-1].get("i_asn_dev")
                    return {"message": "Device assigned successfully", "assignment_id": str(assignment_id)}
        raise HTTPException(status_code=500, detail="Failed to assign device")
    except DatabaseError as e:
        logger.error(f"Database error assigning device: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error assigning device: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/delete_device_assignment/{assignment_id}",
    summary="Delete a specific device assignment",
    description=load_description("delete_device_assignment"),
    tags=["triggers"]
)
async def delete_device_assignment(assignment_id: int):
    result = await call_stored_procedure("maint", "usp_assign_dev_delete", assignment_id)
    if result and isinstance(result, list) and result:
        message = result[0].get("usp_assign_dev_delete")
        if message == "Assignment end date updated successfully":
            return {"message": "Device assignment deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete device assignment")

@router.delete(
    "/delete_all_device_assignments",
    summary="Delete all device assignments in the ParcoRTLS system",
    description=load_description("delete_all_device_assignments"),
    tags=["triggers"]
)
async def delete_all_device_assignments():
    result = await call_stored_procedure("maint", "usp_assign_dev_delete_all")
    if result and isinstance(result, (int, str)):
        return {"message": "All device assignments deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete all device assignments")

@router.delete(
    "/delete_device_assignments_by_entity/{entity_id}",
    summary="Delete all device assignments for a specific entity",
    description=load_description("delete_device_assignments_by_entity"),
    tags=["triggers"]
)
async def delete_device_assignments_by_entity(entity_id: str):
    result = await call_stored_procedure("maint", "usp_assign_dev_delete_all_by_ent", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignments deleted successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to delete device assignments for entity")

@router.put(
    "/edit_device_assignment",
    summary="Update an existing device assignment",
    description=load_description("edit_device_assignment"),
    tags=["triggers"]
)
async def edit_device_assignment(request: AssignDeviceEditRequest):
    result = await call_stored_procedure("maint", "usp_assign_dev_edit", request.assignment_id, request.device_id, request.entity_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit device assignment")

@router.post(
    "/end_device_assignment",
    summary="End a specific device assignment",
    description=load_description("end_device_assignment"),
    tags=["triggers"]
)
async def end_device_assignment(request: AssignDeviceEndRequest):
    result = await call_stored_procedure("maint", "usp_assign_dev_end", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end device assignment")

@router.post(
    "/end_all_device_assignments",
    summary="End all device assignments in the ParcoRTLS system",
    description=load_description("end_all_device_assignments"),
    tags=["triggers"]
)
async def end_all_device_assignments():
    result = await call_stored_procedure("maint", "usp_assign_dev_end_all")
    if result and isinstance(result, (int, str)):
        return {"message": "All device assignments ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end all device assignments")

@router.get(
    "/list_device_assignments",
    summary="Retrieve a list of all device assignments",
    description=load_description("list_device_assignments"),
    tags=["triggers"]
)
async def list_device_assignments(include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_dev_list", include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found")

@router.get(
    "/list_device_assignments_by_entity/{entity_id}",
    summary="Retrieve all device assignments for a specific entity",
    description=load_description("list_device_assignments_by_entity"),
    tags=["triggers"]
)
async def list_device_assignments_by_entity(entity_id: str, include_ended: bool = False):
    try:
        result = await call_stored_procedure("maint", "usp_assign_dev_list_by_entity", entity_id, include_ended)
        if result and isinstance(result, list) and result:
            return result
        return []  # Return empty list instead of 404
    except DatabaseError as e:
        logger.error(f"Database error in list_device_assignments_by_entity: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in list_device_assignments_by_entity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get(
    "/list_device_assignments_by_device/{device_id}",
    summary="Retrieve all assignments for a specific device",
    description=load_description("list_device_assignments_by_device"),
    tags=["triggers"]
)
async def list_device_assignments_by_device(device_id: str, include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_id", device_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for device")

@router.get(
    "/list_device_assignments_by_reason/{reason_id}",
    summary="Retrieve all device assignments for a specific reason",
    description=load_description("list_device_assignments_by_reason"),
    tags=["triggers"]
)
async def list_device_assignments_by_reason(reason_id: int, include_ended: bool = False):
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_reason", reason_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for reason")

@router.get(
    "/zone_list",
    summary="Retrieve a list of all zones in the ParcoRTLS system",
    description=load_description("list_zones"),
    tags=["triggers"]
)
async def list_zones():
    try:
        result = await call_stored_procedure("maint", "usp_zone_list")
        if result and isinstance(result, list):
            logger.info("Successfully fetched zone list")
            return result
        raise HTTPException(status_code=404, detail="No zones found")
    except Exception as e:
        logger.error(f"Error fetching zone list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/zones_with_maps",
    summary="Retrieve all zones with their associated map IDs for the Build Out Tool",
    description=load_description("get_zones_with_maps"),
    tags=["triggers"]
)
async def get_zones_with_maps():
    try:
        result = await execute_raw_query(
            "maint",
            "SELECT i_zn, x_nm_zn, i_typ_zn, i_map FROM public.zones ORDER BY i_zn"
        )
        if result and isinstance(result, list):
            logger.info("Successfully fetched zones with map IDs")
            return result
        raise HTTPException(status_code=404, detail="No zones found")
    except Exception as e:
        logger.error(f"Error fetching zones with maps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))