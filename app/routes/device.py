# Version: 250319 /home/parcoadmin/parco_fastapi/app/routes/device.py 0.1.27
# --- CHANGED: Bumped version from 0.1.26 to 0.1.27 to pass new device ID to usp_device_edit for updating x_id_dev
# Device management endpoints for ParcoRTLS FastAPI application.
#   
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from models import DeviceAddRequest, DeviceStateRequest, DeviceTypeRequest, DeviceEndDateRequest, AssignDeviceRequest, AssignDeviceDeleteRequest, AssignDeviceEditRequest, AssignDeviceEndRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/get_all_devices")
async def get_all_devices():
    """Fetches all devices with zone_id"""
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

@router.get("/check_device_id/{device_id}")
async def check_device_id(device_id: str):
    """Check if a device ID already exists in the database."""
    try:
        result = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
        exists = result and isinstance(result, list) and result
        return {"exists": exists}
    except Exception as e:
        logger.error(f"Error checking device ID {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking device ID: {str(e)}")

@router.post("/add_device")
async def add_device(
    device_id: str = Form(...),
    device_type: int = Form(...),
    device_name: str = Form(None),
    n_moe_x: float = Form(None),
    n_moe_y: float = Form(None),
    n_moe_z: float = Form(0),
    zone_id: int = Form(None)
):
    """Add a new device with zone_id"""
    try:
        logger.debug(f"Adding device: {device_id}, type: {device_type}, name: {device_name}, loc: ({n_moe_x}, {n_moe_y}, {n_moe_z}), zone_id: {zone_id}")
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

@router.put("/edit_device/{device_id}")
async def edit_device(
    device_id: str,
    new_device_id: str = Form(...),  # --- CHANGED: Added new_device_id parameter to capture the updated device ID
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
    """Edit an existing device’s name, type, location, and zone_id using usp_device_edit in public schema."""
    try:
        logger.info(f"Received edit_device request: device_id={device_id}, new_device_id={new_device_id}, device_type={device_type}, device_name={device_name}, n_moe_x={n_moe_x}, n_moe_y={n_moe_y}, n_moe_z={n_moe_z}, zone_id={zone_id}, d_srv_bgn={d_srv_bgn}, d_srv_end={d_srv_end}, f_log={f_log}")
        
        d_srv_bgn_timestamp = datetime.fromisoformat(d_srv_bgn.replace('Z', '+00:00')) if d_srv_bgn else None
        d_srv_end_timestamp = datetime.fromisoformat(d_srv_end.replace('Z', '+00:00')) if d_srv_end else None

        # --- CHANGED: Pass the new device ID to usp_device_edit
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
            device_id,  # Original device ID
            new_device_id,  # New device ID
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

@router.delete("/delete_device/{device_id}")
async def delete_device(device_id: str):
    """Delete a device by ID. Returns success if deleted or already gone."""
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

@router.get("/zone_list")
async def list_zones():
    """List all zones with their map IDs."""
    try:
        result = await call_stored_procedure("maint", "usp_zone_list")
        if result and isinstance(result, list):
            logger.info("Successfully fetched zone list")
            return result
        raise HTTPException(status_code=404, detail="No zones found")
    except Exception as e:
        logger.error(f"Error fetching zone list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/zones_with_maps")
async def get_zones_with_maps():
    """Fetch all zones with their map IDs for Build Out Tool."""
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