"""
Version: 250226 app.py Version 0P.7B.33 (Expanded Stored Procedures, Optimized Performance, VB.NET Collection Integration, Comprehensive Device/Zone/History/Trigger/Text/Assignment/Entity/Region/Resource Management for ParcoRTLSMaint/HistR/Data, Fixed 500 Errors, Connection Pool Tuning, Enhanced Timeout Handling, Corrected Device/Assignments/Zones)

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24, Michael Farnsworth, and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
import asyncpg
import paho.mqtt.publish as publish
import logging
import asyncio
import json
from typing import List, Dict, Optional, Union
from database.db_functions import call_stored_procedure, DatabaseError
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Parco RTLS API", version="0P.7B.33", docs_url="/docs")

MQTT_BROKER = "127.0.0.1"

# PostgreSQL Database Configuration (async)
DB_CONFIGS_ASYNC = {
    "maint": {
        "database": "ParcoRTLSMaint",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "data": {
        "database": "ParcoRTLSData",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_r": {
        "database": "ParcoRTLSHistR",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_p": {
        "database": "ParcoRTLSHistP",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    },
    "hist_o": {
        "database": "ParcoRTLSHistO",
        "user": "parcoadmin",
        "password": "parcoMCSE04106!",
        "host": "192.168.210.226",
        "port": 5432
    }
}

async def get_async_db_pool(db_type: str = "maint"):
    """Establish an async database connection pool with optimized settings and increased retries for connection issues."""
    max_retries = 10  # Increased retries to handle "too many clients already" more robustly
    retry_delay = 5  # Increased delay to allow database to recover
    for attempt in range(max_retries):
        try:
            pool = await asyncpg.create_pool(
                **DB_CONFIGS_ASYNC[db_type],
                max_size=20,  # Reduced to prevent overwhelming PostgreSQL, adjust based on server capacity
                min_size=2,
                timeout=30
            )
            # Test the connection by executing a simple query
            async with pool.acquire() as connection:
                await connection.execute("SELECT 1")
            return pool
        except asyncpg.TooManyConnectionsError as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to connect to {db_type}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached for {db_type}: {str(e)}")
                if db_type in ["data", "hist_r", "hist_p", "hist_o"]:
                    logger.warning(f"Database {db_type} connection failed due to too many clients, falling back to maintenance-only mode.")
                    return None  # Return None to indicate connection failure, handled by caller
                raise HTTPException(status_code=503, detail=f"Failed to connect to {db_type} after retries: too many clients")
        except asyncpg.PostgresError as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to connect to {db_type}: {str(e)}")
            if "database does not exist" in str(e) or "no such database" in str(e):
                logger.warning(f"Database {db_type} may be empty or missing. Falling back to maintenance-only mode.")
                return None  # Return None to indicate empty database, handled by caller
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached for {db_type}: {str(e)}")
                raise HTTPException(status_code=503, detail=f"Failed to connect to {db_type} after retries")
    raise HTTPException(status_code=503, detail=f"Failed to connect to {db_type}")

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and SDK collections on startup, handling empty or inaccessible databases."""
    logger.info("Initializing async database connections and SDK collections...")
    app.state.async_db_pools = {}
    for db_type in DB_CONFIGS_ASYNC.keys():
        try:
            pool = await get_async_db_pool(db_type)
            if pool:
                app.state.async_db_pools[db_type] = pool
            else:
                logger.warning(f"Database {db_type} is empty, inaccessible, or has too many clients, skipping initialization.")
        except HTTPException as e:
            logger.error(f"Failed to initialize pool for {db_type}: {str(e)}")
    # Placeholder for SDKCollection initialization (to be expanded in future)
    app.state.sdk_clients = []  # Will be replaced with SDKCollection class
    logger.info("Database connections and SDK collections established.")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections and SDK clients on shutdown."""
    logger.info("Closing async database connections and SDK clients...")
    if hasattr(app.state, "async_db_pools"):
        for pool in app.state.async_db_pools.values():
            await pool.close()
    # Cleanup for SDK clients (to be expanded)
    if hasattr(app.state, "sdk_clients"):
        for client in app.state.sdk_clients:
            if hasattr(client, "close") and callable(client.close):
                await client.close()
    logger.info("All connections and clients closed.")

@app.get("/")
def root():
    """Return a simple health check for the FastAPI application."""
    return {"message": "FastAPI is running!"}

@app.get("/status")
async def system_status():
    """Asynchronously check the status of FastAPI and Mosquitto services."""
    try:
        fastapi_status = await asyncio.create_subprocess_exec(
            "systemctl", "is-active", "fastapi",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        fastapi_output, _ = await fastapi_status.communicate()
        fastapi_running = fastapi_output.decode().strip() == "active"

        mqtt_status = await asyncio.create_subprocess_exec(
            "systemctl", "is-active", "mosquitto",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        mqtt_output, _ = await mqtt_status.communicate()
        mqtt_running = mqtt_output.decode().strip() == "active"

        return {
            "FastAPI": "Running ✅" if fastapi_running else "Stopped ❌",
            "Mosquitto": "Running ✅" if mqtt_running else "Stopped ❌"
        }
    except Exception as e:
        logger.error(f"Error checking system status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check system status")

# Existing endpoints from Version 0P.7B.32 (preserved, with fixes)
@app.get("/api/get_devices")
async def get_devices():
    """Fetch all devices from ParcoRTLSData with debugging (limited to 5 for now), handling empty database."""
    try:
        if not app.state.async_db_pools.get("data"):
            raise HTTPException(status_code=503, detail="ParcoRTLSData database is empty or unavailable")
        async with app.state.async_db_pools["data"].acquire() as connection:
            query = "SELECT * FROM devices LIMIT 5;"
            devices = await connection.fetch(query)
            logger.info("Retrieved Devices: %s", devices)
            return {"devices": [dict(device) for device in devices]}
    except asyncpg.PostgresError as e:
        logger.error("Error fetching devices: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get_parents")
async def get_parents():
    """Fetch all top-level parent zones from ParcoRTLSMaint."""
    try:
        async with app.state.async_db_pools["maint"].acquire() as connection:
            query = "SELECT i_zn, i_typ_zn, x_nm_zn FROM public.zones WHERE i_pnt_zn IS NULL ORDER BY i_zn DESC;"
            parents = await connection.fetch(query)
            return {"parents": [dict(parent) for parent in parents]}
    except asyncpg.PostgresError as e:
        logger.error("Error fetching parents: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get_children/{parent_id}")
async def get_children(parent_id: int):
    """Fetch all child zones of a selected parent zone."""
    try:
        async with app.state.async_db_pools["maint"].acquire() as connection:
            query = "SELECT * FROM usp_zone_children_select($1);"
            children = await connection.fetchval(query, parent_id)
            if not children:
                return {"children": []}
            if isinstance(children, str):
                children = json.loads(children)
            return {"children": children if isinstance(children, list) else [children]}
    except asyncpg.PostgresError as e:
        logger.error("Error fetching children: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get_map/{zone_id}", response_class=Response)
async def get_map(zone_id: int):
    """Fetch the map image associated with a selected zone as a downloadable file."""
    try:
        async with app.state.async_db_pools["maint"].acquire() as connection:
            zone_query = "SELECT i_map FROM zones WHERE i_zn = $1;"
            i_map = await connection.fetchval(zone_query, zone_id)
            if i_map is None:
                raise HTTPException(status_code=404, detail=f"No zone found for zone_id={zone_id}")

            map_query = "SELECT img_data FROM maps WHERE i_map = $1;"
            img_data = await connection.fetchval(map_query, i_map)
            if img_data is None:
                raise HTTPException(status_code=404, detail=f"No map found for map_id={i_map}")

            format_query = "SELECT x_format FROM maps WHERE i_map = $1;"
            file_format = await connection.fetchval(format_query, i_map) or "image/png"

            return Response(
                content=img_data,
                media_type=file_format,  # e.g., "image/png"
                headers={
                    "Content-Disposition": f"attachment; filename=map_zone_{zone_id}.{file_format.split('/')[-1]}"
                }
            )
    except asyncpg.PostgresError as e:
        logger.error("Error fetching map: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get_zone_vertices/{zone_id}")
async def get_zone_vertices(zone_id: int):
    """Fetch vertices for a selected zone to draw its boundary."""
    try:
        async with app.state.async_db_pools["maint"].acquire() as connection:
            query = "SELECT * FROM usp_zone_vertices_select_by_zone($1);"
            vertices = await connection.fetch(query, zone_id)
            return {"vertices": [dict(vertex) for vertex in vertices]}
    except asyncpg.PostgresError as e:
        logger.error("Error fetching zone vertices: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/{trigger_name}")
async def trigger_event(trigger_name: str):
    """Publish a trigger event to the MQTT broker."""
    try:
        publish.single("home/rtls/trigger", trigger_name, hostname=MQTT_BROKER)
        return {"message": f"Trigger {trigger_name} activated!"}
    except Exception as e:
        logger.error(f"Error triggering event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class DeviceAddRequest(BaseModel):
    """Request model for adding a new device to the Parco RTLS system."""
    device_id: str
    device_type: int
    device_name: Optional[str] = None
    start_date: Optional[datetime] = None  # Changed to datetime for proper type handling

class AssignDeviceRequest(BaseModel):
    """Request model for assigning a device to a zone."""
    device_id: str
    entity_id: str  # Updated to match expected string format in usp_assign_dev_add
    reason_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PositionRequest(BaseModel):
    """Request model for inserting a device position."""
    device_id: str
    start_time: datetime
    end_time: datetime
    x: float
    y: float
    z: float

class TextEventRequest(BaseModel):
    """Request model for logging a text event."""
    device_id: str
    event_data: str
    timestamp: Optional[datetime] = None

class DeviceStateRequest(BaseModel):
    """Request model for updating a device's state."""
    device_id: str
    new_state: str  # Expected values: "active" or "inactive"

