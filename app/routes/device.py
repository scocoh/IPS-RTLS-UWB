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

logger = logging.getLogger(__name__)
router = APIRouter(tags=["devices"])

@router.get("/get_all_devices")
async def get_all_devices():
    """
    Retrieve a list of all devices in the ParcoRTLS system, including their associated zone IDs.

    This endpoint fetches all devices (e.g., tags, beacons) from the `devices` table using a raw SQL query. It is used to provide a comprehensive overview of devices for monitoring, reporting, or populating UI elements in the React frontend.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing device details.
            - x_id_dev (str): Device ID (e.g., "TAG001").
            - i_typ_dev (int): Device type ID (e.g., 1 for Tag, 2 for Beacon).
            - x_nm_dev (str): Device name (e.g., "Employee Tag").
            - n_moe_x (float or None): X-coordinate of the device's margin of error.
            - n_moe_y (float or None): Y-coordinate of the device's margin of error.
            - n_moe_z (float or None): Z-coordinate of the device's margin of error.
            - zone_id (int or None): ID of the associated zone (e.g., 1 for "Main Lobby").

    Raises:
        None: Returns an empty list on error to prevent frontend crashes.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_all_devices"
        ```
        Response:
        ```json
        [
            {
                "x_id_dev": "TAG001",
                "i_typ_dev": 1,
                "x_nm_dev": "Employee Tag",
                "n_moe_x": 100.5,
                "n_moe_y": 200.7,
                "n_moe_z": 10.0,
                "zone_id": 1
            },
            {
                "x_id_dev": "BEACON002",
                "i_typ_dev": 2,
                "x_nm_dev": "Lobby Beacon",
                "n_moe_x": null,
                "n_moe_y": null,
                "n_moe_z": null,
                "zone_id": 1
            }
        ]
        ```

    Use Case:
        - Populate a dashboard in the React frontend with all devices and their current zones for real-time monitoring.
        - Generate a report of all devices and their locations for inventory management.

    Hint:
        - Use this endpoint sparingly in high-traffic scenarios, as it retrieves all devices. Consider filtering by type or zone for better performance.
        - The `zone_id` can be cross-referenced with the `/zone_list` endpoint to get zone details.
    """
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
    """
    Check if a device ID exists in the ParcoRTLS system.

    This endpoint queries the database using the `usp_device_select_by_id` stored procedure to verify if a device ID is already registered. It is used to prevent duplicate device IDs during device creation.

    Args:
        device_id (str): The device ID to check (e.g., "TAG001"). Required.

    Returns:
        dict: A JSON response indicating whether the device ID exists.
            - exists (bool): True if the device ID exists, False otherwise.

    Raises:
        HTTPException:
            - 500: If a database or unexpected error occurs during the check.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/check_device_id/TAG001"
        ```
        Response:
        ```json
        {"exists": true}
        ```

    Use Case:
        - Validate a new device ID in the React frontend before submitting a device creation form.
        - Ensure uniqueness when registering a new tag or beacon in the system.

    Hint:
        - Use this endpoint before calling `/add_device` to avoid duplicate key errors.
    """
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
    """
    Add a new device to the ParcoRTLS system using form data.

    This endpoint creates a new device (e.g., tag, beacon) in the system by executing the `usp_device_add` stored procedure via a raw query. It supports associating the device with a zone and setting initial location coordinates. It is used to register devices for tracking within the ParcoRTLS system.

    Args:
        device_id (str): Unique identifier for the device (e.g., "TAG001"). Required.
        device_type (int): Device type ID (e.g., 1 for Tag, 2 for Beacon). Required.
        device_name (str, optional): Descriptive name of the device (e.g., "Employee Tag"). Defaults to None.
        n_moe_x (float, optional): X-coordinate of the device's margin of error. Defaults to None.
        n_moe_y (float, optional): Y-coordinate of the device's margin of error. Defaults to None.
        n_moe_z (float, optional): Z-coordinate of the device's margin of error. Defaults to 0.
        zone_id (int, optional): ID of the associated zone (e.g., 1 for "Main Lobby"). Defaults to None.

    Returns:
        dict: A JSON response indicating success and the device ID.
            - x_id_dev (str): The ID of the newly created device.
            - message (str): Success message ("Device added successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/add_device" \
             -H "Content-Type: multipart/form-data" \
             -F "device_id=TAG001" \
             -F "device_type=1" \
             -F "device_name=Employee Tag" \
             -F "n_moe_x=100.5" \
             -F "n_moe_y=200.7" \
             -F "n_moe_z=10.0" \
             -F "zone_id=1"
        ```
        Response:
        ```json
        {"x_id_dev": "TAG001", "message": "Device added successfully"}
        ```

    Use Case:
        - Register a new employee tag ("TAG001") with initial location coordinates and assign it to a specific zone for real-time tracking.
        - Add a beacon to a zone to enhance location accuracy in a hospital campus.

    Hint:
        - Use `/check_device_id/{device_id}` to verify the `device_id` is unique before calling this endpoint.
        - Retrieve valid `device_type` values from `/list_device_types` and `zone_id` values from `/zone_list` to ensure accurate inputs.
        - The `multipart/form-data` content type is used to support form submissions from the React frontend.
    """
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

