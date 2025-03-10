"""
routes/device.py
Version: 0.1.13 (Fixed handling of usp_device_add results for i_typ_dev)
Device management endpoints for ParcoRTLS FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from models import DeviceAddRequest, DeviceStateRequest, DeviceTypeRequest, DeviceEndDateRequest, AssignDeviceRequest, AssignDeviceDeleteRequest, AssignDeviceEditRequest, AssignDeviceEndRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/get_all_devices")
async def get_all_devices():
    """Fetch all devices."""
    result = await call_stored_procedure("maint", "usp_device_select_all")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No devices found")

@router.post("/add_device")
async def add_device(device_id: str = Form(...), device_type: int = Form(...), device_name: str = Form(None)):
    """Add a new device via form input or JSON.
    
    Args:
        device_id: The manufacturer-provided device ID (e.g., AllTraq_2503251633).
        device_type: The device type ID (e.g., 1 for Tag).
        device_name: Optional name for the device (defaults to 'New Device' if not provided).
    """
    request = DeviceAddRequest(device_id=device_id, device_type=device_type, device_name=device_name)
    try:
        # Check if device_id already exists using raw query (bypass stored procedure)
        logger.debug(f"Checking if device_id '{request.device_id}' exists using raw query")
        existing = await execute_raw_query("maint", "SELECT x_id_dev FROM public.devices WHERE x_id_dev = $1", request.device_id)
        logger.debug(f"Raw query result for '{request.device_id}': {existing}")
        if existing:
            raise HTTPException(status_code=400, detail=f"Device ID '{request.device_id}' already exists. Please use a unique ID from the manufacturer (e.g., Tag123).")
        
        # Validate device type
        types = await call_stored_procedure("maint", "usp_device_type_list")
        if not any(t["i_typ_dev"] == request.device_type for t in types):
            raise HTTPException(status_code=400, detail="Invalid device type")
        
        start_date = datetime.now()
        logger.debug(f"Attempting to add device with p_x_id_dev: {request.device_id}, p_i_typ_dev: {request.device_type}, p_x_nm_dev: {request.device_name or ''}, p_d_srv_bgn: {start_date}")
        result = await call_stored_procedure(
            "maint", "usp_device_add",
            request.device_id, request.device_type, request.device_name or "", start_date
        )
        logger.debug(f"usp_device_add raw result for p_x_id_dev '{request.device_id}': {result}")
        
        # Handle the result more robustly
        if result is not None:
            if isinstance(result, (int, str)):
                device_id_result = str(result)
            elif isinstance(result, list) and result:
                # If result is a list of rows, extract i_typ_dev or use device_id
                if result and "i_typ_dev" in result[0]:
                    device_id_result = str(result[0]["i_typ_dev"])
                else:
                    device_id_result = request.device_id
            else:
                # If result is None or unexpected, check if the device was added
                existing_after = await execute_raw_query("maint", "SELECT x_id_dev, i_typ_dev FROM public.devices WHERE x_id_dev = $1", request.device_id)
                if existing_after:
                    logger.warning(f"Device {request.device_id} was added despite usp_device_add returning {result}")
                    device_id_result = str(existing_after[0]["i_typ_dev"]) if "i_typ_dev" in existing_after[0] else request.device_id
                else:
                    raise HTTPException(status_code=500, detail="Failed to add device")
        else:
            raise HTTPException(status_code=500, detail="Failed to add device")
        
        logger.info(f"Successfully added device with ID: {request.device_id}")
        return {"message": "Device added successfully", "device_id": device_id_result}
    
    except HTTPException as e:
        # Re-raise HTTPException to ensure correct status code (400 or 500)
        raise e
    except DatabaseError as e:
        logger.error(f"Database error adding device: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error adding device: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# [Keep the rest of the endpoints unchanged]

@router.delete("/delete_device/{device_id}")
async def delete_device(device_id: str):
    """Delete a device by ID."""
    try:
        existing = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Device not found")
        result = await call_stored_procedure("maint", "usp_device_delete", device_id)
        if result and isinstance(result, (int, str)):
            return {"message": "Device deleted successfully"}
        raise HTTPException(status_code=500, detail="Failed to delete device")
    except DatabaseError as e:
        logger.error(f"Database error deleting device: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_device_by_id/{device_id}")
async def get_device_by_id(device_id: str):
    """Fetch device details by ID."""
    result = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Device not found")

@router.get("/get_device_by_type/{device_type}")
async def get_device_by_type(device_type: int):
    """Fetch devices by type."""
    result = await call_stored_procedure("maint", "usp_device_select_by_type", device_type)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No devices found for this type")

@router.get("/get_out_of_service_devices")
async def get_out_of_service_devices():
    """Fetch all out-of-service devices."""
    result = await call_stored_procedure("maint", "usp_device_select_outofservice")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No out-of-service devices found")

@router.post("/set_device_end_date")
async def set_device_end_date(request: DeviceEndDateRequest):
    """Set or remove the end date for a device."""
    end_date = request.end_date or None
    result = await call_stored_procedure("maint", "usp_device_set_end_date", request.device_id, end_date)
    if result and isinstance(result, (int, str)):
        return {"message": "Device end date updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update device end date")

@router.delete("/remove_device_end_date/{device_id}")
async def remove_device_end_date(device_id: str):
    """Remove the end date for a device."""
    result = await call_stored_procedure("maint", "usp_device_remove_end_date", device_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device end date removed successfully"}
    raise HTTPException(status_code=500, detail="Failed to remove device end date")

@router.put("/set_device_state")
async def set_device_state(device_id: str = Form(...), new_state: str = Form(...)):
    """Update a device's state via form input or JSON."""
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