class AssignDeviceDeleteRequest(BaseModel):
    """Request model for deleting a device assignment."""
    assignment_id: int

class AssignDeviceEditRequest(BaseModel):
    """Request model for editing a device assignment."""
    assignment_id: int
    device_id: str
    entity_id: str
    reason_id: int

class AssignDeviceEndRequest(BaseModel):
    """Request model for ending a device assignment."""
    assignment_id: int

class EntityAssignRequest(BaseModel):
    """Request model for assigning an entity."""
    parent_id: str
    child_id: str
    reason_id: int

class EntityAssignEndRequest(BaseModel):
    """Request model for ending an entity assignment."""
    assignment_id: int

class AssignmentReasonRequest(BaseModel):
    """Request model for adding or editing an assignment reason."""
    reason: str

class DeviceTypeRequest(BaseModel):
    """Request model for adding or editing a device type."""
    description: str

class DeviceEndDateRequest(BaseModel):
    """Request model for setting or removing a device end date."""
    device_id: str
    end_date: Optional[datetime] = None

class EntityRequest(BaseModel):
    """Request model for adding or editing an entity."""
    entity_id: str
    entity_type: int
    entity_name: Optional[str] = None

class EntityTypeRequest(BaseModel):
    """Request model for adding or editing an entity type."""
    type_name: str