@router.put("/edit_device/{device_id}")
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
    """
    Update an existing device's details in the ParcoRTLS system.

    This endpoint modifies a device's attributes (e.g., ID, type, name, location, zone, service dates, logging flag) using the `usp_device_edit` stored procedure. It is used to update device information when changes occur, such as reassigning a device to a new zone or updating its location coordinates.

    Args:
        device_id (str): The current ID of the device to update (e.g., "TAG001"). Required.
        new_device_id (str): The new ID for the device (e.g., "TAG002"). Required.
        device_type (int, optional): Updated device type ID (e.g., 1 for Tag). Defaults to None.
        device_name (str, optional): Updated device name (e.g., "Updated Employee Tag"). Defaults to None.
        n_moe_x (float, optional): Updated X-coordinate of the device's margin of error. Defaults to None.
        n_moe_y (float, optional): Updated Y-coordinate of the device's margin of error. Defaults to None.
        n_moe_z (float, optional): Updated Z-coordinate of the device's margin of error. Defaults to None.
        zone_id (int, optional): Updated zone ID (e.g., 2 for "Ward A"). Defaults to None.
        d_srv_bgn (str, optional): Updated service start date in ISO format (e.g., "2025-04-26T00:00:00Z"). Defaults to None.
        d_srv_end (str, optional): Updated service end date in ISO format (e.g., "2025-12-31T00:00:00Z"). Defaults to None.
        f_log (bool, optional): Updated logging flag indicating whether to log device activity. Defaults to None.

    Returns:
        dict: A JSON response indicating success and the updated device ID.
            - x_id_dev (str): The updated device ID.
            - message (str): Success message ("Device updated successfully").

    Raises:
        HTTPException:
            - 404: If the device is not found.
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/edit_device/TAG001" \
             -H "Content-Type: multipart/form-data" \
             -F "new_device_id=TAG002" \
             -F "device_type=1" \
             -F "device_name=Updated Employee Tag" \
             -F "n_moe_x=150.0" \
             -F "n_moe_y=250.0" \
             -F "n_moe_z=15.0" \
             -F "zone_id=2" \
             -F "d_srv_bgn=2025-04-26T00:00:00Z" \
             -F "d_srv_end=2025-12-31T00:00:00Z" \
             -F "f_log=true"
        ```
        Response:
        ```json
        {"x_id_dev": "TAG002", "message": "Device updated successfully"}
        ```

    Use Case:
        - Update a tag's location coordinates after it moves to a new area in a Zone L1 campus.
        - Reassign a beacon to a different zone or change its service dates after maintenance.

    Hint:
        - Verify the `device_id` exists using `/get_device_by_id/{device_id}` before updating.
        - Ensure `device_type` and `zone_id` are valid by checking `/list_device_types` and `/zone_list`, respectively.
        - The `d_srv_bgn` and `d_srv_end` parameters must be in ISO 8601 format with a 'Z' suffix for UTC.
    """
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

@router.delete("/delete_device/{device_id}")
async def delete_device(device_id: str):
    """
    Delete a device from the ParcoRTLS system.

    This endpoint removes a device by its ID using the `usp_device_delete` stored procedure. It is used to decommission devices that are no longer in use, such as retired tags or beacons.

    Args:
        device_id (str): The ID of the device to delete (e.g., "TAG001"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device deleted successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_device/TAG001"
        ```
        Response:
        ```json
        {"message": "Device deleted successfully"}
        ```

    Use Case:
        - Remove a tag ("TAG001") from the system after an employee leaves the organization.
        - Decommission a beacon that is no longer operational.

    Hint:
        - Ensure all assignments for the device are removed using `/delete_all_device_assignments` or `/end_all_device_assignments` before deletion to avoid database constraints.
        - A return value of 0 from the stored procedure indicates the device was already deleted, which is treated as success.
    """
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
    """
    Retrieve details of a specific device by its ID.

    This endpoint fetches a single device's details using the `usp_device_select_by_id` stored procedure. It is used to display device information or verify existence before performing operations like assignments or updates.

    Args:
        device_id (str): The ID of the device to retrieve (e.g., "TAG001"). Required.

    Returns:
        dict: A dictionary containing device details.
            - x_id_dev (str): Device ID.
            - i_typ_dev (int): Device type ID.
            - x_nm_dev (str): Device name.
            - n_moe_x (float or None): X-coordinate of the margin of error.
            - n_moe_y (float or None): Y-coordinate of the margin of error.
            - n_moe_z (float or None): Z-coordinate of the margin of error.
            - zone_id (int or None): Associated zone ID.
            - d_srv_bgn (datetime or None): Service start date.
            - d_srv_end (datetime or None): Service end date.
            - f_log (bool or None): Logging flag.

    Raises:
        HTTPException:
            - 404: If the device is not found.
            - 500: If a database error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_device_by_id/TAG001"
        ```
        Response:
        ```json
        {
            "x_id_dev": "TAG001",
            "i_typ_dev": 1,
            "x_nm_dev": "Employee Tag",
            "n_moe_x": 100.5,
            "n_moe_y": 200.7,
            "n_moe_z": 10.0,
            "zone_id": 1,
            "d_srv_bgn": "2025-04-26T00:00:00",
            "d_srv_end": null,
            "f_log": true
        }
        ```

    Use Case:
        - Display detailed information about a tag ("TAG001") in the React frontend.
        - Verify a device's current zone or location before reassigning it.

    Hint:
        - Use this endpoint to prefetch device data before rendering forms or dashboards to reduce latency.
    """
    result = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Device not found")

