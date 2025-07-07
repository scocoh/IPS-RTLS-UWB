# Name: zonebuilder_routes.py
# Version: 0.1.2
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Version 0.1.2 Fixed Pylance syntax errors - null checks, image access, psycopg2 connection
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/routes/zonebuilder_routes.py
# VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/zonebuilder_routes.py 0P.10B.23
# --- CHANGED: Bumped version from 0P.10B.22 to 0P.10B.23
# --- FIXED: Added enhanced documentation for /api/get_all_devices, /api/add_device, /api/edit_device, /api/delete_device, and /validate-support-access endpoints
# --- PREVIOUS: Enhanced endpoint documentation with detailed docstrings, including descriptions, parameters, return values, examples, use cases, hints, and error handling, version 0P.10B.22
# --- PREVIOUS: Added /get_zone_vertices/{zone_id} endpoint to fetch vertices for a specific zone, excluding child zones and trigger regions, version 0P.10B.21
# 
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from fastapi import APIRouter, Depends, HTTPException, Response, Form, Body
from database.db import execute_raw_query, get_async_db_pool
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from PIL import Image
import sys

from pathlib import Path


def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "zonebuilder_routes" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter()
logger = logging.getLogger(__name__)
logger.debug(f"sys.path: {sys.path}")

# Database connection configuration (adjust as per your setup)
DB_CONFIG = {
    "dbname": "maint",
    "user": "parcoadmin",  # Replace with your DB username
    "password": "parcoMCSE04106!",  # Replace with your DB password
    "host": "localhost",  # Replace with your DB host if different
    "port": "5432"  # Replace with your DB port if different
}

@router.get(
    "/get_maps",
    summary="Retrieve a list of all available maps from the ParcoRTLS database",
    description=load_description("get_maps"),
    tags=["triggers"]
)
async def get_maps():
    try:
        maps_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map FROM maps"
        )
        logger.info(f"Fetched {len(maps_data)} maps")
        return {"maps": [{"map_id": m["i_map"], "name": m["x_nm_map"]} for m in maps_data]}
    except Exception as e:
        logger.error(f"Error retrieving maps: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving maps: {str(e)}")

@router.get(
    "/get_map_data/{map_id}",
    summary="Fetch map data for the Zone Builder, including the image URL and coordinate bounds",
    description=load_description("get_map_data"),
    tags=["triggers"]
)
async def get_map_data(map_id: int):
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map, min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No map found for map_id={map_id}")
        
        data = map_data[0]
        logger.info(f"Fetched map data for map_id={map_id}: {data['x_nm_map']}")
        return {
            "imageUrl": f"/zonebuilder/get_map/{map_id}",
            "bounds": [[data["min_y"], data["min_x"]], [data["max_y"], data["max_x"]]]
        }
    except Exception as e:
        logger.error(f"Error retrieving map data for map_id={map_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map data: {str(e)}")

@router.get(
    "/get_map_metadata/{map_id}",
    summary="Retrieve metadata for a specific map, including its ID, name, and coordinate bounds",
    description=load_description("get_map_metadata"),
    tags=["triggers"]
)
async def get_map_metadata(map_id: int):
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map, min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No metadata found for map_id={map_id}")
        data = map_data[0]
        logger.info(f"Fetched map metadata for map_id={map_id}: {data['x_nm_map']}")
        return {
            "map_id": data["i_map"],
            "name": data["x_nm_map"],
            "min_x": data["min_x"],
            "min_y": data["min_y"],
            "max_x": data["max_x"],
            "max_y": data["max_y"]
        }
    except Exception as e:
        logger.error(f"Error retrieving map metadata for map_id={map_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map metadata: {str(e)}")

