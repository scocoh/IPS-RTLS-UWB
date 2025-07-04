# Name: maps.py
# Version: 0.1.13
# Created: 971201
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: ParcoAdmin, TC and Nexus, Claude AI & AI Assistant
# Description: Python script for ParcoRTLS backend with pure coordinate-based map cropping functionality - TBI-friendly - Updated to use centralized configuration
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Maps management endpoints for ParcoRTLS FastAPI application.
# CHANGED: Bumped version from 0.1.12 to 0.1.13
# UPDATED: Replaced hardcoded IP addresses with centralized configuration
# REMOVED: Zone creation logic from coordinate crop endpoint
# REMOVED: _create_zone_hierarchy function (~75 lines)
# ADDED: Simple coordinate update endpoints for TBI-friendly modularity
# SIMPLIFIED: Pure image cropping only - no zones/regions complexity
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

from PIL import Image
import io
import asyncpg

# Import centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

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

        # Use centralized configuration for server host
        server_host = get_server_host()
        
        logger.info(f"Retrieved map data for zone_id={zone_id}, map_id={i_map}")
        return {
            "imageUrl": f"http://{server_host}:8000/api/get_map/{zone_id}",
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

@router.put("/update_map_metadata")
async def update_map_metadata(request: MapUpdateRequest):
    """
    Updates X,Y metadata for a specific map in the ParcoRTLS system.
    """
    try:
        # Use direct SQL instead of missing stored procedure
        query = """
            UPDATE maps 
            SET min_x = $1, min_y = $2, max_x = $3, max_y = $4
            WHERE i_map = $5
            RETURNING i_map;
        """
        result = await execute_raw_query(
            "maint", query, 
            request.min_x, request.min_y, request.max_x, request.max_y, request.map_id
        )
        
        if result:
            logger.info(f"Map metadata updated for map_id={request.map_id}")
            return {"message": "Map metadata updated successfully"}
        else:
            logger.warning(f"Map not found for map_id={request.map_id}")
            raise HTTPException(status_code=404, detail="Map not found")
            
    except Exception as e:
        logger.error(f"Error updating map metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating map metadata: {str(e)}")

# NEW TBI-FRIENDLY COORDINATE UPDATE ENDPOINTS

class MapCoordinatesRequest(BaseModel):
    map_id: int
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

class MapLatLonRequest(BaseModel):
    map_id: int
    lat_origin: float
    lon_origin: float

@router.put("/update_coordinates")
async def update_map_coordinates(request: MapCoordinatesRequest):
    """
    Updates X,Y,Z coordinates for a specific map.
    
    Simple endpoint for updating map coordinate bounds.
    Used by crop tool to fix coordinate scaling.
    """
    try:
        query = """
            UPDATE maps 
            SET min_x = $1, min_y = $2, min_z = $3, max_x = $4, max_y = $5, max_z = $6
            WHERE i_map = $7
            RETURNING i_map;
        """
        result = await execute_raw_query(
            "maint", query, 
            request.min_x, request.min_y, request.min_z,
            request.max_x, request.max_y, request.max_z,
            request.map_id
        )
        
        if result:
            logger.info(f"Map coordinates updated for map_id={request.map_id}")
            return {"message": "Map coordinates updated successfully"}
        else:
            logger.warning(f"Map not found for map_id={request.map_id}")
            raise HTTPException(status_code=404, detail="Map not found")
            
    except Exception as e:
        logger.error(f"Error updating map coordinates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating coordinates: {str(e)}")

@router.put("/update_lat_lon")
async def update_map_lat_lon(request: MapLatLonRequest):
    """
    Updates latitude/longitude origin for a specific map.
    
    Simple endpoint for updating map lat/lon origin points.
    Used to reset GPS coordinates to 0,0.
    """
    try:
        query = """
            UPDATE maps 
            SET lat_origin = $1, lon_origin = $2
            WHERE i_map = $3
            RETURNING i_map;
        """
        result = await execute_raw_query(
            "maint", query, 
            request.lat_origin, request.lon_origin, request.map_id
        )
        
        if result:
            logger.info(f"Map lat/lon updated for map_id={request.map_id}")
            return {"message": "Map lat/lon updated successfully"}
        else:
            logger.warning(f"Map not found for map_id={request.map_id}")
            raise HTTPException(status_code=404, detail="Map not found")
            
    except Exception as e:
        logger.error(f"Error updating map lat/lon: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating lat/lon: {str(e)}")

@router.put("/update_all_metadata/{map_id}")
async def update_all_map_metadata(
    map_id: int,
    min_x: float,
    min_y: float, 
    min_z: float,
    max_x: float,
    max_y: float,
    max_z: float,
    lat_origin: float = 0.0,
    lon_origin: float = 0.0
):
    """
    Updates all map metadata in one call.
    
    Complete update endpoint for coordinates + lat/lon.
    Used by crop tool for single-call updates.
    """
    try:
        query = """
            UPDATE maps 
            SET min_x = $1, min_y = $2, min_z = $3, max_x = $4, max_y = $5, max_z = $6,
                lat_origin = $7, lon_origin = $8
            WHERE i_map = $9
            RETURNING i_map;
        """
        result = await execute_raw_query(
            "maint", query, 
            min_x, min_y, min_z, max_x, max_y, max_z,
            lat_origin, lon_origin, map_id
        )
        
        if result:
            logger.info(f"All map metadata updated for map_id={map_id}")
            return {"message": "All map metadata updated successfully"}
        else:
            logger.warning(f"Map not found for map_id={map_id}")
            raise HTTPException(status_code=404, detail="Map not found")
            
    except Exception as e:
        logger.error(f"Error updating all map metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating metadata: {str(e)}")

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
    
@router.get("/get_image_metadata/{map_id}")
async def get_image_metadata(map_id: int):
    try:
        query = "SELECT img_data, x_format FROM maps WHERE i_map = $1;"
        result = await execute_raw_query("maint", query, map_id)
        if not result:
            raise HTTPException(status_code=404, detail="Map not found")
        
        img_data, file_format = result[0]["img_data"], result[0]["x_format"]
        image = Image.open(io.BytesIO(img_data))
        
        return {
            "width": image.width,
            "height": image.height,
            "format": file_format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_db_connection():
    """Get database connection for transactions using centralized configuration"""
    db_configs = get_db_configs_sync()
    maint_config = db_configs['maint']
    
    return await asyncpg.connect(
        host=maint_config['host'],
        port=maint_config['port'],
        user=maint_config['user'],
        password=maint_config['password'],
        database=maint_config['database']
    )

# SIMPLIFIED COORDINATE-BASED MAP CROPPING - IMAGE ONLY, NO ZONES

class CoordinateCropRequest(BaseModel):
    source_map_id: int
    crop_name: str
    min_x: float
    min_y: float
    max_x: float
    max_y: float

@router.post(
    "/create_coordinate_crop",
    summary="Create a new map from coordinate-based crop of an existing map - IMAGE ONLY",
    description="Creates a new map entry that represents a cropped section of a source map, working entirely in ParcoRTLS coordinate space (feet). Pure image cropping with no zone creation.",
    tags=["maps"]
)
async def create_coordinate_crop(request: CoordinateCropRequest):
    """
    Create a new map from coordinate-based crop - IMAGE ONLY, NO ZONES
    
    This endpoint creates a new map entry with a cropped image and properly scaled 
    coordinate bounds. Works entirely in ParcoRTLS coordinate space (feet).
    """
    try:
        # 1. Validate source map exists and get its metadata
        source_map_query = """
            SELECT i_map, x_nm_map, min_x, min_y, min_z, max_x, max_y, max_z, 
                   lat_origin, lon_origin, img_data, x_format
            FROM maps WHERE i_map = $1
        """
        source_map_result = await execute_raw_query("maint", source_map_query, request.source_map_id)
        
        if not source_map_result:
            raise HTTPException(status_code=404, detail=f"Source map {request.source_map_id} not found")
        
        source_map = source_map_result[0]
        logger.info(f"Source map found: {source_map['x_nm_map']}")
        
        # 2. Validate crop bounds are within source map bounds
        if (request.min_x < source_map['min_x'] or request.max_x > source_map['max_x'] or
            request.min_y < source_map['min_y'] or request.max_y > source_map['max_y']):
            raise HTTPException(
                status_code=400, 
                detail=f"Crop bounds ({request.min_x},{request.min_y},{request.max_x},{request.max_y}) "
                      f"exceed source map bounds ({source_map['min_x']},{source_map['min_y']},"
                      f"{source_map['max_x']},{source_map['max_y']})"
            )
        
        if request.min_x >= request.max_x or request.min_y >= request.max_y:
            raise HTTPException(status_code=400, detail="Invalid crop bounds: min values must be less than max values")
        
        # 3. Calculate pixel coordinates for cropping the actual image
        source_width = source_map['max_x'] - source_map['min_x']
        source_height = source_map['max_y'] - source_map['min_y']
        
        # Get actual image dimensions
        source_image = Image.open(io.BytesIO(source_map['img_data']))
        img_width, img_height = source_image.size
        
        # Calculate scale factors from coordinate space to pixels
        pixels_per_foot_x = img_width / source_width
        pixels_per_foot_y = img_height / source_height
        
        # Convert crop coordinates to pixel coordinates
        crop_pixel_x1 = int((request.min_x - source_map['min_x']) * pixels_per_foot_x)
        crop_pixel_y1 = int((request.min_y - source_map['min_y']) * pixels_per_foot_y)
        crop_pixel_x2 = int((request.max_x - source_map['min_x']) * pixels_per_foot_x)
        crop_pixel_y2 = int((request.max_y - source_map['min_y']) * pixels_per_foot_y)
        
        # PIL uses top-left origin, but ParcoRTLS uses bottom-left, so flip Y
        crop_pixel_y1_flipped = img_height - crop_pixel_y2
        crop_pixel_y2_flipped = img_height - crop_pixel_y1
        
        logger.info(f"Source image: {img_width}x{img_height} pixels")
        logger.info(f"Crop pixels: ({crop_pixel_x1}, {crop_pixel_y1_flipped}) to ({crop_pixel_x2}, {crop_pixel_y2_flipped})")
        
        # Validate pixel bounds
        if (crop_pixel_x1 < 0 or crop_pixel_y1_flipped < 0 or 
            crop_pixel_x2 > img_width or crop_pixel_y2_flipped > img_height):
            raise HTTPException(
                status_code=400,
                detail=f"Crop area extends beyond image bounds"
            )
        
        # Perform the actual image crop
        try:
            cropped_image = source_image.crop((crop_pixel_x1, crop_pixel_y1_flipped, crop_pixel_x2, crop_pixel_y2_flipped))
            logger.info(f"Cropped image size: {cropped_image.size}")
            
            # Convert cropped image to bytes
            img_buffer = io.BytesIO()
            cropped_image.save(img_buffer, format=source_map['x_format'])
            cropped_img_data = img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Image cropping failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image cropping failed: {str(e)}")
        
        # 4. Create new map entry with cropped image and new coordinate bounds
        create_map_query = """
            INSERT INTO maps (x_nm_map, min_x, min_y, min_z, max_x, max_y, max_z, 
                            lat_origin, lon_origin, img_data, x_format, d_uploaded)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
            RETURNING i_map
        """
        
        # For the cropped map, the coordinate bounds become the new "full map" bounds
        crop_width = request.max_x - request.min_x
        crop_height = request.max_y - request.min_y
        
        # New map coordinate space: (0,0) to (crop_width, crop_height)
        new_map_result = await execute_raw_query(
            "maint", create_map_query,
            request.crop_name,
            0.0,  # new min_x starts at 0
            0.0,  # new min_y starts at 0  
            source_map.get('min_z', -1.0),
            crop_width,   # new max_x is the crop width
            crop_height,  # new max_y is the crop height
            source_map.get('max_z', 40.0),
            source_map.get('lat_origin'),
            source_map.get('lon_origin'),
            cropped_img_data,  # Use cropped image data
            source_map['x_format']
        )
        
        new_map_id = new_map_result[0]['i_map']
        logger.info(f"Created new cropped map {new_map_id}: {request.crop_name}")
        
        return {
            "new_map_id": new_map_id,
            "source_map_id": request.source_map_id,
            "crop_bounds": {
                "min_x": request.min_x,
                "min_y": request.min_y, 
                "max_x": request.max_x,
                "max_y": request.max_y
            },
            "new_map_bounds": {
                "min_x": 0.0,
                "min_y": 0.0,
                "max_x": crop_width,
                "max_y": crop_height
            },
            "message": "Coordinate crop created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating coordinate crop: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating coordinate crop: {str(e)}")