@router.get("/get_device_by_type/{device_type}")
async def get_device_by_type(device_type: int):
    """
    Retrieve all devices of a specific type.

    This endpoint fetches devices of a given type (e.g., all tags or all beacons) using the `usp_device_select_by_type` stored procedure. It is useful for filtering devices by their category for reporting or UI display.

    Args:
        device_type (int): The device type ID to filter by (e.g., 1 for Tag, 2 for Beacon). Required.

    Returns:
        list: A list of dictionaries, each containing device details.
            - x_id_dev (str): Device ID.
            - i_typ_dev (int): Device type ID.
            - x_nm_dev (str): Device name.
            - n_moe_x (float or None): X-coordinate of the margin of error.
            - n_moe_y (float or None): Y-coordinate of the margin of error.
            - n_moe_z (float or None): Z-coordinate of the margin of error.
            - zone_id (int or None): Associated zone ID.
            - d_srv_bgn (datetime or None): Service start date.
            - d_srv_end (datetime or None): Service end date.
            - f_log (bool or None): Logging flag.

    Raises:
        None: Returns an empty list if no devices are found or if an error occurs, preventing frontend crashes.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_device_by_type/1"
        ```
        Response:
        ```json
        [
            {
                "x_id_dev": "TAG001",
                "i_typ_dev": 1,
                "x_nm_dev": "Employee Tag",
                "n_moe_x": 100.5,
                "n_moe_y": 200.7,
                "n_moe_z": 10.0,
                "zone_id": 1,
                "d_srv_bgn": "2025-04-26T00:00:00",
                "d_srv_end": null,
                "f_log": true
            }
        ]
        ```

    Use Case:
        - List all tags (type ID 1) in a dropdown for assigning to entities in the React frontend.
        - Generate a report of all beacons (type ID 2) for maintenance scheduling.

    Hint:
        - Retrieve valid `device_type` values from `/list_device_types` to ensure accurate filtering.
        - The empty list return on error aligns with version 0.1.38 changes to improve frontend compatibility.
    """
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

@router.get("/get_out_of_service_devices")
async def get_out_of_service_devices():
    """
    Retrieve all out-of-service devices in the ParcoRTLS system.

    This endpoint fetches devices marked as out-of-service (e.g., with an active end date) using the `usp_device_select_outofservice` stored procedure. It is used to identify devices that are not currently operational for maintenance or replacement purposes.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing details of out-of-service devices.
            - x_id_dev (str): Device ID.
            - i_typ_dev (int): Device type ID.
            - x_nm_dev (str): Device name.
            - n_moe_x (float or None): X-coordinate of the margin of error.
            - n_moe_y (float or None): Y-coordinate of the margin of error.
            - n_moe_z (float or None): Z-coordinate of the margin of error.
            - zone_id (int or None): Associated zone ID.
            - d_srv_bgn (datetime or None): Service start date.
            - d_srv_end (datetime or None): Service end date.
            - f_log (bool or None): Logging flag.

    Raises:
        HTTPException:
            - 404: If no out-of-service devices are found.
            - 500: If a database error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_out_of_service_devices"
        ```
        Response:
        ```json
        [
            {
                "x_id_dev": "TAG002",
                "i_typ_dev": 1,
                "x_nm_dev": "Retired Tag",
                "n_moe_x": null,
                "n_moe_y": null,
                "n_moe_z": null,
                "zone_id": null,
                "d_srv_bgn": "2025-01-01T00:00:00",
                "d_srv_end": "2025-04-26T00:00:00",
                "f_log": false
            }
        ]
        ```

    Use Case:
        - Generate a maintenance report of all out-of-service tags for replacement.
        - Display out-of-service beacons in the React frontend to prioritize repairs.

    Hint:
        - Cross-reference with `/get_device_by_id/{device_id}` to get detailed history for each out-of-service device.
        - Use `/set_device_end_date` to mark devices as out-of-service or `/remove_device_end_date` to restore them.
    """
    result = await call_stored_procedure("maint", "usp_device_select_outofservice")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No out-of-service devices found")

@router.post("/set_device_end_date")
async def set_device_end_date(request: DeviceEndDateRequest):
    """
    Set or update the end date for a device, marking it as out-of-service.

    This endpoint updates a device's service end date using the `usp_device_set_end_date` stored procedure. It is used to indicate that a device is no longer operational, such as when a tag is retired or a beacon is taken offline for maintenance.

    Args:
        request (DeviceEndDateRequest): The request body containing device details.
            - device_id (str): The ID of the device to update (e.g., "TAG001"). Required.
            - end_date (datetime or None): The service end date in ISO format (e.g., "2025-12-31T00:00:00"). Optional, defaults to None (clears end date).

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device end date updated successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/set_device_end_date" \
             -H "Content-Type: application/json" \
             -d '{"device_id": "TAG001", "end_date": "2025-12-31T00:00:00"}'
        ```
        Response:
        ```json
        {"message": "Device end date updated successfully"}
        ```

    Use Case:
        - Mark a tag as out-of-service after an employee leaves the organization.
        - Set an end date for a beacon scheduled for maintenance.

    Hint:
        - Verify the `device_id` exists using `/get_device_by_id/{device_id}` before updating.
        - Setting `end_date` to null via this endpoint or using `/remove_device_end_date` can restore a device to active status.
    """
    end_date = request.end_date or None
    result = await call_stored_procedure("maint", "usp_device_set_end_date", request.device_id, end_date)
    if result and isinstance(result, (int, str)):
        return {"message": "Device end date updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update device end date")

