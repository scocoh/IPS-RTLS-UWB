# Name: history.py
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
routes/history.py
Historical data and positioning endpoints for ParcoRTLS FastAPI application.
// # VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/history.py 0P.10B.02
// # Changelog:
// # - 0P.10B.02 (2025-04-26): Enhanced endpoint docstrings with detailed descriptions, parameters, return values, examples, use cases, and error handling.
// # - 0P.10B.01 (2025-03-16): Initial implementation of history routes.
// #
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError
from models import PositionRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["history"])

@router.get("/get_recent_device_positions/{device_id}")
async def get_recent_device_positions(device_id: str):
    """
    Retrieve recent position data for a specific device in the ParcoRTLS system.

    This endpoint queries the `hist_r` schema's `usp_location_by_id` stored procedure to fetch the most recent
    position records for a given device. It is used to track the current or recent location of a device (e.g., a tag
    or asset) within the real-time location system.

    Parameters:
        device_id (str): The unique identifier of the device (e.g., tag ID or asset ID). Required.

    Returns:
        list: A list of position records, each containing fields like `device_id`, `x`, `y`, `z`, and `timestamp`.
              The exact structure depends on the `usp_location_by_id` stored procedure output.
              Example: [{"device_id": "TAG123", "x": 10.5, "y": 20.3, "z": 1.2, "timestamp": "2025-04-26T10:00:00"}]

    Raises:
        HTTPException (404): If no recent positions are found for the device.
        HTTPException (500): If a database error occurs (e.g., connection failure or stored procedure error).

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_recent_device_positions/TAG123"
        ```
        Response:
        ```json
        [
            {"device_id": "TAG123", "x": 10.5, "y": 20.3, "z": 1.2, "timestamp": "2025-04-26T10:00:00"},
            {"device_id": "TAG123", "x": 10.6, "y": 20.4, "z": 1.2, "timestamp": "2025-04-26T10:00:01"}
        ]
        ```

    Use Case:
        - **Scenario**: A facility manager needs to check the latest location of a specific asset (e.g., a medical device with tag ID "TAG123") on a campus.
        - **Application**: The React frontend calls this endpoint to display the device's recent positions on a map, helping the manager locate the asset in real-time.

    Hint:
        - This endpoint is useful for Zone L1 zones (e.g., campus-level tracking) to verify if a tag is within a specific area.
        - For performance, ensure the `usp_location_by_id` stored procedure is optimized, as it may query large datasets.
    """
    try:
        result = await call_stored_procedure("hist_r", "usp_location_by_id", device_id)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No recent positions found")
    except DatabaseError as e:
        logger.error(f"Database error fetching positions: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.post("/insert_position")
async def insert_position(device_id: str = Form(...), x: float = Form(...), y: float = Form(...), z: float = Form(...)):
    """
    Insert a new position record for a device in the ParcoRTLS system.

    This endpoint records a device's position (x, y, z coordinates) at a specific timestamp by calling the `hist_r`
    schema's `usp_position_insert` stored procedure. It first verifies the device's existence in the `maint` schema
    using `usp_device_select_by_id`. This is critical for logging device movements in the RTLS system.

    Parameters:
        device_id (str): The unique identifier of the device (e.g., tag ID or asset ID). Required.
        x (float): The x-coordinate of the device's position (e.g., in meters). Required.
        y (float): The y-coordinate of the device's position (e.g., in meters). Required.
        z (float): The z-coordinate of the device's position (e.g., in meters, for height). Required.

    Returns:
        dict: A JSON object indicating success.
              Example: {"message": "Position inserted successfully"}

    Raises:
        HTTPException (404): If the device is not found in the `maint` schema.
        HTTPException (500): If the position insertion fails or a database/general error occurs.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/insert_position" \
             -F "device_id=TAG123" \
             -F "x=10.5" \
             -F "y=20.3" \
             -F "z=1.2"
        ```
        Response:
        ```json
        {"message": "Position inserted successfully"}
        ```

    Use Case:
        - **Scenario**: An RTLS gateway detects a tag's new position and sends it to the backend for storage.
        - **Application**: This endpoint is used by the ParcoRTLS middleware to log real-time position updates, enabling historical tracking and analytics.

    Hint:
        - Ensure the device ID exists in the `maint` schema before calling this endpoint to avoid 404 errors.
        - The `start_time` and `end_time` are set to the current timestamp, assuming instantaneous position updates.
        - For high-frequency updates, consider batching position inserts to optimize database performance.
    """
    start_time = datetime.now()
    end_time = start_time
    request = PositionRequest(device_id=device_id, start_time=start_time, end_time=end_time, x=x, y=y, z=z)
    try:
        device = await call_stored_procedure("maint", "usp_device_select_by_id", request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found in ParcoRTLSMaint")
        result = await call_stored_procedure(
            "hist_r", "usp_position_insert",
            request.device_id, request.start_time, request.end_time, request.x, request.y, request.z
        )
        if result and isinstance(result, (int, str)):
            return {"message": "Position inserted successfully"}
        raise HTTPException(status_code=500, detail="Failed to insert position")
    except DatabaseError as e:
        logger.error(f"Database error inserting position: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error inserting position: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_history_by_device/{device_id}")
async def get_history_by_device(device_id: str, start_date: datetime, end_date: datetime):
    """
    Retrieve historical position data for a device within a specified time range in the ParcoRTLS system.

    This endpoint queries the `hist_r` schema's `usp_history_by_id` stored procedure to fetch position records
    for a device between the given start and end dates. It is used for analyzing a device's movement history,
    such as tracking an asset's path over time.

    Parameters:
        device_id (str): The unique identifier of the device (e.g., tag ID or asset ID). Required.
        start_date (datetime): The start of the time range for the history query (e.g., "2025-04-26T00:00:00"). Required.
        end_date (datetime): The end of the time range for the history query (e.g., "2025-04-26T23:59:59"). Required.

    Returns:
        list: A list of position records, each containing fields like `device_id`, `x`, `y`, `z`, and `timestamp`.
              The exact structure depends on the `usp_history_by_id` stored procedure output.
              Example: [{"device_id": "TAG123", "x": 10.5, "y": 20.3, "z": 1.2, "timestamp": "2025-04-26T10:00:00"}]

    Raises:
        HTTPException (404): If no history records are found for the device in the specified time range.
        HTTPException (500): If a database error occurs (e.g., connection failure or stored procedure error).

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_history_by_device/TAG123?start_date=2025-04-26T00:00:00&end_date=2025-04-26T23:59:59"
        ```
        Response:
        ```json
        [
            {"device_id": "TAG123", "x": 10.5, "y": 20.3, "z": 1.2, "timestamp": "2025-04-26T10:00:00"},
            {"device_id": "TAG123", "x": 10.6, "y": 20.4, "z": 1.2, "timestamp": "2025-04-26T10:01:00"}
        ]
        ```

    Use Case:
        - **Scenario**: A security team needs to review the movement history of a tagged asset over the past day to investigate an incident.
        - **Application**: The React frontend calls this endpoint to fetch and visualize the device's path on a map, aiding in incident analysis.

    Hint:
        - Ensure `start_date` and `end_date` are in a valid ISO 8601 format to avoid parsing errors.
        - For large time ranges, the query may return a large dataset; consider implementing pagination or limiting the time range.
        - This endpoint is ideal for generating reports or visualizing movement patterns in Zone L1 zones.
    """
    try:
        result = await call_stored_procedure("hist_r", "usp_history_by_id", device_id, start_date, end_date)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No history found for device")
    except DatabaseError as e:
        logger.error(f"Database error fetching history: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)