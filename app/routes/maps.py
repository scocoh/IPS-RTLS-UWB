# Name: maps.py
# Version: 0.1.1
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Version 0.1.1 Converted to external descriptions using load_description()
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Maps management endpoints for ParcoRTLS FastAPI application.
# VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/maps.py 0P.3B.008
# CHANGED: Bumped version from 0P.3B.007 to 0P.3B.008
# ADDED: Enhanced docstrings for all endpoints with detailed descriptions, parameters, return values, examples, use cases, error handling, and hints
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
from typing import List
from database.db import call_stored_procedure, execute_raw_query
import logging

from pathlib import Path


def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "maps" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter(tags=["maps"])
logger = logging.getLogger(__name__)

class MapNameUpdateRequest(BaseModel):
    map_id: int
    name: str

@router.post(
    "/update_map_name",
    summary="Updates the name of a map in the ParcoRTLS system",
    description=load_description("update_map_name"),
    tags=["triggers"]
)
async def update_map_name(request: MapNameUpdateRequest):
    try:
        if not request.name.strip():
            logger.warning("Map name cannot be empty")
            raise HTTPException(status_code=400, detail="Map name cannot be empty")
        if len(request.name) > 100:
            logger.warning("Map name exceeds 100 characters")
            raise HTTPException(status_code=400, detail="Map name cannot exceed 100 characters")
        query = "UPDATE maps SET x_nm_map = $1 WHERE i_map = $2 RETURNING i_map;"
        result = await execute_raw_query("maint", query, request.name.strip(), request.map_id)
        if not result:
            logger.warning(f"Map not found for map_id={request.map_id}")
            raise HTTPException(status_code=404, detail="Map not found")
        logger.info(f"Map name updated for map_id={request.map_id} to '{request.name}'")
        return {"message": "Map name updated successfully"}
    except Exception as e:
        logger.error(f"Error updating map name for map_id={request.map_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating map name: {str(e)}")

@router.get(
    "/get_maps",
    summary="Retrieves a list of all maps in the ParcoRTLS system",
    description=load_description("get_maps"),
    tags=["triggers"]
)
async def get_maps():
    try:
        result = await call_stored_procedure("maint", "usp_map_list")
        if result:
            logger.info(f"Retrieved {len(result)} maps")
            return result
        logger.warning("No maps found")
        raise HTTPException(status_code=404, detail="No maps found")
    except Exception as e:
        logger.error(f"Error retrieving maps: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving maps: {str(e)}")

@router.get(
    "/get_map/{map_id}",
    summary="Retrieves the stored image for a specific map in the ParcoRTLS system",
    description=load_description("get_map"),
    tags=["triggers"]
)
async def get_map(map_id: int):
    try:
        query = "SELECT img_data, x_format FROM maps WHERE i_map = $1;"
        result = await execute_raw_query("maint", query, map_id)

        if not result or not result[0]["img_data"]:
            logger.warning(f"No image found for map_id={map_id}")
            raise HTTPException(status_code=404, detail="Map image not found")

        img_data = result[0]["img_data"]
        img_format = result[0]["x_format"] or "png"
        return Response(content=img_data, media_type=f"image/{img_format.lower()}")
    except Exception as e:
        logger.error(f"Error retrieving map image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving map image")

@router.get(
    "/get_map_data/{zone_id}",
    summary="Retrieves map data (image URL and bounds) for a specific zone in the ParcoRTLS system",
    description=load_description("get_map_data"),
    tags=["triggers"]
)
async def get_map_data(zone_id: int):
    try:
        zone_query = "SELECT i_map FROM zones WHERE i_zn = $1;"
        i_map = await execute_raw_query("maint", zone_query, zone_id)
        if not i_map or not i_map[0]["i_map"]:
            logger.warning(f"No zone found for zone_id={zone_id}")
            raise HTTPException(status_code=404, detail=f"No zone found for zone_id={zone_id}")
        i_map = i_map[0]["i_map"]

        map_query = "SELECT min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1;"
        map_data = await execute_raw_query("maint", map_query, i_map)
        if not map_data:
            logger.warning(f"No map data found for map_id={i_map}")
            raise HTTPException(status_code=404, detail=f"No map data found for map_id={i_map}")

        logger.info(f"Retrieved map data for zone_id={zone_id}, map_id={i_map}")
        return {
            "imageUrl": f"http://192.168.210.226:8000/api/get_map/{zone_id}",
            "bounds": [
                [map_data[0]["min_y"] or 0, map_data[0]["min_x"] or 0],
                [map_data[0]["max_y"] or 100, map_data[0]["max_x"] or 100]
            ]
        }
    except Exception as e:
        logger.error(f"Error retrieving map data for zone_id={zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map data: {str(e)}")

