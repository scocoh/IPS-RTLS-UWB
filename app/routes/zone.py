"""
routes/zone.py
Version: 0.1.3 (Added HEAD support for /get_map/{zone_id} endpoint)
Zone management endpoints for ParcoRTLS FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Response
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from models import ZoneRequest
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Existing endpoints
@router.get("/get_parents")
async def get_parents():
    """Fetch all top-level parent zones from ParcoRTLSMaint."""
    try:
        query = "SELECT i_zn, i_typ_zn, x_nm_zn FROM public.zones WHERE i_pnt_zn IS NULL ORDER BY i_zn DESC;"
        parents = await execute_raw_query("maint", query)
        logger.info(f"Retrieved {len(parents)} parent zones")
        return {"parents": parents}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching parents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_children/{parent_id}")
async def get_children(parent_id: int):
    """Fetch all child zones of a selected parent zone."""
    try:
        result = await call_stored_procedure("maint", "usp_zone_children_select", parent_id)
        if not result:
            logger.warning(f"No children found for parent_id={parent_id}")
            return {"children": []}
        if isinstance(result, str):
            children = json.loads(result)
        else:
            children = result
        logger.info(f"Retrieved {len(children if isinstance(children, list) else 1)} children for parent_id={parent_id}")
        return {"children": children if isinstance(children, list) else [children]}
    except DatabaseError as e:
        logger.error(f"Database error fetching children: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching children: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_map/{zone_id}", response_class=Response)
@router.head("/get_map/{zone_id}")
async def get_map(zone_id: int):
    """Fetch the map image associated with a selected zone as a downloadable file.

    Supports both GET and HEAD requests to allow browsers to check the resource before fetching.
    Note: Ensure CORS middleware is configured in app.py to allow requests from the React app (http://192.168.210.231:3000).
    """
    try:
        # Get map ID from zone
        zone_query = "SELECT i_map FROM zones WHERE i_zn = $1;"
        i_map = await execute_raw_query("maint", zone_query, zone_id)
        if not i_map or not i_map[0]["i_map"]:
            logger.warning(f"No zone found for zone_id={zone_id}")
            raise HTTPException(status_code=404, detail=f"No zone found for zone_id={zone_id}")
        i_map = i_map[0]["i_map"]

        # Get map image data
        map_query = "SELECT img_data FROM maps WHERE i_map = $1;"
        img_data_result = await execute_raw_query("maint", map_query, i_map)
        if not img_data_result or not img_data_result[0]["img_data"]:
            logger.warning(f"No map found for map_id={i_map}")
            raise HTTPException(status_code=404, detail=f"No map found for map_id={i_map}")
        img_data = img_data_result[0]["img_data"]

        # Get map format
        format_query = "SELECT x_format FROM maps WHERE i_map = $1;"
        format_result = await execute_raw_query("maint", format_query, i_map)
        file_format = format_result[0]["x_format"] if format_result and format_result[0]["x_format"] else "image/png"

        logger.info(f"Retrieved map for zone_id={zone_id}, map_id={i_map}")
        return Response(
            content=img_data,
            media_type=file_format,
            headers={"Content-Disposition": f"attachment; filename=map_zone_{zone_id}.{file_format.split('/')[-1]}"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_zone_vertices/{zone_id}")
async def get_zone_vertices(zone_id: int):
    """Fetch vertices for a selected zone to draw its boundary."""
    try:
        result = await call_stored_procedure("maint", "usp_zone_vertices_select_by_zone", zone_id)
        if result and isinstance(result, list) and result:
            logger.info(f"Retrieved {len(result)} vertices for zone_id={zone_id}")
            return {"vertices": [dict(vertex) for vertex in result]}
        logger.warning(f"No vertices found for zone_id={zone_id}")
        raise HTTPException(status_code=404, detail="No zone vertices found")
    except Exception as e:
        logger.error(f"Error fetching vertices for zone_id={zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_zone_types")
async def get_zone_types():
    """Fetch all zone types from ParcoRTLSMaint."""
    try:
        query = "SELECT i_typ_zn, x_dsc_zn FROM tlkzonetypes ORDER BY i_typ_zn;"
        zone_types = await execute_raw_query("maint", query)
        if not zone_types:
            logger.warning("No zone types found in the database")
            return []
        api_mapping = {1: "/api/add_trigger", 2: "/api/add_trigger", 3: "/api/add_trigger", 4: "/api/add_trigger", 5: "/api/add_trigger", 10: "/api/add_trigger"}
        zone_list = [{"zone_level": z["i_typ_zn"], "zone_name": z["x_dsc_zn"], "api_endpoint": api_mapping.get(z["i_typ_zn"], "/api/add_trigger")} for z in zone_types]
        logger.info(f"Retrieved {len(zone_list)} zone types")
        return zone_list
    except Exception as e:
        logger.error(f"Error retrieving zone types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving zone types: {str(e)}")

@router.get("/get_parent_zones")
async def get_parent_zones():
    """Fetch all top-level parent zones from ParcoRTLSMaint."""
    try:
        query = "SELECT i_zn AS zone_id, x_nm_zn AS name FROM public.zones WHERE i_pnt_zn IS NULL ORDER BY i_zn;"
        parents = await execute_raw_query("maint", query)
        if not parents:
            logger.warning("No parent zones found")
            return {"zones": []}
        logger.info(f"Retrieved {len(parents)} parent zones")
        return {"zones": parents}
    except Exception as e:
        logger.error(f"Error retrieving parent zones: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving parent zones: {str(e)}")