@router.get(
    "/get_parent_zones",
    summary="Fetch all zones to allow selection as parent zones in the Zone Builder",
    description=load_description("get_parent_zones"),
    tags=["triggers"]
)
async def get_parent_zones():
    try:
        logger.debug("Attempting to get database pool for maint in get_parent_zones")
        pool = await get_async_db_pool("maint")
        if not pool:
            logger.error("Database pool unavailable for maint in get_parent_zones")
            raise HTTPException(status_code=500, detail="Database pool unavailable")
        async with pool.acquire() as conn:
            logger.debug("Executing query: SELECT i_zn, x_nm_zn, i_typ_zn FROM zones ORDER BY i_typ_zn, x_nm_zn")
            zones = await conn.fetch(
                "SELECT i_zn, x_nm_zn, i_typ_zn FROM zones ORDER BY i_typ_zn, x_nm_zn"
            )
            logger.info(f"Fetched {len(zones)} parent zones")
            return {
                "zones": [
                    {
                        "zone_id": zone["i_zn"],
                        "name": zone["x_nm_zn"],
                        "level": zone["i_typ_zn"]
                    }
                    for zone in zones
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching parent zones: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get(
    "/get_parent_zones_for_trigger_demo",
    summary="Fetch all zones with additional metadata for trigger demo purposes",
    description=load_description("get_parent_zones_for_trigger_demo"),
    tags=["triggers"]
)
async def get_parent_zones_for_trigger_demo():
    try:
        logger.debug("Starting get_parent_zones_for_trigger_demo")
        logger.debug("Attempting to get database pool for maint")
        pool = await get_async_db_pool("maint")
        if not pool:
            logger.error("Database pool unavailable for maint")
            raise HTTPException(status_code=500, detail="Database pool unavailable for maint")
        logger.debug("Successfully acquired database pool")
        async with pool.acquire() as conn:
            logger.debug("Acquired connection from pool")
            logger.debug("Executing query: SELECT i_zn, x_nm_zn, i_typ_zn, i_map, i_pnt_zn FROM zones ORDER BY i_typ_zn, x_nm_zn")
            zones = await conn.fetch(
                "SELECT i_zn, x_nm_zn, i_typ_zn, i_map, i_pnt_zn FROM zones ORDER BY i_typ_zn, x_nm_zn"
            )
            logger.info(f"Fetched {len(zones)} parent zones for trigger demo")
            return {
                "zones": [
                    {
                        "zone_id": zone["i_zn"],
                        "name": zone["x_nm_zn"],
                        "level": zone["i_typ_zn"],
                        "i_map": zone["i_map"],
                        "parent_zone_id": zone["i_pnt_zn"]
                    }
                    for zone in zones
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching parent zones for trigger demo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get(
    "/test_db_connection",
    summary="Test the database connection to the `maint` schema",
    description=load_description("test_db_connection"),
    tags=["triggers"]
)
async def test_db_connection():
    try:
        logger.debug("Testing database connection for maint")
        pool = await get_async_db_pool("maint")
        if not pool:
            logger.error("Database pool unavailable for maint in test_db_connection")
            raise HTTPException(status_code=500, detail="Database pool unavailable")
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            logger.info("Database connection test successful")
            return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error testing database connection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get(
    "/get_zone_types",
    summary="Fetch all zone types from the ParcoRTLS database",
    description=load_description("get_zone_types"),
    tags=["triggers"]
)
async def get_zone_types():
    try:
        zone_types = await execute_raw_query(
            "maint",
            "SELECT i_typ_zn, x_dsc_zn FROM tlkzonetypes ORDER BY i_typ_zn"
        )
        logger.info(f"Fetched {len(zone_types)} zone types")
        return [{"zone_level": z["i_typ_zn"], "zone_name": z["x_dsc_zn"], "api_endpoint": "/create_zone"} for z in zone_types]
    except Exception as e:
        logger.error(f"Error retrieving zone types: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving zone types: {str(e)}")

@router.get(
    "/get_zone_vertices/{zone_id}",
    summary="Fetch vertices for a specific zone, excluding child zones and trigger regions",
    description=load_description("get_zone_vertices"),
    tags=["triggers"]
)
async def get_zone_vertices(zone_id: int):
    try:
        vertices_data = await execute_raw_query(
            "maint",
            """
            SELECT v.i_vtx, v.i_rgn, v.n_x, v.n_y, v.n_z, v.n_ord
            FROM vertices v
            JOIN regions r ON v.i_rgn = r.i_rgn
            WHERE r.i_zn = $1 AND r.i_trg IS NULL
            ORDER BY v.n_ord
            """,
            zone_id
        )
        if not vertices_data:
            logger.warning(f"No vertices found for zone_id={zone_id}")
            return {"vertices": []}
        logger.info(f"Retrieved {len(vertices_data)} vertices for zone_id={zone_id}")
        return {"vertices": vertices_data}
    except Exception as e:
        logger.error(f"Error fetching vertices for zone_id={zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/internal-metadata", include_in_schema=False)
async def get_internal_metadata(format: str | None = None):
    try:
        with Image.open("static/default_grid_box.png") as img:
            # Fix: Use getattr with default to safely access text attribute
            concealed_text = None
            img_text = getattr(img, 'text', None)
            if img_text:
                concealed_text = img_text.get("concealed_text")
            
            if not concealed_text:
                raise HTTPException(status_code=404, detail="Concealed metadata not found")
            
            if format == "html":
                html_output = f"""
                <html>
                  <head>
                    <title>Internal Metadata</title>
                    <style>
                      body {{ font-family: Arial, sans-serif; margin: 20px; }}
                      pre {{ background-color: #f4f4f4; padding: 1em; border: 1px solid #ccc; }}
                    </style>
                  </head>
                  <body>
                    <h1>Internal Metadata</h1>
                    <pre>{concealed_text}</pre>
                  </body>
                </html>
                """
                return Response(content=html_output, media_type="text/html")
            else:
                return {"internal_metadata": concealed_text}
    except Exception as e:
        logger.error(f"Error retrieving internal metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/create_zone",
    summary="Create a new zone with associated region and vertices",
    description=load_description("create_zone"),
    tags=["triggers"]
)
async def create_zone(data: dict):
    try:
        zone_name = data.get('zone_name')
        map_id = data.get('map_id')
        zone_level = data.get('zone_level')
        parent_zone_id = data.get('parent_zone_id')
        vertices = data.get('vertices', [])

        if not all([zone_name, map_id, zone_level]):
            raise HTTPException(status_code=400, detail="Missing required fields (zone_name, map_id, zone_level)")

        # Fix: Add proper null checking before int conversion
        try:
            map_id = int(map_id) if map_id is not None else None
            zone_level = int(zone_level) if zone_level is not None else None
            if map_id is None or zone_level is None:
                raise ValueError("map_id and zone_level cannot be None")
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid map_id or zone_level. Expected integers.")

        logger.info(f"Creating zone with data: {data}")

        new_zone = await execute_raw_query(
            "maint",
            """
            INSERT INTO zones (x_nm_zn, i_typ_zn, i_pnt_zn, i_map)
            VALUES ($1, $2, $3, $4)
            RETURNING i_zn;
            """,
            zone_name, zone_level, parent_zone_id, map_id
        )

        if not new_zone:
            raise HTTPException(status_code=500, detail="Zone creation failed.")
        zone_id = new_zone[0]["i_zn"]
        logger.info(f"✅ Inserted Zone ID: {zone_id}")

        if vertices:
            x_coords = [v.get('n_x', 0) for v in vertices]
            y_coords = [v.get('n_y', 0) for v in vertices]
            z_coords = [v.get('n_z', 0) for v in vertices]
            n_min_x = min(x_coords) if x_coords else 0
            n_max_x = max(x_coords) if x_coords else 0
            n_min_y = min(y_coords) if y_coords else 0
            n_max_y = max(y_coords) if y_coords else 0
            n_min_z = min(z_coords) if z_coords else 0
            n_max_z = max(z_coords) if z_coords else 0
        else:
            n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z = 0, 0, 0, 0, 0, 0

        new_region = await execute_raw_query(
            "maint",
            """
            INSERT INTO regions (i_zn, x_nm_rgn, n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING i_rgn;
            """,
            zone_id, zone_name, n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z
        )
        region_id = new_region[0]["i_rgn"]
        logger.info(f"✅ Inserted Region ID: {region_id}")

        if vertices:
            for idx, vertex in enumerate(vertices):
                await execute_raw_query(
                    "maint",
                    """
                    INSERT INTO vertices (i_rgn, n_x, n_y, n_z, n_ord)
                    VALUES ($1, $2, $3, $4, $5);
                    """,
                    region_id, vertex['n_x'], vertex['n_y'], vertex['n_z'], idx + 1
                )
                logger.info(f"✅ Inserted Vertex: {vertex}")

        return {"zone_id": zone_id, "message": "Zone created successfully"}
    except Exception as e:
        logger.error(f"Error creating zone: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating zone: {str(e)}")

@router.get(
    "/get_map/{map_id}",
    summary="Fetch the binary image data for a specific map",
    description=load_description("get_map"),
    tags=["triggers"]
)
async def get_map(map_id: int):
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT img_data, x_format FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No map found for map_id={map_id}")
        logger.info(f"Fetched map image for map_id={map_id}")
        return Response(content=map_data[0]["img_data"], media_type=f"image/{map_data[0]['x_format'].lower()}")
    except Exception as e:
        logger.error(f"Error retrieving map {map_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map: {str(e)}")

@router.post(
    "/api/add_device_type",
    summary="Add a new device type to the ParcoRTLS database",
    description=load_description("add_device_type"),
    tags=["triggers"]
)
async def add_device_type(data: dict):
    try:
        description = data.get("description")
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        if len(description) > 50:
            raise HTTPException(status_code=400, detail="Description must be 50 characters or less")
        
        result = await execute_raw_query(
            "maint",
            "INSERT INTO tlkdevicetypes (x_dsc_dev) VALUES ($1) RETURNING i_typ_dev",
            description
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to insert device type")
        
        type_id = result[0]["i_typ_dev"]
        logger.info(f"Added device type: {description} with ID {type_id}")
        return {"type_id": type_id}
    except Exception as e:
        logger.error(f"Error adding device type: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get(
    "/api/get_all_devices",
    summary="Fetch all devices with their associated zone IDs from the ParcoRTLS database",
    description=load_description("get_all_devices"),
    tags=["triggers"]
)
async def get_all_devices():
    try:
        devices_data = await execute_raw_query(
            "maint",
            "SELECT * FROM usp_device_select_all()"
        )
        logger.info(f"Raw devices data: {devices_data}")
        response = [
            {
                "x_id_dev": d["x_id_dev"],
                "i_typ_dev": d["i_typ_dev"],
                "x_nm_dev": d["x_nm_dev"],
                "d_srv_bgn": d["d_srv_bgn"].isoformat() if d["d_srv_bgn"] else None,
                "d_srv_end": d["d_srv_end"].isoformat() if d["d_srv_end"] else None,
                "n_moe_x": float(d["n_moe_x"]) if d["n_moe_x"] is not None else None,
                "n_moe_y": float(d["n_moe_y"]) if d["n_moe_y"] is not None else None,
                "n_moe_z": float(d["n_moe_z"]) if d["n_moe_z"] is not None else None,
                "f_log": d["f_log"],
                "zone_id": d.get("zone_id", None)
            } for d in devices_data
        ]
        logger.info(f"Fetched {len(devices_data)} devices: {[d['x_id_dev'] for d in devices_data]}")
        logger.info(f"Response devices: {response}")
        return response
    except Exception as e:
        logger.error(f"Error retrieving devices: {e}")
        # Fallback to raw query if the function fails
        logger.info("Falling back to raw SELECT * FROM devices")
        devices_data = await execute_raw_query(
            "maint",
            "SELECT * FROM devices"
        )
        response = [
            {
                "x_id_dev": d["x_id_dev"],
                "i_typ_dev": d["i_typ_dev"],
                "x_nm_dev": d["x_nm_dev"],
                "d_srv_bgn": d["d_srv_bgn"].isoformat() if d["d_srv_bgn"] else None,
                "d_srv_end": d["d_srv_end"].isoformat() if d["d_srv_end"] else None,
                "n_moe_x": float(d["n_moe_x"]) if d["n_moe_x"] is not None else None,
                "n_moe_y": float(d["n_moe_y"]) if d["n_moe_y"] is not None else None,
                "n_moe_z": float(d["n_moe_z"]) if d["n_moe_z"] is not None else None,
                "f_log": d["f_log"],
                "zone_id": d.get("zone_id", None)
            } for d in devices_data
        ]
        logger.info(f"Fallback response devices: {response}")
        return response

@router.post(
    "/api/add_device",
    summary="Add a new device with an associated zone ID to the ParcoRTLS database",
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
    zone_id: int = Form(...)
):
    try:
        logger.info(f"Received add_device request: device_id={device_id}, device_type={device_type}, device_name={device_name}, n_moe_x={n_moe_x}, n_moe_y={n_moe_y}, n_moe_z={n_moe_z}, zone_id={zone_id}, type(zone_id)={type(zone_id)}")
        
        # Define the INSERT query with all relevant columns, including zone_id
        query = """
            INSERT INTO devices (x_id_dev, i_typ_dev, x_nm_dev, zone_id, f_log, d_srv_bgn, n_moe_x, n_moe_y, n_moe_z)
            VALUES ($1, $2, $3, $4, $5, NOW(), $6, $7, $8)
            RETURNING x_id_dev, zone_id;
        """
        params = (device_id, device_type, device_name, zone_id, False, n_moe_x, n_moe_y, n_moe_z)
        
        # Execute the query using execute_raw_query
        logger.info(f"Executing query: {query} with params: {params}")
        result = await execute_raw_query("maint", query, *params)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to add device")
        
        logger.info(f"Inserted device: {device_id}, returned zone_id: {result[0]['zone_id']}")
        return {"x_id_dev": result[0]["x_id_dev"], "message": "Device added successfully"}
    
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding device: {str(e)}")

@router.put(
    "/api/edit_device/{device_id}",
    summary="Edit an existing device's details, including its zone association, in the ParcoRTLS database",
    description=load_description("edit_device"),
    tags=["triggers"]
)
async def edit_device(
    device_id: str,
    device_name: str = Form(None),
    n_moe_x: float = Form(None),
    n_moe_y: float = Form(None),
    n_moe_z: float = Form(None),
    zone_id: int = Form(...)
):
    try:
        logger.info(f"Received edit_device request: device_id={device_id}, device_name={device_name}, n_moe_x={n_moe_x}, n_moe_y={n_moe_y}, n_moe_z={n_moe_z}, zone_id={zone_id}, type(zone_id)={type(zone_id)}")
        
        # Fix: Use correct psycopg2.connect syntax
        conn = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            UPDATE devices
            SET x_nm_dev = %s, n_moe_x = %s, n_moe_y = %s, n_moe_z = %s, zone_id = %s
            WHERE x_id_dev = %s
            RETURNING x_id_dev, zone_id;
        """
        params = (device_name, n_moe_x, n_moe_y, n_moe_z, zone_id, device_id)
        logger.info(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if not result:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        logger.info(f"Updated device: {device_id}, result: {result}")
        logger.info(f"Returned zone_id: {result['zone_id']}")
        return {"x_id_dev": result["x_id_dev"], "message": "Device updated successfully"}
    except Exception as e:
        logger.error(f"Error editing device: {e}")
        if 'conn' in locals():
            conn.close()
        raise HTTPException(status_code=500, detail=f"Error editing device: {str(e)}")

@router.delete(
    "/api/delete_device/{device_id}",
    summary="Delete a device and its associated assignments from the ParcoRTLS database",
    description=load_description("delete_device"),
    tags=["triggers"]
)
async def delete_device(device_id: str):
    try:
        logger.info(f"Received delete_device request for device_id={device_id}")
        await execute_raw_query(
            "maint",
            "DELETE FROM deviceassmts WHERE x_id_dev = $1",
            device_id
        )
        
        result = await execute_raw_query(
            "maint",
            "DELETE FROM devices WHERE x_id_dev = $1 RETURNING x_id_dev",
            device_id
        )
        if not result:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        logger.info(f"Deleted device: {device_id}")
        return {"message": f"Device {device_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting device: {str(e)}")

@router.post("/validate-support-access", include_in_schema=False)
async def validate_support_access(payload: dict = Body(...)):
    secret_password = "gene"
    if payload.get("password") == secret_password:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=403, detail="Invalid password")
    
@router.get("/proxy_map/{map_id}", response_class=Response, include_in_schema=False)
async def proxy_map(map_id: int):
    """
    Proxy the binary map image through the /api prefix so the frontend
    can fetch it via the same origin & port 3000 proxy.
    """
    from fastapi.responses import StreamingResponse
    import httpx

    backend_url = f"http://localhost:8000/zonebuilder/get_map/{map_id}"
    async with httpx.AsyncClient() as client:
        r = await client.get(backend_url)
        r.raise_for_status()
        return StreamingResponse(r.aiter_bytes(),
                                 media_type=r.headers["content-type"])