class MapAddRequest(BaseModel):
    name: str
    image: str

@router.post(
    "/add_map",
    summary="Adds a new map to the ParcoRTLS system",
    description=load_description("add_map"),
    tags=["triggers"]
)
async def add_map(request: MapAddRequest):
    try:
        result = await call_stored_procedure(
            "maint", "usp_map_insert", request.name, request.image
        )
        if result:
            logger.info(f"Map '{request.name}' added successfully")
            return {"message": "Map added successfully"}
        logger.warning("Failed to add map")
        raise HTTPException(status_code=500, detail="Failed to add map")
    except Exception as e:
        logger.error(f"Error adding map: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding map: {str(e)}")

@router.delete(
    "/delete_map/{map_id}",
    summary="Deletes a map from the ParcoRTLS system",
    description=load_description("delete_map"),
    tags=["triggers"]
)
async def delete_map(map_id: int):
    try:
        result = await call_stored_procedure("maint", "usp_map_delete", map_id)
        if result:
            logger.info(f"Map {map_id} deleted successfully")
            return {"message": f"Map {map_id} deleted successfully"}
        logger.warning(f"Map {map_id} not found")
        raise HTTPException(status_code=404, detail="Map not found")
    except Exception as e:
        logger.error(f"Error deleting map: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting map: {str(e)}")

@router.get(
    "/get_map_metadata/{map_id}",
    summary="Retrieves metadata for a specific map in the ParcoRTLS system",
    description=load_description("get_map_metadata"),
    tags=["triggers"]
)
async def get_map_metadata(map_id: int):
    try:
        result = await call_stored_procedure("maint", "usp_map_metadata", map_id)
        if result:
            logger.info(f"Retrieved metadata for map_id={map_id}")
            return result
        logger.warning(f"Map metadata not found for map_id={map_id}")
        raise HTTPException(status_code=404, detail="Map metadata not found")
    except Exception as e:
        logger.error(f"Error retrieving map metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map metadata: {str(e)}")

class MapUpdateRequest(BaseModel):
    map_id: int
    min_x: float
    min_y: float
    max_x: float
    max_y: float

@router.put(
    "/update_map_metadata",
    summary="Updates metadata for a specific map in the ParcoRTLS system",
    description=load_description("update_map_metadata"),
    tags=["triggers"]
)
async def update_map_metadata(request: MapUpdateRequest):
    try:
        result = await call_stored_procedure(
            "maint", "usp_map_update_metadata",
            request.map_id, request.min_x, request.min_y, request.max_x, request.max_y
        )
        if result:
            logger.info(f"Map metadata updated for map_id={request.map_id}")
            return {"message": "Map metadata updated successfully"}
        logger.warning(f"Map metadata update failed for map_id={request.map_id}")
        raise HTTPException(status_code=404, detail="Map metadata update failed")
    except Exception as e:
        logger.error(f"Error updating map metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating map metadata: {str(e)}")

@router.get(
    "/get_campus_zones/{campus_id}",
    summary="Retrieves the zone hierarchy for a specific campus in the ParcoRTLS system",
    description=load_description("get_campus_zones"),
    tags=["triggers"]
)
async def get_campus_zones(campus_id: int):
    try:
        result = await execute_raw_query(
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
        if not result:
            logger.warning(f"No zones found for campus_id={campus_id}")
            raise HTTPException(status_code=404, detail="No zones found for this campus")

        zone_map = {z["i_zn"]: {
            "zone_id": z["i_zn"],
            "zone_name": z["x_nm_zn"],
            "zone_type": z["i_typ_zn"],
            "parent_zone_id": z["i_pnt_zn"],
            "map_id": z["i_map"],
            "children": []
        } for z in result}

        zones = []
        for zone_id, zone_data in zone_map.items():
            if zone_data["parent_zone_id"] is None:
                zones.append(zone_data)
            else:
                parent = zone_map.get(zone_data["parent_zone_id"])
                if parent:
                    parent["children"].append(zone_data)

        logger.info(f"Retrieved {len(zones)} top-level zones for campus_id={campus_id}")
        return {"zones": zones}
    except Exception as e:
        logger.error(f"Error retrieving zones for campus_id={campus_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving zones: {str(e)}")