class MapRequest(BaseModel):
    """Request model for adding a map."""
    map_name: str
    map_path: str
    map_format: str
    map_scale: float
    zone_id: int

class RegionRequest(BaseModel):
    """Request model for adding or editing a region."""
    region_id: int
    zone_id: int
    region_name: str
    max_x: float
    max_y: float
    max_z: float
    min_x: float
    min_y: float
    min_z: float
    trigger_id: int

class ResourceRequest(BaseModel):
    """Request model for adding or editing a resource."""
    resource_type: int
    resource_name: str
    resource_ip: str
    resource_port: int
    resource_rank: int
    resource_fs: bool
    resource_avg: bool

class TriggerAddRequest(BaseModel):
    """Request model for adding a trigger."""
    direction: int
    name: str
    ignore: bool

class VertexRequest(BaseModel):
    """Request model for adding or editing a vertex."""
    vertex_id: int
    coord_x: float
    coord_y: float
    coord_z: float
    order_num: int
    region_id: int

class ZoneRequest(BaseModel):
    """Request model for adding or editing a zone."""
    zone_type: int
    zone_name: str
    parent_zone: Optional[int] = None

# Device Management (ParcoRTLSMaint) - Existing + Fixed
@app.get("/api/get_all_devices")
async def get_all_devices():
    """Fetch all devices."""
    result = await call_stored_procedure("maint", "usp_device_select_all")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No devices found")

@app.post("/api/add_device")
async def add_device(request: DeviceAddRequest):
    """Add a new device with optional name and start date."""
    start_date = request.start_date or datetime.now()
    result = await call_stored_procedure("maint", "usp_device_add", request.device_id, request.device_type, request.device_name, start_date)
    if result and isinstance(result, (int, str)):  # Handle integer or string return (device ID)
        return {"message": "Device added successfully", "device_id": str(result) if isinstance(result, int) else result}
    raise HTTPException(status_code=500, detail="Failed to add device: Invalid result from usp_device_add")

@app.delete("/api/delete_device/{device_id}")
async def delete_device(device_id: str):
    """Delete a device by ID."""
    result = await call_stored_procedure("maint", "usp_device_delete", device_id)
    if result and isinstance(result, (int, str)):  # Ensure result is handled consistently
        return {"message": "Device deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete device")

