# VERSION 250309 /home/parcoadmin/parco_fastapi/app/routes/maps_upload.py 0P.1B.01
#  
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from database.db import execute_raw_query
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)  # ✅ Add logging

# ✅ Upload Map Endpoint (POST)
@router.post("/upload_map")
async def upload_map(
    name: str = Form(...),
    lat_origin: float = Form(None),
    lon_origin: float = Form(None),
    min_x: float = Form(None),
    min_y: float = Form(None),
    min_z: float = Form(None),
    max_x: float = Form(None),
    max_y: float = Form(None),
    max_z: float = Form(None),
    file: UploadFile = File(...)
):
    try:
        img_binary = await file.read()  # Read file as binary
        file_format = file.filename.split('.')[-1].upper()

        # ✅ Check file format
        allowed_formats = {"PNG", "JPG", "JPEG", "GIF"}
        if file_format not in allowed_formats:
            logger.warning(f"Unsupported file format attempted: {file_format}")
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_format}")

        # ⚠ Warning: If file is 4MB or larger, notify the user
        file_size_mb = len(img_binary) / (1024 * 1024)
        if file_size_mb >= 4:
            logger.warning(f"⚠ Large file detected: {file_size_mb:.2f} MB")

        logger.info(f"Uploading map: {name} ({file_format}, {file_size_mb:.2f} MB)")

        query = """
            INSERT INTO maps (x_nm_map, x_format, d_uploaded, min_x, min_y, min_z, max_x, max_y, max_z, lat_origin, lon_origin, img_data)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING i_map;
        """
        result = await execute_raw_query(
            "maint", query, name, file_format, datetime.utcnow(), min_x, min_y, min_z, max_x, max_y, max_z, lat_origin, lon_origin, img_binary
        )

        if result:
            logger.info(f"Map uploaded successfully: ID {result[0]['i_map']}")
            return {"message": "Map uploaded successfully", "map_id": result[0]["i_map"]}
        else:
            logger.error("Map upload failed unexpectedly.")
            raise HTTPException(status_code=500, detail="Failed to upload map")

    except Exception as e:
        logger.error(f"Error during map upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Retrieve Stored Map Image (GET)
@router.get("/map_image/{map_id}")
async def get_map_image(map_id: int):
    query = "SELECT img_data, x_format FROM maps WHERE i_map = $1;"
    try:
        result = await execute_raw_query("maint", query, map_id)
        if not result:
            raise HTTPException(status_code=404, detail="Map not found")

        img_data, file_format = result[0]["img_data"], result[0]["x_format"]
        return Response(content=img_data, media_type=f"image/{file_format.lower()}")
    except Exception as e:
        logger.error(f"Error retrieving map image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving map image")

# ✅ Edit Map Metadata (PUT)
@router.put("/edit_map/{map_id}")
async def edit_map(
    map_id: int,
    name: str = Form(...),
    lat_origin: float = Form(None),
    lon_origin: float = Form(None),
    min_x: float = Form(None),
    min_y: float = Form(None),
    min_z: float = Form(None),
    max_x: float = Form(None),
    max_y: float = Form(None),
    max_z: float = Form(None)
):
    try:
        query = """
            UPDATE maps 
            SET x_nm_map = $1, min_x = $2, min_y = $3, min_z = $4, max_x = $5, max_y = $6, max_z = $7, lat_origin = $8, lon_origin = $9
            WHERE i_map = $10;
        """
        result = await execute_raw_query(
            "maint", query, name, min_x, min_y, min_z, max_x, max_y, max_z, lat_origin, lon_origin, map_id
        )

        if result:
            logger.info(f"Map updated successfully: ID {map_id}")
            return {"message": "Map updated successfully"}
        else:
            logger.warning(f"Map update failed: ID {map_id}")
            raise HTTPException(status_code=500, detail="Failed to update map")

    except Exception as e:
        logger.error(f"Error updating map metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Delete Map (DELETE)
@router.delete("/delete_map/{map_id}")
async def delete_map(map_id: int):
    try:
        query = "DELETE FROM maps WHERE i_map = $1 RETURNING i_map;"
        result = await execute_raw_query("maint", query, map_id)

        if result:
            logger.info(f"Map deleted successfully: ID {map_id}")
            return {"message": f"Map {map_id} deleted successfully"}
        else:
            logger.warning(f"Attempted to delete non-existent map: ID {map_id}")
            raise HTTPException(status_code=404, detail="Map not found")

    except Exception as e:
        logger.error(f"Error deleting map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Added these new routs to Provide Map Metadata
# ✅ Get the number of zones for a specific map
@router.get("/get_map_zones/{map_id}")
async def get_map_zones(map_id: int):
    query = """
        SELECT COUNT(*) AS zone_count 
        FROM zones 
        WHERE i_map = $1;
    """
    result = await execute_raw_query("maint", query, map_id)
    return {"zone_count": result[0]["zone_count"] if result else 0}

# ✅ Get the number of regions for a specific map
@router.get("/get_map_regions/{map_id}")
async def get_map_regions(map_id: int):
    query = """
        SELECT COUNT(*) AS region_count 
        FROM regions 
        JOIN zones ON regions.i_zn = zones.i_zn
        WHERE zones.i_map = $1;
    """
    try:
        result = await execute_raw_query("maint", query, map_id)
        return {"region_count": result[0]["region_count"] if result else 0}
    except Exception as e:
        logger.error(f"Error fetching regions for map {map_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching region data")

# ✅ Get the number of triggers for a specific map
@router.get("/get_map_triggers/{map_id}")
async def get_map_triggers(map_id: int):
    query = """
        SELECT COUNT(*) AS trigger_count 
        FROM triggers 
        JOIN regions ON triggers.i_trg = regions.i_trg
        JOIN zones ON regions.i_zn = zones.i_zn
        WHERE zones.i_map = $1;
    """
    try:
        result = await execute_raw_query("maint", query, map_id)
        return {"trigger_count": result[0]["trigger_count"] if result else 0}
    except Exception as e:
        logger.error(f"Error fetching triggers for map {map_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching trigger data")