@router.delete("/remove_device_end_date/{device_id}")
async def remove_device_end_date(device_id: str):
    """
    Remove the end date for a device, restoring it to active status.

    This endpoint clears a device's service end date using the `usp_device_remove_end_date` stored procedure. It is used to reactivate a device that was previously marked as out-of-service.

    Args:
        device_id (str): The ID of the device to update (e.g., "TAG001"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device end date removed successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/remove_device_end_date/TAG001"
        ```
        Response:
        ```json
        {"message": "Device end date removed successfully"}
        ```

    Use Case:
        - Reactivate a tag after it is reassigned to a new employee.
        - Restore a beacon to service after maintenance is completed.

    Hint:
        - Verify the `device_id` exists and is out-of-service using `/get_out_of_service_devices` before calling this endpoint.
        - This endpoint is equivalent to calling `/set_device_end_date` with a null `end_date`.
    """
    result = await call_stored_procedure("maint", "usp_device_remove_end_date", device_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device end date removed successfully"}
    raise HTTPException(status_code=500, detail="Failed to remove device end date")

@router.put("/set_device_state")
async def set_device_state(device_id: str = Form(...), new_state: str = Form(...)):
    """
    Update a device's state (active or inactive) in the ParcoRTLS system.

    This endpoint sets a device's state by either removing its end date (for "active" state) or setting an end date to the current time (for any other state, e.g., "inactive") using the appropriate stored procedures (`usp_device_remove_end_date` or `usp_device_set_end_date`). It is used to manage device operational status.

    Args:
        device_id (str): The ID of the device to update (e.g., "TAG001"). Required.
        new_state (str): The new state of the device (e.g., "active", "inactive"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device state updated successfully").

    Raises:
        HTTPException:
            - 404: If the device is not found.
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/set_device_state" \
             -H "Content-Type: multipart/form-data" \
             -F "device_id=TAG001" \
             -F "new_state=inactive"
        ```
        Response:
        ```json
        {"message": "Device state updated successfully"}
        ```

    Use Case:
        - Mark a tag as inactive when an employee is on leave.
        - Set a beacon to active after it is redeployed post-maintenance.

    Hint:
        - Use `/get_device_by_id/{device_id}` to verify the device's current state before updating.
        - The `new_state` value "active" clears the end date, while any other value sets it to the current time.
        - Supports form data for compatibility with React frontend forms.
    """
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
    """
    Add a new device type to the ParcoRTLS system.

    This endpoint creates a new device type (e.g., Tag, Beacon) using the `usp_device_type_add` stored procedure. Device types categorize devices for organizational and filtering purposes.

    Args:
        request (DeviceTypeRequest): The request body containing the device type details.
            - description (str): The name or description of the device type (e.g., "Tag"). Required.

    Returns:
        dict: A JSON response indicating success and the new type ID.
            - message (str): Success message ("Device type added successfully").
            - type_id (int): The ID of the newly created device type.

    Raises:
        HTTPException:
            - 400: If the device type description already exists.
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/add_device_type" \
             -H "Content-Type: application/json" \
             -d '{"description": "Tag"}'
        ```
        Response:
        ```json
        {"message": "Device type added successfully", "type_id": 1}
        ```

    Use Case:
        - Add a new device type ("Patient Tag") to support tracking patients in a hospital campus.
        - Create a custom device type for a specific use case (e.g., "Vehicle Tracker").

    Hint:
        - Check existing types with `/list_device_types` to avoid duplicating descriptions.
        - The returned `type_id` is used when adding devices via `/add_device`.
    """
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

@router.delete("/delete_device_type/{type_id}")
async def delete_device_type(type_id: int):
    """
    Delete a device type from the ParcoRTLS system.

    This endpoint removes a device type by its ID using the `usp_device_type_delete` stored procedure. It is used to remove obsolete or unused device types.

    Args:
        type_id (int): The ID of the device type to delete (e.g., 1). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device type deleted successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_device_type/1"
        ```
        Response:
        ```json
        {"message": "Device type deleted successfully"}
        ```

    Use Case:
        - Remove an obsolete device type ("Temporary Tag") that is no longer needed.
        - Clean up unused device types during system maintenance.

    Hint:
        - Ensure no devices are using the `type_id` (check `/get_device_by_type/{device_type}`) before deletion to avoid database constraints.
        - A return value of 0 from the stored procedure indicates the type was already deleted, which is treated as success.
    """
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

@router.put("/edit_device_type")
async def edit_device_type(type_id: int, request: DeviceTypeRequest):
    """
    Update an existing device type's description.

    This endpoint modifies the description of a device type using the `usp_device_type_edit` stored procedure. It is used to correct or update type names for clarity or consistency.

    Args:
        type_id (int): The ID of the device type to update (e.g., 1). Required.
        request (DeviceTypeRequest): The request body containing the updated type details.
            - description (str): The updated description of the device type (e.g., "Staff Tag"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device type edited successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/edit_device_type?type_id=1" \
             -H "Content-Type: application/json" \
             -d '{"description": "Staff Tag"}'
        ```
        Response:
        ```json
        {"message": "Device type edited successfully"}
        ```

    Use Case:
        - Rename a device type from "Tag" to "Staff Tag" for better clarity.
        - Update a type description to reflect a new use case.

    Hint:
        - Verify the `type_id` exists using `/list_device_types` before updating.
    """
    result = await call_stored_procedure("maint", "usp_device_type_edit", type_id, request.description)
    if result and isinstance(result, (int, str)):
        return {"message": "Device type edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit device type")

@router.get("/list_device_types")
async def list_device_types():
    """
    Retrieve a list of all device types in the ParcoRTLS system.

    This endpoint fetches all device types (e.g., Tag, Beacon) using the `usp_device_type_list` stored procedure. It is useful for populating UI elements or validating device type IDs.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing device type details.
            - i_typ_dev (int): Device type ID.
            - x_dsc_dev_typ (str): Device type description (e.g., "Tag").
            - d_crt (datetime): Creation date.
            - d_udt (datetime): Last update date.

    Raises:
        HTTPException:
            - 404: If no device types are found.
            - 500: If a database error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_device_types"
        ```
        Response:
        ```json
        [
            {"i_typ_dev": 1, "x_dsc_dev_typ": "Tag", "d_crt": "2025-04-26T10:00:00", "d_udt": "2025-04-26T10:00:00"},
            {"i_typ_dev": 2, "x_dsc_dev_typ": "Beacon", "d_crt": "2025-04-25T09:00:00", "d_udt": "2025-04-25T09:00:00"}
        ]
        ```

    Use Case:
        - Populate a dropdown in the React frontend for selecting device types when adding a new device.
        - Validate device type IDs before creating or updating devices.

    Hint:
        - Use this endpoint to ensure valid `device_type` values are used in `/add_device` or `/edit_device`.
    """
    result = await call_stored_procedure("maint", "usp_device_type_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device types found")

@router.post("/assign_device_to_zone")
async def assign_device_to_zone(device_id: str = Form(...), entity_id: str = Form(...), reason_id: int = Form(...)):
    """
    Assign a device to a zone or entity in the ParcoRTLS system.

    This endpoint creates an assignment between a device and an entity (e.g., a zone or person) using the `usp_assign_dev_add` stored procedure. It validates the device, entity, and reason before creating the assignment, ensuring proper tracking within the system.

    Args:
        device_id (str): The ID of the device to assign (e.g., "TAG001"). Required.
        entity_id (str): The ID of the entity (e.g., zone or person) to assign the device to (e.g., "ZONE001"). Required.
        reason_id (int): The ID of the assignment reason (e.g., 1 for "Location Tracking"). Required.

    Returns:
        dict: A JSON response indicating success and the assignment ID.
            - message (str): Success message ("Device assigned successfully").
            - assignment_id (str): The ID of the newly created assignment.

    Raises:
        HTTPException:
            - 400: If the reason ID is invalid.
            - 404: If the device or entity is not found.
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/assign_device_to_zone" \
             -H "Content-Type: multipart/form-data" \
             -F "device_id=TAG001" \
             -F "entity_id=ZONE001" \
             -F "reason_id=1"
        ```
        Response:
        ```json
        {"message": "Device assigned successfully", "assignment_id": "101"}
        ```

    Use Case:
        - Assign a tag to a zone ("ZONE001") for location tracking in a Zone L1 campus.
        - Link a beacon to a department entity for enhanced positioning accuracy.

    Hint:
        - Verify `device_id` and `entity_id` exist using `/get_device_by_id/{device_id}` and `/get_entity_by_id/{entity_id}` (from `entity.py`) before assigning.
        - Retrieve valid `reason_id` values from `/list_assignment_reasons` (from `entity.py`).
        - Supports form data for compatibility with React frontend forms.
    """
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

@router.delete("/delete_device_assignment/{assignment_id}")
async def delete_device_assignment(assignment_id: int):
    """
    Delete a specific device assignment.

    This endpoint removes a device assignment (e.g., a tag's association with a zone) using the `usp_assign_dev_delete` stored procedure. It is used to dissolve assignments when they are no longer needed.

    Args:
        assignment_id (int): The ID of the assignment to delete (e.g., 101). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device assignment deleted successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_device_assignment/101"
        ```
        Response:
        ```json
        {"message": "Device assignment deleted successfully"}
        ```

    Use Case:
        - Remove a tag's assignment to a zone after it is reassigned to a new zone.
        - Dissolve a beacon's assignment to an entity after it is decommissioned.

    Hint:
        - Verify the `assignment_id` exists using `/list_device_assignments_by_device/{device_id}` before deletion.
        - The stored procedure may update the assignment's end date rather than deleting it, depending on implementation (see version 0.1.36 changelog).
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_delete", assignment_id)
    if result and isinstance(result, list) and result:
        message = result[0].get("usp_assign_dev_delete")
        if message == "Assignment end date updated successfully":
            return {"message": "Device assignment deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete device assignment")

@router.delete("/delete_all_device_assignments")
async def delete_all_device_assignments():
    """
    Delete all device assignments in the ParcoRTLS system.

    This endpoint removes all device assignments using the `usp_assign_dev_delete_all` stored procedure. It is used to reset all device-entity associations, typically during major system maintenance or reconfiguration.

    Args:
        None

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("All device assignments deleted successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_all_device_assignments"
        ```
        Response:
        ```json
        {"message": "All device assignments deleted successfully"}
        ```

    Use Case:
        - Clear all device assignments during a system-wide reset or migration.
        - Remove all tag-zone associations before reconfiguring a campus's zone structure.

    Hint:
        - Use this endpoint cautiously, as it affects all devices and may disrupt tracking operations.
        - Consider using `/end_all_device_assignments` to preserve historical data instead of deleting assignments.
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_delete_all")
    if result and isinstance(result, (int, str)):
        return {"message": "All device assignments deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete all device assignments")

@router.delete("/delete_device_assignments_by_entity/{entity_id}")
async def delete_device_assignments_by_entity(entity_id: str):
    """
    Delete all device assignments for a specific entity.

    This endpoint removes all device assignments associated with a given entity (e.g., a zone or person) using the `usp_assign_dev_delete_all_by_ent` stored procedure. It is used to clear assignments when an entity is decommissioned or reassigned.

    Args:
        entity_id (str): The ID of the entity whose assignments are to be deleted (e.g., "ZONE001"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device assignments deleted successfully for entity").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_device_assignments_by_entity/ZONE001"
        ```
        Response:
        ```json
        {"message": "Device assignments deleted successfully for entity"}
        ```

    Use Case:
        - Clear all tag assignments for a zone ("ZONE001") that is being reconfigured.
        - Remove device assignments for a department entity after it is dissolved.

    Hint:
        - Verify the `entity_id` exists using `/get_entity_by_id/{entity_id}` (from `entity.py`) before deletion.
        - Use `/end_all_device_assignments` if historical assignment data needs to be preserved.
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_delete_all_by_ent", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignments deleted successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to delete device assignments for entity")

@router.put("/edit_device_assignment")
async def edit_device_assignment(request: AssignDeviceEditRequest):
    """
    Update an existing device assignment.

    This endpoint modifies a device assignment (e.g., changing the device, entity, or reason) using the `usp_assign_dev_edit` stored procedure. It is used to update assignment details when reassigning devices or correcting errors.

    Args:
        request (AssignDeviceEditRequest): The request body containing updated assignment details.
            - assignment_id (int): The ID of the assignment to update (e.g., 101). Required.
            - device_id (str): The updated device ID (e.g., "TAG001"). Required.
            - entity_id (str): The updated entity ID (e.g., "ZONE001"). Required.
            - reason_id (int): The updated reason ID (e.g., 1 for "Location Tracking"). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device assignment edited successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/edit_device_assignment" \
             -H "Content-Type: application/json" \
             -d '{"assignment_id": 101, "device_id": "TAG001", "entity_id": "ZONE002", "reason_id": 1}'
        ```
        Response:
        ```json
        {"message": "Device assignment edited successfully"}
        ```

    Use Case:
        - Reassign a tag from one zone ("ZONE001") to another ("ZONE002") in a Zone L1 campus.
        - Update the reason for a beacon's assignment after a change in its purpose.

    Hint:
        - Verify the `assignment_id` exists using `/list_device_assignments_by_device/{device_id}` before updating.
        - Ensure `device_id`, `entity_id`, and `reason_id` are valid using appropriate endpoints (e.g., `/get_device_by_id/{device_id}`, `/get_entity_by_id/{entity_id}`, `/list_assignment_reasons`).
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_edit", request.assignment_id, request.device_id, request.entity_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit device assignment")

@router.post("/end_device_assignment")
async def end_device_assignment(request: AssignDeviceEndRequest):
    """
    End a specific device assignment.

    This endpoint marks a device assignment as ended using the `usp_assign_dev_end` stored procedure. It is used to terminate an assignment without deleting it, preserving historical data.

    Args:
        request (AssignDeviceEndRequest): The request body containing the assignment ID.
            - assignment_id (int): The ID of the assignment to end (e.g., 101). Required.

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("Device assignment ended successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/end_device_assignment" \
             -H "Content-Type: application/json" \
             -d '{"assignment_id": 101}'
        ```
        Response:
        ```json
        {"message": "Device assignment ended successfully"}
        ```

    Use Case:
        - End a tag's assignment to a zone when it is reassigned to a new zone.
        - Terminate a beacon's assignment to an entity when it is taken offline.

    Hint:
        - Use this endpoint to maintain historical records instead of deleting assignments with `/delete_device_assignment/{assignment_id}`.
        - Verify the `assignment_id` exists using `/list_device_assignments_by_device/{device_id}`.
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_end", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end device assignment")

@router.post("/end_all_device_assignments")
async def end_all_device_assignments():
    """
    End all device assignments in the ParcoRTLS system.

    This endpoint marks all device assignments as ended using the `usp_assign_dev_end_all` stored procedure. It is used to terminate all device-entity associations while preserving historical data, typically during system reconfiguration.

    Args:
        None

    Returns:
        dict: A JSON response indicating success.
            - message (str): Success message ("All device assignments ended successfully").

    Raises:
        HTTPException:
            - 500: If the database operation fails or the stored procedure returns an unexpected result.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/end_all_device_assignments"
        ```
        Response:
        ```json
        {"message": "All device assignments ended successfully"}
        ```

    Use Case:
        - End all tag assignments during a system-wide reset while retaining historical data.
        - Terminate all beacon assignments before reconfiguring zone associations.

    Hint:
        - Use this endpoint instead of `/delete_all_device_assignments` if historical data needs to be retained.
        - Ensure all affected devices are reassigned as needed after calling this endpoint.
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_end_all")
    if result and isinstance(result, (int, str)):
        return {"message": "All device assignments ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end all device assignments")

@router.get("/list_device_assignments")
async def list_device_assignments(include_ended: bool = False):
    """
    Retrieve a list of all device assignments.

    This endpoint fetches all device assignments (active or ended) using the `usp_assign_dev_list` stored procedure. It is useful for auditing or displaying device-entity relationships in the React frontend.

    Args:
        include_ended (bool, optional): Whether to include ended assignments. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing assignment details.
            - i_asn_dev (int): Assignment ID.
            - x_id_dev (str): Device ID.
            - x_id_ent (str): Entity ID.
            - i_rsn (int): Assignment reason ID.
            - d_bgn (datetime): Assignment start date.
            - d_end (datetime or None): Assignment end date (null if active).

    Raises:
        HTTPException:
            - 404: If no assignments are found.
            - 500: If a database error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_device_assignments?include_ended=true"
        ```
        Response:
        ```json
        [
            {
                "i_asn_dev": 101,
                "x_id_dev": "TAG001",
                "x_id_ent": "ZONE001",
                "i_rsn": 1,
                "d_bgn": "2025-04-26T10:00:00",
                "d_end": null
            },
            {
                "i_asn_dev": 102,
                "x_id_dev": "TAG002",
                "x_id_ent": "ZONE002",
                "i_rsn": 2,
                "d_bgn": "2025-04-25T09:00:00",
                "d_end": "2025-04-26T12:00:00"
            }
        ]
        ```

    Use Case:
        - Display all active device assignments in the React frontend for administrative oversight.
        - Generate a report of all assignments, including ended ones, for auditing.

    Hint:
        - Set `include_ended=True` to retrieve historical assignments, useful for tracking changes over time.
        - Cross-reference `x_id_ent` with `/get_entity_by_id/{entity_id}` (from `entity.py`) for entity details.
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_list", include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found")

@router.get("/list_device_assignments_by_entity/{entity_id}")
async def list_device_assignments_by_entity(entity_id: str, include_ended: bool = False):
    """
    Retrieve all device assignments for a specific entity.

    This endpoint fetches assignments where the specified entity (e.g., a zone or person) is associated with devices, using the `usp_assign_dev_list_by_entity` stored procedure. It is used to view all devices linked to an entity.

    Args:
        entity_id (str): The ID of the entity to filter by (e.g., "ZONE001"). Required.
        include_ended (bool, optional): Whether to include ended assignments. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing assignment details.
            - i_asn_dev (int): Assignment ID.
            - x_id_dev (str): Device ID.
            - x_id_ent (str): Entity ID.
            - i_rsn (int): Assignment reason ID.
            - d_bgn (datetime): Assignment start date.
            - d_end (datetime or None): Assignment end date (null if active).

    Raises:
        None: Returns an empty list if no assignments are found or if an error occurs, preventing frontend crashes.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_device_assignments_by_entity/ZONE001?include_ended=true"
        ```
        Response:
        ```json
        [
            {
                "i_asn_dev": 101,
                "x_id_dev": "TAG001",
                "x_id_ent": "ZONE001",
                "i_rsn": 1,
                "d_bgn": "2025-04-26T10:00:00",
                "d_end": null
            }
        ]
        ```

    Use Case:
        - List all tags assigned to a zone ("ZONE001") in the React frontend for location tracking.
        - View all beacons assigned to a department entity for maintenance planning.

    Hint:
        - Verify the `entity_id` exists using `/get_entity_by_id/{entity_id}` (from `entity.py`) before querying.
        - The empty list return on error aligns with version 0.1.38 changes to improve frontend compatibility.
    """
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

@router.get("/list_device_assignments_by_device/{device_id}")
async def list_device_assignments_by_device(device_id: str, include_ended: bool = False):
    """
    Retrieve all assignments for a specific device.

    This endpoint fetches all assignments where the specified device is involved, using the `usp_assign_dev_list_by_id` stored procedure. It is used to view the entities (e.g., zones, people) a device is associated with.

    Args:
        device_id (str): The ID of the device to filter by (e.g., "TAG001"). Required.
        include_ended (bool, optional): Whether to include ended assignments. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing assignment details.
            - i_asn_dev (int): Assignment ID.
            - x_id_dev (str): Device ID.
            - x_id_ent (str): Entity ID.
            - i_rsn (int): Assignment reason ID.
            - d_bgn (datetime): Assignment start date.
            - d_end (datetime or None): Assignment end date (null if active).

    Raises:
        HTTPException:
            - 404: If no assignments are found for the device.
            - 500: If a database error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_device_assignments_by_device/TAG001?include_ended=true"
        ```
        Response:
        ```json
        [
            {
                "i_asn_dev": 101,
                "x_id_dev": "TAG001",
                "x_id_ent": "ZONE001",
                "i_rsn": 1,
                "d_bgn": "2025-04-26T10:00:00",
                "d_end": null
            }
        ]
        ```

    Use Case:
        - View all zones a tag ("TAG001") is assigned to for tracking purposes.
        - Check the assignment history of a beacon to understand its usage.

    Hint:
        - Verify the `device_id` exists using `/get_device_by_id/{device_id}` before querying.
        - Use `include_ended=True` for historical analysis of the device's assignments.
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_id", device_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for device")

@router.get("/list_device_assignments_by_reason/{reason_id}")
async def list_device_assignments_by_reason(reason_id: int, include_ended: bool = False):
    """
    Retrieve all device assignments for a specific reason.

    This endpoint fetches assignments associated with a given reason using the `usp_assign_dev_list_by_reason` stored procedure. It is used to analyze assignments by their purpose, such as tracking or maintenance.

    Args:
        reason_id (int): The ID of the assignment reason (e.g., 1 for "Location Tracking"). Required.
        include_ended (bool, optional): Whether to include ended assignments. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing assignment details.
            - i_asn_dev (int): Assignment ID.
            - x_id_dev (str): Device ID.
            - x_id_ent (str): Entity ID.
            - i_rsn (int): Assignment reason ID.
            - d_bgn (datetime): Assignment start date.
            - d_end (datetime or None): Assignment end date (null if active).

    Raises:
        HTTPException:
            - 404: If no assignments are found for the reason.
            - 500: If a database error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/list_device_assignments_by_reason/1?include_ended=true"
        ```
        Response:
        ```json
        [
            {
                "i_asn_dev": 101,
                "x_id_dev": "TAG001",
                "x_id_ent": "ZONE001",
                "i_rsn": 1,
                "d_bgn": "2025-04-26T10:00:00",
                "d_end": null
            }
        ]
        ```

    Use Case:
        - List all assignments with reason "Location Tracking" for operational reporting.
        - Analyze assignments for a specific reason to understand device usage patterns.

    Hint:
        - Retrieve valid `reason_id` values from `/list_assignment_reasons` (from `entity.py`) before querying.
        - Use `include_ended=True` for comprehensive historical analysis.
    """
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_reason", reason_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for reason")

