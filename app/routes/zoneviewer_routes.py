"""
/home/parcoadmin/parco_fastapi/app/routes/zoneviewer_routes.py
Version: 0.1.10 (Fixed add_vertex by directly implementing logic)
Zone Viewer & Editor endpoints for ParcoRTLS FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from database.db import execute_raw_query
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class AddVertexRequest(BaseModel):
    zone_id: int
    x: float
    y: float
    z: float = 0.0
    order: float

@router.get("/get_campus_zones")
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_map/{map_id}")
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_map_metadata/{map_id}")
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_map_data/{map_id}")
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

        logger.info(f"Retrieved map data for map_id={map_id}")
        data = map_data[0]
        return {
            "imageUrl": f"http://192.168.210.231:8000/zoneviewer/get_map/{map_id}",
            "bounds": [
                [float(data["min_y"]), float(data["min_x"])],
                [float(data["max_y"]), float(data["max_x"])]
            ]
        }
    except Exception as e:
        logger.error(f"Error retrieving map data for map_id={map_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_all_zones_for_campus/{campus_id}")
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_vertices_for_campus/{campus_id}")
async def get_vertices_for_campus(campus_id: int):
    """Fetch all vertices for zones under a campus."""
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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_vertices")
async def update_vertices(vertices: list[dict]):
    """Bulk update vertices."""
    try:
        if not vertices:
            raise HTTPException(status_code=400, detail="No vertices provided")
        updated_count = 0
        for vertex in vertices:
            vertex_id = vertex.get("vertex_id")
            x = round(float(vertex.get("x")), 6)
            y = round(float(vertex.get("y")), 6)
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
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_vertex/{vertex_id}")
async def delete_vertex(vertex_id: int):
    """Delete a vertex by ID."""
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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_vertex")
async def add_vertex(request: AddVertexRequest):
    """Add a new vertex to a zone, aligned with DataV2.VertexAdd."""
    try:
        logger.debug(f"Received add_vertex request: {request.dict()}")
        # Get region ID for the zone
        region_data = await execute_raw_query(
            "maint",
            "SELECT i_rgn FROM regions WHERE i_zn = $1 LIMIT 1",
            request.zone_id
        )
        if not region_data:
            logger.warning(f"No region found for zone_id={request.zone_id}")
            raise HTTPException(status_code=404, detail=f"No region found for zone_id={request.zone_id}")
        region_id = region_data[0]["i_rgn"]

        # Validate region_id exists
        region_exists = await execute_raw_query(
            "maint",
            "SELECT i_rgn FROM public.regions WHERE i_rgn = $1",
            region_id
        )
        if not region_exists:
            logger.warning(f"Region ID {region_id} not found")
            raise HTTPException(status_code=400, detail=f"Region ID {region_id} does not exist")

        # Insert vertex using DataV2.VertexAdd logic
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
            int(request.order)  # Ensure integer order
        )
        if not result:
            logger.error("Failed to add vertex: no rows inserted")
            raise HTTPException(status_code=500, detail="Failed to add vertex")

        new_vertex = result[0]
        new_vertex["zone_id"] = request.zone_id  # Add zone_id for frontend consistency
        logger.info(f"Added vertex {new_vertex['vertex_id']} to zone_id={request.zone_id}")
        return new_vertex
    except Exception as e:
        logger.error(f"Error adding vertex to zone_id={request.zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))