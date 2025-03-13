# Version 250311 /home/parcoadmin/parco_fastapi/app/routes/zone_builder.py 0P.3B.001
from fastapi import APIRouter, HTTPException, Query
from database.db import execute_raw_query
from pydantic import BaseModel
from typing import List, Optional
import logging

# Initialize router
router = APIRouter(tags=["zone_builder"])
logger = logging.getLogger(__name__)

# Zone Creation Request Model
class ZoneCreateRequest(BaseModel):
    zone_name: str
    zone_type: int
    map_id: int
    parent_zone_id: Optional[int] = None
    vertices: List[dict] = []

# Zone Update Request Model
class ZoneUpdateRequest(BaseModel):
    vertices: List[dict]

# ✅ Create Zone
@router.post("/create_zone")
async def create_zone(data: ZoneCreateRequest):
    """Creates a new zone with optional parent zone and vertices."""
    try:
        # Ensure parent zone containment if applicable
        if data.parent_zone_id:
            parent_query = """
                SELECT n_min_x, n_max_x, n_min_y, n_max_y
                FROM regions WHERE i_zn = $1;
            """
            parent_region = await execute_raw_query("maint", parent_query, data.parent_zone_id)
            if not parent_region:
                raise HTTPException(status_code=400, detail="Invalid parent zone ID")

        # Insert Zone
        query_zone = """
            INSERT INTO zones (x_nm_zn, i_typ_zn, i_pnt_zn, i_map)
            VALUES ($1, $2, $3, $4) RETURNING i_zn;
        """
        result = await execute_raw_query("maint", query_zone, data.zone_name, data.zone_type, data.parent_zone_id, data.map_id)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create zone")
        zone_id = result[0]["i_zn"]

        # Insert Region (Only if vertices exist)
        if not data.vertices:
            return {"i_zn": zone_id, "message": "Zone created without a region (no vertices)"}

        x_coords = [v.get("n_x", 0) for v in data.vertices]
        y_coords = [v.get("n_y", 0) for v in data.vertices]
        n_min_x, n_max_x = min(x_coords), max(x_coords)
        n_min_y, n_max_y = min(y_coords), max(y_coords)

        query_region = """
            INSERT INTO regions (i_zn, x_nm_rgn, n_min_x, n_max_x, n_min_y, n_max_y)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING i_rgn;
        """
        result_region = await execute_raw_query("maint", query_region, zone_id, data.zone_name, n_min_x, n_max_x, n_min_y, n_max_y)
        if not result_region:
            raise HTTPException(status_code=500, detail="Failed to create region")
        region_id = result_region[0]["i_rgn"]

        # Insert Vertices
        for order, vertex in enumerate(data.vertices, start=1):
            query_vertex = """
                INSERT INTO vertices (i_rgn, n_x, n_y, n_z, n_ord)
                VALUES ($1, $2, $3, $4, $5);
            """
            await execute_raw_query("maint", query_vertex, region_id, vertex["n_x"], vertex["n_y"], vertex.get("n_z", 0), order)

        return {"i_zn": zone_id, "i_rgn": region_id, "message": "Zone, region, and vertices created successfully"}

    except Exception as e:
        logger.error(f"Error in create_zone: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Edit Zone (Update Vertices)
@router.put("/update_zone/{zone_id}")
async def update_zone(zone_id: int, data: ZoneUpdateRequest):
    """Update vertices of an existing zone."""
    try:
        # Fetch region ID
        query_region = "SELECT i_rgn FROM regions WHERE i_zn = $1;"
        region_result = await execute_raw_query("maint", query_region, zone_id)
        if not region_result:
            raise HTTPException(status_code=404, detail="Region not found for this zone")
        region_id = region_result[0]["i_rgn"]

        # Delete old vertices
        query_delete_vertices = "DELETE FROM vertices WHERE i_rgn = $1;"
        await execute_raw_query("maint", query_delete_vertices, region_id)

        # Insert new vertices
        for order, vertex in enumerate(data.vertices, start=1):
            query_insert_vertex = """
                INSERT INTO vertices (i_rgn, n_x, n_y, n_z, n_ord)
                VALUES ($1, $2, $3, $4, $5);
            """
            await execute_raw_query("maint", query_insert_vertex, region_id, vertex["n_x"], vertex["n_y"], vertex.get("n_z", 0), order)

        return {"message": "Zone vertices updated successfully"}

    except Exception as e:
        logger.error(f"Error updating zone: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Get All Zones
@router.get("/get_all_zones")
async def get_all_zones():
    """Retrieve all zones."""
    query = "SELECT i_zn AS zone_id, x_nm_zn AS name FROM zones;"
    result = await execute_raw_query("maint", query)
    if not result:
        raise HTTPException(status_code=404, detail="No zones found")
    return {"zones": result}