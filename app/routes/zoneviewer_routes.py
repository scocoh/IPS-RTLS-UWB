# Name: zoneviewer_routes.py
# Version: 0.1.2
# Created: 971201
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & AI Assistant
# Version 0.1.2 Updated to use centralized configuration instead of hardcoded IP addresses, bumped from 0.1.1
# Version 0.1.1 Converted to external descriptions using load_description()
# Description: Python script for ParcoRTLS backend - Updated to use centralized configuration
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/zoneviewer_routes.py
Version: 0.1.2 (Updated to use centralized configuration)
Zone Viewer & Editor endpoints for ParcoRTLS FastAPI application.
# VERSION 250703 /home/parcoadmin/parco_fastapi/app/routes/zoneviewer_routes.py 0P.10B.04
# --- CHANGED: Bumped version from 0P.10B.03 to 0P.10B.04, updated to use centralized configuration
# --- UPDATED: Replaced hardcoded IP addresses with centralized configuration
# --- UPDATED: DATABASE_URL now uses centralized configuration
# --- PREVIOUS: 0P.10B.03 (Enhanced endpoint documentation)
# --- PREVIOUS: 0P.10B.02 (Added /get_maps_with_zone_types endpoint)
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from database.db import execute_raw_query
import logging
from sqlalchemy import create_engine, text
from contextlib import asynccontextmanager
import traceback

from pathlib import Path

# Import centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "zoneviewer_routes" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter()
logger = logging.getLogger(__name__)

# Ensure logging captures all levels
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)

# Database connection for transaction support using centralized configuration
def get_database_url():
    """Get database URL from centralized configuration"""
    db_configs = get_db_configs_sync()
    maint_config = db_configs['maint']
    return f"postgresql://{maint_config['user']}:{maint_config['password']}@{maint_config['host']}:{maint_config['port']}/{maint_config['database']}"

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)

class AddVertexRequest(BaseModel):
    zone_id: int
    x: float
    y: float
    z: float = 0.0
    order: float

@asynccontextmanager
async def get_db_connection():
    """Provide a transactional scope around a series of operations."""
    connection = engine.connect()
    transaction = connection.begin()
    try:
        yield connection
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        raise e
    finally:
        connection.close()