@app.get("/api/get_device_by_id/{device_id}")
async def get_device_by_id(device_id: str):
    """Fetch device details by ID."""
    result = await call_stored_procedure("maint", "usp_device_select_by_id", device_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Device not found")

@app.get("/api/get_device_by_type/{device_type}")
async def get_device_by_type(device_type: int):
    """Fetch devices by type."""
    result = await call_stored_procedure("maint", "usp_device_select_by_type", device_type)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No devices found for this type")

@app.get("/api/get_out_of_service_devices")
async def get_out_of_service_devices():
    """Fetch all out-of-service devices."""
    result = await call_stored_procedure("maint", "usp_device_select_outofservice")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No out-of-service devices found")

@app.post("/api/set_device_end_date")
async def set_device_end_date(request: DeviceEndDateRequest):
    """Set or remove the end date for a device."""
    end_date = request.end_date or None
    result = await call_stored_procedure("maint", "usp_device_set_end_date", request.device_id, end_date)
    if result and isinstance(result, (int, str)):
        return {"message": "Device end date updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update device end date")

@app.delete("/api/remove_device_end_date/{device_id}")
async def remove_device_end_date(device_id: str):
    """Remove the end date for a device."""
    result = await call_stored_procedure("maint", "usp_device_remove_end_date", device_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device end date removed successfully"}
    raise HTTPException(status_code=500, detail="Failed to remove device end date")

# Device Type Management
@app.post("/api/add_device_type")
async def add_device_type(request: DeviceTypeRequest):
    """Add a new device type."""
    result = await call_stored_procedure("maint", "usp_device_type_add", request.description)
    if result and isinstance(result, (int, str)):
        return {"message": "Device type added successfully", "type_id": result if isinstance(result, int) else result[0]["i_typ_dev"] if isinstance(result, list) and result else None}
    raise HTTPException(status_code=500, detail="Failed to add device type")

@app.delete("/api/delete_device_type/{type_id}")
async def delete_device_type(type_id: int):
    """Delete a device type by ID."""
    result = await call_stored_procedure("maint", "usp_device_type_delete", type_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device type deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete device type")

@app.put("/api/edit_device_type")
async def edit_device_type(type_id: int, request: DeviceTypeRequest):
    """Edit a device type."""
    result = await call_stored_procedure("maint", "usp_device_type_edit", type_id, request.description)
    if result and isinstance(result, (int, str)):
        return {"message": "Device type edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit device type")

@app.get("/api/list_device_types")
async def list_device_types():
    """List all device types."""
    result = await call_stored_procedure("maint", "usp_device_type_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device types found")

# Device Assignment Management - Fixed
@app.post("/api/assign_device_to_zone")
async def assign_device_to_zone(request: AssignDeviceRequest):
    """Assign a device to a zone with optional end date."""
    start_date = request.start_date or datetime.now()
    end_date = request.end_date or None
    result = await call_stored_procedure("maint", "usp_assign_dev_add", request.device_id, request.entity_id, request.reason_id, start_date, end_date)
    if result and isinstance(result, (int, str)):  # Handle integer or string return (assignment ID)
        return {"message": "Device assigned successfully", "assignment_id": str(result) if isinstance(result, int) else result[0]["i_asn_dev"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to assign device: Invalid result from usp_assign_dev_add")

@app.delete("/api/delete_device_assignment/{assignment_id}")
async def delete_device_assignment(request: AssignDeviceDeleteRequest):
    """Delete a device assignment by ID."""
    result = await call_stored_procedure("maint", "usp_assign_dev_delete", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete device assignment")

@app.delete("/api/delete_all_device_assignments")
async def delete_all_device_assignments():
    """Delete all device assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_delete_all")
    if result and isinstance(result, (int, str)):
        return {"message": "All device assignments deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete all device assignments")

@app.delete("/api/delete_device_assignments_by_entity/{entity_id}")
async def delete_device_assignments_by_entity(entity_id: str):
    """Delete all device assignments by entity ID."""
    result = await call_stored_procedure("maint", "usp_assign_dev_delete_all_by_ent", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignments deleted successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to delete device assignments for entity")

@app.put("/api/edit_device_assignment")
async def edit_device_assignment(request: AssignDeviceEditRequest):
    """Edit a device assignment."""
    result = await call_stored_procedure("maint", "usp_assign_dev_edit", request.assignment_id, request.device_id, request.entity_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit device assignment")

@app.post("/api/end_device_assignment")
async def end_device_assignment(request: AssignDeviceEndRequest):
    """End a device assignment by ID."""
    result = await call_stored_procedure("maint", "usp_assign_dev_end", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Device assignment ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end device assignment")

@app.post("/api/end_all_device_assignments")
async def end_all_device_assignments():
    """End all device assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_end_all")
    if result and isinstance(result, (int, str)):
        return {"message": "All device assignments ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end all device assignments")

@app.get("/api/list_device_assignments")
async def list_device_assignments(include_ended: bool = False):
    """List all device assignments, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_list", include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found")

@app.get("/api/list_device_assignments_by_entity/{entity_id}")
async def list_device_assignments_by_entity(entity_id: str, include_ended: bool = False):
    """List device assignments by entity ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_entity", entity_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for entity")

@app.get("/api/list_device_assignments_by_device/{device_id}")
async def list_device_assignments_by_device(device_id: str, include_ended: bool = False):
    """List device assignments by device ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_id", device_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for device")

@app.get("/api/list_device_assignments_by_reason/{reason_id}")
async def list_device_assignments_by_reason(reason_id: int, include_ended: bool = False):
    """List device assignments by reason ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_dev_list_by_reason", reason_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No device assignments found for reason")

# Entity Management
@app.post("/api/add_entity")
async def add_entity(request: EntityRequest):
    """Add a new entity."""
    creation_date = datetime.now()
    update_date = datetime.now()
    result = await call_stored_procedure("maint", "usp_entity_add", request.entity_id, request.entity_type, request.entity_name, creation_date, update_date)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity added successfully", "entity_id": result[0]["x_id_ent"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add entity")

@app.get("/api/list_all_entities")
async def list_all_entities():
    """List all entities."""
    result = await call_stored_procedure("maint", "usp_entity_all")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entities found")

@app.get("/api/get_entity_by_id/{entity_id}")
async def get_entity_by_id(entity_id: str):
    """Fetch entity details by ID."""
    result = await call_stored_procedure("maint", "usp_entity_by_id", entity_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Entity not found")

@app.get("/api/get_entities_by_type/{entity_type}")
async def get_entities_by_type(entity_type: int):
    """Fetch entities by type."""
    result = await call_stored_procedure("maint", "usp_entity_by_type", entity_type)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entities found for this type")

@app.delete("/api/delete_entity/{entity_id}")
async def delete_entity(entity_id: str):
    """Delete an entity by ID."""
    result = await call_stored_procedure("maint", "usp_entity_delete", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity")

@app.put("/api/edit_entity")
async def edit_entity(request: EntityRequest):
    """Edit an entity."""
    result = await call_stored_procedure("maint", "usp_entity_edit", request.entity_id, request.entity_type, request.entity_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity")

# Entity Type Management
@app.post("/api/add_entity_type")
async def add_entity_type(request: EntityTypeRequest):
    """Add a new entity type."""
    result = await call_stored_procedure("maint", "usp_entity_type_add", request.type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type added successfully", "type_id": result[0]["i_typ_ent"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add entity type")

@app.delete("/api/delete_entity_type/{type_id}")
async def delete_entity_type(type_id: str):
    """Delete an entity type by ID."""
    result = await call_stored_procedure("maint", "usp_entity_type_delete", type_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity type")

@app.put("/api/edit_entity_type")
async def edit_entity_type(type_id: str, request: EntityTypeRequest):
    """Edit an entity type."""
    result = await call_stored_procedure("maint", "usp_entity_type_edit", type_id, request.type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity type edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity type")

@app.get("/api/list_entity_types")
async def list_entity_types():
    """List all entity types."""
    result = await call_stored_procedure("maint", "usp_entity_type_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity types found")

# Entity Assignment Management
@app.post("/api/assign_entity")
async def assign_entity(request: EntityAssignRequest):
    """Assign an entity (parent-child relationship)."""
    result = await call_stored_procedure("maint", "usp_assign_entity_add", request.parent_id, request.child_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment added successfully", "assignment_id": result[0]["i_asn_ent"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to assign entity")

@app.delete("/api/delete_entity_assignment/{assignment_id}")
async def delete_entity_assignment(assignment_id: int):
    """Delete an entity assignment by ID."""
    result = await call_stored_procedure("maint", "usp_assign_entity_delete", assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete entity assignment")

@app.delete("/api/delete_all_entity_assignments/{entity_id}")
async def delete_all_entity_assignments(entity_id: str):
    """Delete all entity assignments by entity ID."""
    result = await call_stored_procedure("maint", "usp_assign_entity_delete_all", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "All entity assignments deleted successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to delete all entity assignments")

@app.put("/api/edit_entity_assignment")
async def edit_entity_assignment(assignment_id: int, request: EntityAssignRequest):
    """Edit an entity assignment."""
    result = await call_stored_procedure("maint", "usp_assign_entity_edit", assignment_id, request.parent_id, request.child_id, request.reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit entity assignment")

@app.post("/api/end_entity_assignment")
async def end_entity_assignment(request: EntityAssignEndRequest):
    """End an entity assignment by ID."""
    result = await call_stored_procedure("maint", "usp_assign_entity_end", request.assignment_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Entity assignment ended successfully"}
    raise HTTPException(status_code=500, detail="Failed to end entity assignment")

@app.post("/api/end_all_entity_assignments/{entity_id}")
async def end_all_entity_assignments(entity_id: str):
    """End all entity assignments by entity ID."""
    result = await call_stored_procedure("maint", "usp_assign_entity_end_all", entity_id)
    if result and isinstance(result, (int, str)):
        return {"message": "All entity assignments ended successfully for entity"}
    raise HTTPException(status_code=500, detail="Failed to end all entity assignments")

@app.get("/api/list_entity_assignments")
async def list_entity_assignments(include_ended: bool = False):
    """List all entity assignments, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_entity_list", include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found")

@app.get("/api/list_entity_assignments_by_child/{child_id}")
async def list_entity_assignments_by_child(child_id: str, include_ended: bool = False):
    """List entity assignments by child entity ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_child", child_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for child")

@app.get("/api/list_entity_assignments_by_id/{assignment_id}")
async def list_entity_assignments_by_id(assignment_id: int):
    """List entity assignments by assignment ID."""
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_key", assignment_id)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for ID")

@app.get("/api/list_entity_assignments_by_parent/{parent_id}")
async def list_entity_assignments_by_parent(parent_id: str, include_ended: bool = False):
    """List entity assignments by parent entity ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_parent", parent_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for parent")

@app.get("/api/list_entity_assignments_by_reason/{reason_id}")
async def list_entity_assignments_by_reason(reason_id: int, include_ended: bool = False):
    """List entity assignments by reason ID, optionally including ended assignments."""
    result = await call_stored_procedure("maint", "usp_assign_entity_list_by_reason", reason_id, include_ended)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No entity assignments found for reason")

# Assignment Reason Management
@app.post("/api/add_assignment_reason")
async def add_assignment_reason(request: AssignmentReasonRequest):
    """Add a new assignment reason."""
    result = await call_stored_procedure("maint", "usp_assmt_reason_add", request.reason)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason added successfully", "reason_id": result[0]["i_rsn"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add assignment reason")

@app.delete("/api/delete_assignment_reason/{reason_id}")
async def delete_assignment_reason(reason_id: int):
    """Delete an assignment reason by ID."""
    result = await call_stored_procedure("maint", "usp_assmt_reason_delete", reason_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete assignment reason")

@app.put("/api/edit_assignment_reason")
async def edit_assignment_reason(reason_id: int, request: AssignmentReasonRequest):
    """Edit an assignment reason."""
    result = await call_stored_procedure("maint", "usp_assmt_reason_edit", reason_id, request.reason)
    if result and isinstance(result, (int, str)):
        return {"message": "Assignment reason edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit assignment reason")

@app.get("/api/list_assignment_reasons")
async def list_assignment_reasons():
    """List all assignment reasons."""
    result = await call_stored_procedure("maint", "usp_assmt_reason_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No assignment reasons found")

# Zone Management (Additional) - Fixed
@app.post("/api/add_zone")
async def add_zone(request: ZoneRequest):
    """Add a new zone."""
    result = await call_stored_procedure("maint", "usp_zone_add", request.zone_type, request.zone_name, request.parent_zone)
    if result and isinstance(result, (int, str)):
        return {"message": "Zone added successfully", "zone_id": result[0]["i_zn"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add zone")

@app.delete("/api/delete_zone/{zone_id}")
async def delete_zone(zone_id: int):
    """Delete a zone by ID."""
    result = await call_stored_procedure("maint", "usp_zone_delete", zone_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Zone deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete zone")

@app.put("/api/edit_zone")
async def edit_zone(request: ZoneRequest):
    """Edit a zone."""
    result = await call_stored_procedure("maint", "usp_zone_edit", request.zone_type, request.zone_name, request.parent_zone)
    if result and isinstance(result, (int, str)):
        return {"message": "Zone edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit zone")

@app.get("/api/get_zone_by_id/{zone_id}")
async def get_zone_by_id(zone_id: int):
    """Fetch zone details by ID."""
    result = await call_stored_procedure("maint", "usp_zone_select_by_id", zone_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Zone not found")

@app.get("/api/get_all_zones")
async def get_all_zones():
    """Fetch all zones in the system."""
    result = await call_stored_procedure("maint", "usp_zone_select_all")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No zones found")

@app.get("/api/get_zone_parent/{child_id}")
async def get_zone_parent(child_id: int):
    """Fetch parent zone by child zone ID."""
    result = await call_stored_procedure("maint", "usp_zone_parent_select", child_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="No parent zone found for child")

@app.get("/api/get_zone_by_point")
async def get_zone_by_point(x: float, y: float, z: float):
    """Fetch zone by point coordinates."""
    result = await call_stored_procedure("maint", "usp_zone_select_by_point", x, y, z)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="No zone found for point")

@app.post("/api/add_zone_type")
async def add_zone_type(zone_type_name: str):
    """Add a new zone type."""
    result = await call_stored_procedure("maint", "usp_zone_type_add", zone_type_name)
    if result and isinstance(result, (int, str)):
        return {"message": "Zone type added successfully", "type_id": result[0]["i_typ_zn"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add zone type")

# Region Management
@app.post("/api/add_region")
async def add_region(request: RegionRequest):
    """Add a new region."""
    result = await call_stored_procedure("maint", "usp_region_add", request.region_id, request.zone_id, request.region_name, request.max_x, request.max_y, request.max_z, request.min_x, request.min_y, request.min_z, request.trigger_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Region added successfully"}
    raise HTTPException(status_code=500, detail="Failed to add region")

@app.delete("/api/delete_region/{region_id}")
async def delete_region(region_id: int):
    """Delete a region by ID."""
    result = await call_stored_procedure("maint", "usp_region_delete", region_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Region deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete region")

@app.put("/api/edit_region")
async def edit_region(request: RegionRequest):
    """Edit a region."""
    result = await call_stored_procedure("maint", "usp_region_edit", request.region_id, request.zone_id, request.region_name, request.max_x, request.max_y, request.max_z, request.min_x, request.min_y, request.min_z, request.trigger_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Region edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit region")

@app.get("/api/list_regions")
async def list_regions():
    """List all regions."""
    result = await call_stored_procedure("maint", "usp_region_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No regions found")

@app.get("/api/get_region_by_id/{region_id}")
async def get_region_by_id(region_id: int):
    """Fetch region details by ID."""
    result = await call_stored_procedure("maint", "usp_region_select_by_id", region_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Region not found")

@app.get("/api/list_regions_by_trigger/{trigger_id}")
async def list_regions_by_trigger(trigger_id: int):
    """List regions by trigger ID."""
    result = await call_stored_procedure("maint", "usp_regions_select_by_trigger", trigger_id)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No regions found for trigger")

@app.get("/api/list_regions_by_zone/{zone_id}")
async def list_regions_by_zone(zone_id: int):
    """List regions by zone ID."""
    result = await call_stored_procedure("maint", "usp_regions_select_by_zone", zone_id)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No regions found for zone")

# Trigger Management (Additional)
@app.post("/api/add_trigger")
async def add_trigger(request: TriggerAddRequest):
    """Add a new trigger."""
    result = await call_stored_procedure("maint", "usp_trigger_add", request.direction, request.name, request.ignore)
    if result and isinstance(result, (int, str)):
        return {"message": "Trigger added successfully", "trigger_id": result[0]["i_trg"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add trigger")

@app.delete("/api/delete_trigger/{trigger_id}")
async def delete_trigger(trigger_id: int):
    """Delete a trigger by ID."""
    result = await call_stored_procedure("maint", "usp_trigger_delete", trigger_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Trigger deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete trigger")

@app.get("/api/list_trigger_directions")
async def list_trigger_directions():
    """List all trigger directions."""
    result = await call_stored_procedure("maint", "usp_trigger_direction_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No trigger directions found")

@app.get("/api/list_triggers")
async def list_triggers():
    """List all triggers."""
    result = await call_stored_procedure("maint", "usp_trigger_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No triggers found")

@app.get("/api/get_trigger_details/{trigger_id}")
async def get_trigger_details(trigger_id: int):
    """Fetch detailed trigger information including regions and zones."""
    result = await call_stored_procedure("maint", "usp_trigger_select", trigger_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Trigger not found")

@app.get("/api/list_all_triggers")
async def list_all_triggers():
    """List all triggers with region/zone details."""
    result = await call_stored_procedure("maint", "usp_trigger_select_all")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No triggers found")

@app.get("/api/get_triggers_by_point")
async def get_triggers_by_point(x: float, y: float, z: float):
    """Fetch triggers by point coordinates."""
    result = await call_stored_procedure("maint", "usp_trigger_select_by_point", x, y, z)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No triggers found for point")

@app.get("/api/get_trigger_by_id/{trigger_id}")
async def get_trigger_by_id(trigger_id: int):
    """Fetch trigger details by ID."""
    try:
        result = await call_stored_procedure("maint", "usp_trigger_select_by_id", trigger_id)
        if result and isinstance(result, list) and result:
            return result[0]
        raise HTTPException(status_code=404, detail="Trigger not found")
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@app.post("/api/fire_trigger/{trigger_name}")
async def fire_trigger(trigger_name: str):
    """Fire a trigger event and notify MQTT."""
    try:
        publish.single("home/rtls/trigger", trigger_name, hostname=MQTT_BROKER)
        result = await call_stored_procedure("maint", "usp_trigger_edit", 1, trigger_name, 1, False)  # Adjust based on actual trigger logic
        if result and isinstance(result, (int, str)):
            return {"message": f"Trigger {trigger_name} fired successfully"}
        raise HTTPException(status_code=500, detail="Failed to fire trigger")
    except Exception as e:
        logger.error(f"Error firing trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Vertex Management
@app.post("/api/add_vertex")
async def add_vertex(request: VertexRequest):
    """Add a new vertex."""
    result = await call_stored_procedure("maint", "usp_vertex_add", request.vertex_id, request.coord_x, request.coord_y, request.coord_z, request.order_num, request.region_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Vertex added successfully"}
    raise HTTPException(status_code=500, detail="Failed to add vertex")

@app.delete("/api/delete_vertex/{vertex_id}")
async def delete_vertex(vertex_id: int):
    """Delete a vertex by ID."""
    result = await call_stored_procedure("maint", "usp_vertex_delete", vertex_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Vertex deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete vertex")

@app.put("/api/edit_vertex")
async def edit_vertex(request: VertexRequest):
    """Edit a vertex."""
    result = await call_stored_procedure("maint", "usp_vertex_edit", request.vertex_id, request.coord_x, request.coord_y, request.coord_z, request.order_num, request.region_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Vertex edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit vertex")

@app.get("/api/list_vertices")
async def list_vertices():
    """List all vertices."""
    result = await call_stored_procedure("maint", "usp_vertex_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No vertices found")

@app.get("/api/get_vertex_by_id/{vertex_id}")
async def get_vertex_by_id(vertex_id: int):
    """Fetch vertex details by ID."""
    result = await call_stored_procedure("maint", "usp_vertex_select_by_id", vertex_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Vertex not found")

# Map Management
@app.post("/api/add_map")
async def add_map(request: MapRequest):
    """Add a new map."""
    result = await call_stored_procedure("maint", "usp_map_insert", request.map_name, request.map_path, request.map_format, request.map_scale, request.zone_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Map added successfully"}
    raise HTTPException(status_code=500, detail="Failed to add map")

@app.delete("/api/delete_map/{map_id}")
async def delete_map(map_id: int):
    """Delete a map by ID."""
    result = await call_stored_procedure("maint", "usp_map_delete", map_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Map deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete map")

@app.get("/api/list_maps")
async def list_maps():
    """List all maps."""
    result = await call_stored_procedure("maint", "usp_map_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No maps found")

# Resource Management
@app.post("/api/add_resource")
async def add_resource(request: ResourceRequest):
    """Add a new resource."""
    result = await call_stored_procedure("maint", "usp_resources_add", request.resource_type, request.resource_name, request.resource_ip, request.resource_port, request.resource_rank, request.resource_fs, request.resource_avg)
    if result and isinstance(result, (int, str)):
        return {"message": "Resource added successfully", "resource_id": result[0]["i_res"] if isinstance(result, list) and result else result}
    raise HTTPException(status_code=500, detail="Failed to add resource")

@app.delete("/api/delete_resource/{resource_id}")
async def delete_resource(resource_id: int):
    """Delete a resource by ID."""
    result = await call_stored_procedure("maint", "usp_resource_delete", resource_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Resource deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete resource")

@app.put("/api/edit_resource")
async def edit_resource(resource_id: int, request: ResourceRequest):
    """Edit a resource."""
    result = await call_stored_procedure("maint", "usp_resource_edit", resource_id, request.resource_type, request.resource_name, request.resource_ip, request.resource_port, request.resource_rank, request.resource_fs, request.resource_avg)
    if result and isinstance(result, (int, str)):
        return {"message": "Resource edited successfully"}
    raise HTTPException(status_code=500, detail="Failed to edit resource")

@app.get("/api/list_resources")
async def list_resources():
    """List all resources."""
    result = await call_stored_procedure("maint", "usp_resource_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No resources found")

@app.get("/api/get_resource_by_id/{resource_id}")
async def get_resource_by_id(resource_id: int):
    """Fetch resource details by ID."""
    result = await call_stored_procedure("maint", "usp_resource_select_by_id", resource_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Resource not found")

@app.get("/api/list_resource_types")
async def list_resource_types():
    """List all resource types."""
    result = await call_stored_procedure("maint", "usp_resource_type_list")
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No resource types found")

@app.post("/api/rank_resource_up/{resource_id}")
async def rank_resource_up(resource_id: int):
    """Increase resource rank."""
    result = await call_stored_procedure("maint", "usp_resources_rank_up", resource_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Resource rank increased successfully"}
    raise HTTPException(status_code=500, detail="Failed to increase resource rank")

@app.post("/api/rank_resource_down/{resource_id}")
async def rank_resource_down(resource_id: int):
    """Decrease resource rank."""
    result = await call_stored_procedure("maint", "usp_resources_rank_down", resource_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Resource rank decreased successfully"}
    raise HTTPException(status_code=500, detail="Failed to decrease resource rank")

# Zone Vertices Management
@app.post("/api/add_zone_vertices")
async def add_zone_vertices(request: VertexRequest):
    """Add zone vertices."""
    result = await call_stored_procedure("maint", "usp_zone_vertices_add", request.vertex_id, request.coord_x, request.coord_y, request.coord_z, request.order_num, request.region_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Zone vertices added successfully"}
    raise HTTPException(status_code=500, detail="Failed to add zone vertices")

@app.delete("/api/delete_zone_vertices/{zone_id}")
async def delete_zone_vertices(zone_id: int):
    """Delete zone vertices by zone ID."""
    result = await call_stored_procedure("maint", "usp_zone_vertices_delete", zone_id)
    if result and isinstance(result, (int, str)):
        return {"message": "Zone vertices deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete zone vertices")

@app.get("/api/list_zone_vertices/{zone_id}")
async def list_zone_vertices(zone_id: int):
    """List zone vertices by zone ID."""
    result = await call_stored_procedure("maint", "usp_zone_vertices_list", zone_id)
    if result and isinstance(result, list) and result:
        return result
    raise HTTPException(status_code=404, detail="No zone vertices found for zone")

# Historical Data & Positioning (ParcoRTLSHistR)
@app.get("/api/get_recent_device_positions/{device_id}")
async def get_recent_device_positions(device_id: str):
    """Retrieve recent device positions for real-time tracking (using ParcoRTLSHistR)."""
    try:
        result = await call_stored_procedure("hist_r", "usp_location_by_id", device_id)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No recent positions found")
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@app.post("/api/insert_position")
async def insert_position(request: PositionRequest):
    """Insert a device position into history (using ParcoRTLSHistR)."""
    try:
        result = await call_stored_procedure("hist_r", "usp_position_insert", request.device_id, request.start_time, request.end_time, request.x, request.y, request.z)
        if result and isinstance(result, (int, str)):
            return {"message": "Position inserted successfully"}
        raise HTTPException(status_code=500, detail="Failed to insert position")
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@app.get("/api/get_history_by_device/{device_id}")
async def get_history_by_device(device_id: str, start_date: datetime, end_date: datetime):
    """Fetch history of a device with date range (using ParcoRTLSHistR)."""
    try:
        result = await call_stored_procedure("hist_r", "usp_history_by_id", device_id, start_date, end_date)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No history found for device")
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

# Text Data Storage (ParcoRTLSData)
@app.post("/api/log_text_event")
async def log_text_event(request: TextEventRequest):
    """Log a text data event for a device with increased timeout handling."""
    try:
        # Increase timeout for the request to handle slow database connections
        timestamp = request.timestamp or datetime.now()
        async with asyncio.timeout(30):  # Increased timeout to 30 seconds
            result = await call_stored_procedure("data", "usp_textdata_add", request.device_id, request.event_data, timestamp)
        if result and isinstance(result, (int, str)):
            return {"message": "Text event logged successfully"}
        raise HTTPException(status_code=500, detail="Failed to log text event")
    except asyncio.TimeoutError:
        logger.error("Timeout occurred while logging text event for ParcoRTLSData")
        raise HTTPException(status_code=504, detail="Request timed out connecting to ParcoRTLSData")
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@app.get("/api/get_text_events_by_device/{device_id}")
async def get_text_events_by_device(device_id: str):
    """Fetch text events for a device (using ParcoRTLSData) with increased timeout handling."""
    try:
        # Increase timeout for the request to handle slow database connections
        async with asyncio.timeout(30):  # Increased timeout to 30 seconds
            result = await call_stored_procedure("data", "usp_textdata_all_by_device", device_id)
        if result and isinstance(result, list) and result:
            return result
        raise HTTPException(status_code=404, detail="No text events found for device")
    except asyncio.TimeoutError:
        logger.error("Timeout occurred while fetching text events for ParcoRTLSData")
        raise HTTPException(status_code=504, detail="Request timed out connecting to ParcoRTLSData")
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@app.put("/api/set_device_state")
async def set_device_state(request: DeviceStateRequest):
    """Update a device's state (e.g., active/inactive)."""
    try:
        end_date = datetime.max if request.new_state == "active" else datetime.now()
        # Use a default device_type (e.g., 1) since DeviceStateRequest doesn't have device_type
        result = await call_stored_procedure("maint", "usp_device_edit", request.device_id, 1, "", end_date)  # Adjusted to match usp_device_edit signature
        if result and isinstance(result, (int, str)):
            return {"message": "Device state updated successfully"}
        raise HTTPException(status_code=500, detail="Device state update failed")
    except Exception as e:
        logger.error(f"Error updating device state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)  # Optimized for high concurrency