@router.post("/add_device_type")
async def add_device_type(request: DeviceTypeRequest):
    """Add a new device type."""
    result = await call_stored_procedure("maint", "usp_device_type_add", request.description)
    if result and isinstance(result, (int, str)):
        return {"message": "Device type added successfully", "type_id": result if isinstance(result, int) else result[0]["i_typ_dev"] if isinstance(result, list) and result else None}
    raise HTTPException(status_code=500, detail="Failed to add device type")

@router.delete("/delete_device_type/{type_id}")
async def delete_device_type(type_id: int):
    """Delete a device type by ID."""
    result = await call_stored_procedure("maint", "usp_device_type_delete", type_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device type deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete device type")

@router.put("/edit_device_type")
async def edit_device_type(type_id: int, request: DeviceTypeRequest):
    """Edit a device type."""
    result = await call_stored_procedure("maint", "usp_device_type_edit", type_id, request.description)
    if result and isinstance(result, (int, str)):
        return {"message": "Device type edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit device type")

@router.get("/list_device_types")
async def list_device_types():
    """List all device types."""
    result = await call_stored_procedure("maint", "usp_device_type_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device types found")

# Device Assignment Management
@router.post("/assign_device_to_zone")
async def assign_device_to_zone(device_id: str = Form(...), entity_id: str = Form(...), reason_id: int = Form(...)):
    """Assign a device to a zone via form input or JSON."""
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
        if result and isinstance(result, (int, str)):
            return {"message": "Device assigned successfully", "assignment_id": str(result)}
        raise HTTPException(status_code=500, detail="Failed to assign device")
    except DatabaseError as e:
        logger.error(f"Database error assigning device: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error assigning device: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_device_assignment/{assignment_id}")
async def delete_device_assignment(request: AssignDeviceDeleteRequest):
    """Delete a device assignment by ID."""
    result = await call_stored_procedure("maint", "usp_assign_dev_delete", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete device assignment")

@router.delete("/delete_all_device_assignments")
async def delete_all_device_assignments():
    """Delete all device assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_delete_all")
    if result and isinstance(result, (int, str)):
        return {"message": "All device assignments deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete all device assignments")

@router.delete("/delete_device_assignments_by_entity/{entity_id}")
async def delete_device_assignments_by_entity(entity_id: str):
    """Delete all device assignments by entity ID."""
    result = await call_stored_procedure("maint", "usp_assign_dev_delete_all_by_ent", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignments deleted successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to delete device assignments for entity")

@router.put("/edit_device_assignment")
async def edit_device_assignment(request: AssignDeviceEditRequest):
    """Edit a device assignment."""
    result = await call_stored_procedure("maint", "usp_assign_dev_edit", request.assignment_id, request.device_id, request.entity_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit device assignment")

@router.post("/end_device_assignment")
async def end_device_assignment(request: AssignDeviceEndRequest):
    """End a device assignment by ID."""
    result = await call_stored_procedure("maint", "usp_assign_dev_end", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end device assignment")

@router.post("/end_all_device_assignments")
async def end_all_device_assignments():
    """End all device assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_end_all")
    if result and isinstance(result, (int, str)):
        return {"message": "All device assignments ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end all device assignments")

@router.get("/list_device_assignments")
async def list_device_assignments(include_ended: bool = False):
    """List all device assignments, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_list", include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found")

@router.get("/list_device_assignments_by_entity/{entity_id}")
async def list_device_assignments_by_entity(entity_id: str, include_ended: bool = False):
    """List device assignments by entity ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_entity", entity_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for entity")

@router.get("/list_device_assignments_by_device/{device_id}")
async def list_device_assignments_by_device(device_id: str, include_ended: bool = False):
    """List device assignments by device ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_id", device_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for device")

@router.get("/list_device_assignments_by_reason/{reason_id}")
async def list_device_assignments_by_reason(reason_id: int, include_ended: bool = False):
    """List device assignments by reason ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_reason", reason_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for reason")