@router.get("/zone_list")
async def list_zones():
    """
    Retrieve a list of all zones in the ParcoRTLS system.

    This endpoint fetches all zones using the `usp_zone_list` stored procedure. It is used to provide a list of zones for assignment, mapping, or display in the React frontend.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing zone details.
            - i_zn (int): Zone ID.
            - x_nm_zn (str): Zone name (e.g., "Main Lobby").
            - i_typ_zn (int): Zone type ID.
            - i_map (int or None): Associated map ID.
            - d_crt (datetime): Creation date.
            - d_udt (datetime): Last update date.

    Raises:
        HTTPException:
            - 404: If no zones are found.
            - 500: If a database error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/zone_list"
        ```
        Response:
        ```json
        [
            {
                "i_zn": 1,
                "x_nm_zn": "Main Lobby",
                "i_typ_zn": 1,
                "i_map": 101,
                "d_crt": "2025-04-26T10:00:00",
                "d_udt": "2025-04-26T10:00:00"
            }
        ]
        ```

    Use Case:
        - Populate a dropdown in the React frontend for selecting zones when assigning devices.
        - Generate a report of all zones for campus planning.

    Hint:
        - Use this endpoint to retrieve valid `zone_id` values for `/add_device` or `/edit_device`.
        - The `i_map` field can be used to link zones to maps in the Build Out Tool.
    """
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
    """
    Retrieve all zones with their associated map IDs for the Build Out Tool.

    This endpoint fetches all zones and their map IDs from the `zones` table using a raw SQL query in the `maint` schema. It is specifically designed for the Build Out Tool, which uses this data to associate zones with maps for visualization and configuration in the ParcoRTLS system. The endpoint supports campus planning and zone management by providing essential mapping information for the React frontend running at http://192.168.210.226:3000.

    Args:
        None

    Returns:
        list: A list of dictionaries, each containing zone and map details.
            - i_zn (int): Zone ID (e.g., 1).
            - x_nm_zn (str): Zone name (e.g., "Main Lobby").
            - i_typ_zn (int): Zone type ID (e.g., 1 for indoor zone).
            - i_map (int or None): Associated map ID (e.g., 101 for a specific map).

    Raises:
        HTTPException:
            - 404: If no zones are found in the database.
            - 500: If a database error or unexpected error occurs during the query.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/zones_with_maps"
        ```
        Response:
        ```json
        [
            {
                "i_zn": 1,
                "x_nm_zn": "Main Lobby",
                "i_typ_zn": 1,
                "i_map": 101
            },
            {
                "i_zn": 2,
                "x_nm_zn": "Ward A",
                "i_typ_zn": 2,
                "i_map": 102
            }
        ]
        ```

    Use Case:
        - Populate the Build Out Tool in the React frontend with zone and map associations for configuring campus layouts.
        - Generate a report of all zones and their map IDs for planning Zone L1 campus expansions.
        - Support zone visualization in the frontend by linking zones to their respective maps.

    Hint:
        - Use this endpoint in conjunction with `/zone_list` to get additional zone details like creation and update dates.
        - The `i_map` field links to map data; ensure maps are configured in the system to utilize this data effectively.
        - For Zone L1 campuses, this endpoint helps verify zone-map associations for accurate device tracking.
        - Log errors are captured for debugging; check logs at `/var/log` if a 500 error occurs.
    """
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