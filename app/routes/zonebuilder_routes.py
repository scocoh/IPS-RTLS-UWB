# /home/parcoadmin/parco_fastapi/app/routes/zonebuilder_routes.py
from fastapi import APIRouter, HTTPException, Response
from database.db import execute_raw_query
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/get_maps")
async def get_maps():
    """Fetches all available maps (async, matches Flask behavior)"""
    try:
        maps_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map FROM maps"
        )
        return {"maps": [{"map_id": m["i_map"], "name": m["x_nm_map"]} for m in maps_data]}
    except Exception as e:
        logger.error(f"Error retrieving maps: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving maps: {str(e)}")

@router.get("/get_map_data/{map_id}")
async def get_map_data(map_id: int):
    """Fetches map data for zone builder without zone lookup"""
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map, min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No map found for map_id={map_id}")
        
        data = map_data[0]
        return {
            "imageUrl": f"http://192.168.210.231:8000/zonebuilder/get_map/{map_id}",
            "bounds": [[data["min_y"], data["min_x"]], [data["max_y"], data["max_x"]]]
        }
    except Exception as e:
        logger.error(f"Error retrieving map data for map_id={map_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map data: {str(e)}")

@router.get("/get_map_metadata/{map_id}")
async def get_map_metadata(map_id: int):
    """Fetches metadata for a specific map (async, no zone lookup)"""
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map, min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No metadata found for map_id={map_id}")
        data = map_data[0]
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

@router.get("/get_parent_zones")
async def get_parent_zones():
    """Fetches all zones (not just top-level) to allow selection as parent (async)"""
    try:
        zones_data = await execute_raw_query(
            "maint",
            "SELECT i_zn, x_nm_zn, i_typ_zn FROM zones ORDER BY i_typ_zn, x_nm_zn"
        )
        return {"zones": [{"zone_id": z["i_zn"], "name": z["x_nm_zn"], "level": z["i_typ_zn"]} for z in zones_data]}
    except Exception as e:
        logger.error(f"Error retrieving parent zones: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving parent zones: {str(e)}")

@router.get("/get_zone_types")
async def get_zone_types():
    """Fetches all zone types (async)"""
    try:
        zone_types = await execute_raw_query(
            "maint",
            "SELECT i_typ_zn, x_dsc_zn FROM tlkzonetypes ORDER BY i_typ_zn"
        )
        return [{"zone_level": z["i_typ_zn"], "zone_name": z["x_dsc_zn"], "api_endpoint": "/create_zone"} for z in zone_types]
    except Exception as e:
        logger.error(f"Error retrieving zone types: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving zone types: {str(e)}")

@router.post("/create_zone")
async def create_zone(data: dict):
    """Creates a new zone (fully async, using execute_raw_query)"""
    try:
        # Extract & validate inputs
        zone_name = data.get('zone_name')
        map_id = data.get('map_id')
        zone_level = data.get('zone_level')
        parent_zone_id = data.get('parent_zone_id')
        vertices = data.get('vertices', [])

        if not all([zone_name, map_id, zone_level]):
            raise HTTPException(status_code=400, detail="Missing required fields (zone_name, map_id, zone_level)")

        try:
            map_id = int(map_id)
            zone_level = int(zone_level)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid map_id or zone_level. Expected integers.")

        # Log input data for debugging
        logger.info(f"Creating zone with data: {data}")

        # Insert zone into DB (Async)
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

        # Insert region with calculated bounds
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

        # Insert vertices with region_id
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

@router.get("/get_map/{map_id}")
async def get_map(map_id: int):
    """Fetches binary map image (async)"""
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
        logger.error(f"Error retrieving map {map_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map: {str(e)}")