@router.get(
    "/get_campus_zones",
    summary="Retrieve all campus zones with their hierarchical structure",
    description=load_description("get_campus_zones"),
    tags=["triggers"]
)
async def get_campus_zones():
    try:
        zones_data = await execute_raw_query(
            "maint",
            """
            SELECT z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn, z.i_map
            FROM zones z
            ORDER BY z.i_pnt_zn NULLS FIRST, z.i_zn;
            """
        )
        if not zones_data:
            logger.warning("No zones found")
            raise HTTPException(status_code=404, detail="No zones found")

        zone_map = {z["i_zn"]: {
            "zone_id": z["i_zn"],
            "zone_name": z["x_nm_zn"],
            "zone_type": z["i_typ_zn"],
            "parent_zone_id": z["i_pnt_zn"],
            "map_id": z["i_map"],
            "children": []
        } for z in zones_data}

        campuses = []
        for zone_id, zone_data in zone_map.items():
            if zone_data["zone_type"] == 1:
                campuses.append(zone_data)
            elif zone_data["parent_zone_id"] in zone_map:
                zone_map[zone_data["parent_zone_id"]]["children"].append(zone_data)

        logger.info(f"Retrieved {len(campuses)} campuses with hierarchy")
        return {"campuses": campuses}
    except Exception as e:
        logger.error(f"Error fetching campus zones: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_map/{map_id}",
    summary="Retrieve the image data for a specific map",
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
        return Response(content=map_data[0]["img_data"], media_type=f"image/{map_data[0]['x_format'].lower()}")
    except Exception as e:
        logger.error(f"Error retrieving map {map_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_map_metadata/{map_id}",
    summary="Retrieve metadata (bounds) for a specific map",
    description=load_description("get_map_metadata"),
    tags=["triggers"]
)
async def get_map_metadata(map_id: int):
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No metadata found for map_id={map_id}")
        data = map_data[0]
        return {
            "min_x": float(data["min_x"]),
            "min_y": float(data["min_y"]),
            "max_x": float(data["max_x"]),
            "max_y": float(data["max_y"])
        }
    except Exception as e:
        logger.error(f"Error retrieving map metadata for map_id={map_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_map_data/{map_id}",
    summary="Retrieve map data including image URL and bounds for rendering",
    description=load_description("get_map_data"),
    tags=["triggers"]
)
async def get_map_data(map_id: int):
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            logger.warning(f"No map data found for map_id={map_id}")
            raise HTTPException(status_code=404, detail=f"No map data found for map_id={map_id}")

        # Use centralized configuration for server host
        server_host = get_server_host()
        
        logger.info(f"Retrieved map data for map_id={map_id}")
        data = map_data[0]
        return {
            "imageUrl": f"http://{server_host}:8000/zoneviewer/get_map/{map_id}",
            "bounds": [
                [float(data["min_y"]), float(data["min_x"])],
                [float(data["max_y"]), float(data["max_x"])]
            ]
        }
    except Exception as e:
        logger.error(f"Error retrieving map data for map_id={map_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_maps_with_zone_types",
    summary="Fetch unique maps with their associated zone types, sorted by hierarchy",
    description=load_description("get_maps_with_zone_types"),
    tags=["triggers"]
)
async def get_maps_with_zone_types():
    try:
        maps_data = await execute_raw_query(
            "maint",
            """
            SELECT i_map, x_nm_map, i_typ_zn
            FROM (
                SELECT DISTINCT z.i_map, m.x_nm_map,
                    MIN(CASE z.i_typ_zn
                        WHEN 1 THEN 1
                        WHEN 10 THEN 2
                        WHEN 2 THEN 3
                        WHEN 3 THEN 4
                        WHEN 4 THEN 5
                        WHEN 5 THEN 6
                        ELSE 7
                    END) AS type_order,
                    MIN(z.i_typ_zn) AS i_typ_zn
                FROM public.zones z
                JOIN public.maps m ON z.i_map = m.i_map
                GROUP BY z.i_map, m.x_nm_map
            ) t
            ORDER BY type_order, x_nm_map;
            """
        )
        if not maps_data:
            logger.warning("No maps found")
            raise HTTPException(status_code=404, detail="No maps found")
        logger.info(f"Retrieved {len(maps_data)} unique maps with zone types")
        return {"maps": [{k: v for k, v in m.items() if k != "type_order"} for m in maps_data]}
    except Exception as e:
        logger.error(f"Error retrieving maps with zone types: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_all_zones_for_campus/{campus_id}",
    summary="Retrieve all zones under a specific campus, including hierarchy",
    description=load_description("get_all_zones_for_campus"),
    tags=["triggers"]
)
async def get_all_zones_for_campus(campus_id: int):
    try:
        zones_data = await execute_raw_query(
            "maint",
            """
            WITH RECURSIVE zone_hierarchy AS (
                SELECT i_zn, x_nm_zn, i_typ_zn, i_pnt_zn, i_map
                FROM zones
                WHERE i_zn = $1
                UNION ALL
                SELECT z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn, z.i_map
                FROM zones z
                JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn
            )
            SELECT i_zn, x_nm_zn, i_typ_zn, i_pnt_zn, i_map
            FROM zone_hierarchy
            ORDER BY i_pnt_zn NULLS FIRST, i_zn
            """,
            campus_id
        )
        if not zones_data:
            logger.warning(f"No zones found for campus_id={campus_id}")
            return {"zones": []}

        zone_map = {z["i_zn"]: {
            "zone_id": z["i_zn"],
            "zone_name": z["x_nm_zn"],
            "zone_type": z["i_typ_zn"],
            "parent_zone_id": z["i_pnt_zn"],
            "map_id": z["i_map"],
            "children": []
        } for z in zones_data}

        zones = []
        for zone_id, zone_data in zone_map.items():
            if zone_data["parent_zone_id"] is None:
                zones.append(zone_data)
            elif zone_data["parent_zone_id"] in zone_map:
                zone_map[zone_data["parent_zone_id"]]["children"].append(zone_data)

        logger.info(f"Retrieved {len(zones)} zones for campus_id={campus_id}")
        return {"zones": zones}
    except Exception as e:
        logger.error(f"Error fetching zones for campus_id={campus_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_vertices_for_campus/{campus_id}",
    summary="Fetch all vertices for zones under a campus, excluding trigger regions",
    description=load_description("get_vertices_for_campus"),
    tags=["triggers"]
)
async def get_vertices_for_campus(campus_id: int):
    try:
        vertices_data = await execute_raw_query(
            "maint",
            """
            WITH RECURSIVE zone_hierarchy AS (
                SELECT i_zn FROM zones WHERE i_zn = $1
                UNION ALL
                SELECT z.i_zn FROM zones z
                JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn
            )
            SELECT v.i_vtx AS vertex_id, v.i_rgn, v.n_x AS x, v.n_y AS y, v.n_z AS z, v.n_ord AS "order", r.i_zn AS zone_id
            FROM vertices v
            JOIN regions r ON v.i_rgn = r.i_rgn
            JOIN zone_hierarchy zh ON r.i_zn = zh.i_zn
            WHERE r.i_trg IS NULL
            ORDER BY r.i_zn, v.n_ord
            """,
            campus_id
        )
        if not vertices_data:
            logger.warning(f"No vertices found for campus_id={campus_id}")
            return {"vertices": []}
        logger.info(f"Retrieved {len(vertices_data)} vertices for campus_id={campus_id}")
        return {"vertices": vertices_data}
    except Exception as e:
        logger.error(f"Error fetching vertices for campus_id={campus_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/update_vertices",
    summary="Bulk update vertices for zones",
    description=load_description("update_vertices"),
    tags=["triggers"]
)
async def update_vertices(vertices: list[dict]):
    try:
        if not vertices:
            raise HTTPException(status_code=400, detail="No vertices provided")
        updated_count = 0
        for vertex in vertices:
            vertex_id = vertex.get("vertex_id")
            x = round(float(vertex.get("x")), 6) # type: ignore # type: ignore
            y = round(float(vertex.get("y")), 6) # type: ignore
            z = round(float(vertex.get("z", 0)), 6)
            order = int(vertex.get("order", 1))
            result = await execute_raw_query(
                "maint",
                """
                UPDATE vertices
                SET n_x = $1, n_y = $2, n_z = $3, n_ord = $4
                WHERE i_vtx = $5
                RETURNING i_vtx
                """,
                x, y, z, order, vertex_id
            )
            if result:
                updated_count += 1
        if updated_count == len(vertices):
            logger.info(f"Updated {updated_count} vertices successfully")
            return {"message": "Vertices updated successfully"}
        logger.error(f"Updated {updated_count} out of {len(vertices)} vertices")
        raise HTTPException(status_code=500, detail=f"Partial update: {updated_count}/{len(vertices)}")
    except Exception as e:
        logger.error(f"Error updating vertices: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/delete_vertex/{vertex_id}",
    summary="Delete a specific vertex by ID",
    description=load_description("delete_vertex"),
    tags=["triggers"]
)
async def delete_vertex(vertex_id: int):
    try:
        result = await execute_raw_query(
            "maint",
            "DELETE FROM vertices WHERE i_vtx = $1 RETURNING i_vtx",
            vertex_id
        )
        if not result:
            logger.warning(f"Vertex {vertex_id} not found")
            raise HTTPException(status_code=404, detail=f"Vertex {vertex_id} not found")
        logger.info(f"Deleted vertex {vertex_id}")
        return {"message": "Vertex deleted successfully", "vertex_id": vertex_id}
    except Exception as e:
        logger.error(f"Error deleting vertex {vertex_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/add_vertex",
    summary="Add a new vertex to a zone",
    description=load_description("add_vertex"),
    tags=["triggers"]
)
async def add_vertex(request: AddVertexRequest):
    try:
        logger.debug(f"Received add_vertex request: {request.dict()}")
        region_data = await execute_raw_query(
            "maint",
            "SELECT i_rgn FROM regions WHERE i_zn = $1 LIMIT 1",
            request.zone_id
        )
        if not region_data:
            logger.warning(f"No region found for zone_id={request.zone_id}")
            raise HTTPException(status_code=404, detail=f"No region found for zone_id={request.zone_id}")
        region_id = region_data[0]["i_rgn"]

        region_exists = await execute_raw_query(
            "maint",
            "SELECT i_rgn FROM public.regions WHERE i_rgn = $1",
            region_id
        )
        if not region_exists:
            logger.warning(f"Region ID {region_id} not found")
            raise HTTPException(status_code=400, detail=f"Region ID {region_id} does not exist")

        query = """
            INSERT INTO public.vertices (i_rgn, n_x, n_y, n_z, n_ord)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING i_vtx AS vertex_id, i_rgn, n_x AS x, n_y AS y, n_z AS z, n_ord AS "order"
        """
        result = await execute_raw_query(
            "maint",
            query,
            region_id,
            request.x,
            request.y,
            request.z,
            int(request.order)
        )
        if not result:
            logger.error("Failed to add vertex: no rows inserted")
            raise HTTPException(status_code=500, detail="Failed to add vertex")

        new_vertex = result[0]
        new_vertex["zone_id"] = request.zone_id
        logger.info(f"Added vertex {new_vertex['vertex_id']} to zone_id={request.zone_id}")
        return new_vertex
    except Exception as e:
        logger.error(f"Error adding vertex to zone_id={request.zone_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/delete_zone_recursive/{zone_id}",
    summary="Delete a zone and all its progeny recursively",
    description=load_description("delete_zone_recursive"),
    tags=["triggers"]
)
async def delete_zone_recursive(zone_id: int):
    try:
        logger.info(f"Attempting to delete zone {zone_id} and its progeny")

        async with get_db_connection() as connection:
            result = connection.execute(
                text("""
                WITH RECURSIVE zone_hierarchy AS (
                    SELECT i_zn FROM zones WHERE i_zn = :zone_id
                    UNION ALL
                    SELECT z.i_zn FROM zones z
                    JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn
                )
                SELECT i_zn FROM zone_hierarchy
                """),
                {"zone_id": zone_id}
            )
            zones_to_delete = result.fetchall()
            if not zones_to_delete:
                logger.warning(f"No zones found to delete for zone_id={zone_id}")
                raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found")

            zone_ids = [row[0] for row in zones_to_delete]
            logger.debug(f"Zones to delete: {zone_ids}")

            connection.execute(
                text("""
                DELETE FROM vertices
                USING regions r
                WHERE vertices.i_rgn = r.i_rgn AND r.i_zn IN :zone_ids
                """),
                {"zone_ids": tuple(zone_ids)}
            )

            connection.execute(
                text("DELETE FROM regions WHERE i_zn IN :zone_ids"),
                {"zone_ids": tuple(zone_ids)}
            )

            connection.execute(
                text("DELETE FROM zones WHERE i_zn IN :zone_ids"),
                {"zone_ids": tuple(zone_ids)}
            )

        logger.info(f"Successfully deleted zone {zone_id} and its {len(zone_ids)} progeny")
        return {"message": f"Deleted zone {zone_id} and its progeny successfully"}
    except Exception as e:
        logger.error(f"Error deleting zone {zone_id} and its progeny: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))