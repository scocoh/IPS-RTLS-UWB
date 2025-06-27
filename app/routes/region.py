# Name: region.py
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
routes/region.py
Version: 0.1.5 (Enhanced endpoint documentation with verbose docstrings)
Region management endpoints for ParcoRTLS FastAPI application.
# VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/region.py 0.1.5
# CHANGED: Enhanced endpoint documentation with detailed docstrings, including descriptions, parameters, return values, examples, use cases, and hints; bumped to 0.1.5
# PREVIOUS: Added tags=["regions"] to APIRouter for Swagger UI grouping, bumped to 0.1.4
# PREVIOUS: Added endpoints for usp_region_list, usp_regions_select, and usp_regions_select_by_trigger; fixed trigger endpoint for proper 404 handling, version 0.1.3
# 
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from fastapi import APIRouter, HTTPException
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from models import RegionRequest
import logging

from pathlib import Path

# Ensure DEBUG logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "region" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter(tags=["regions"])

@router.post(
    "/add_region",
    summary="Add a new region to the ParcoRTLS system, associating it with a zone and optionally a trigger",
    description=load_description("add_region"),
    tags=["triggers"]
)
async def add_region(request: RegionRequest):
    try:
        result = await call_stored_procedure(
            "maint", "usp_region_add",
            request.region_id, request.zone_id, request.region_name, request.max_x, request.max_y, request.max_z,
            request.min_x, request.min_y, request.min_z, request.trigger_id
        )
        if result and isinstance(result, (int, str)):
            return {"message": "Region added successfully", "region_id": result[0]["i_rgn"] if isinstance(result, list) and result else result}
        raise HTTPException(status_code=500, detail="Failed to add region")
    except DatabaseError as e:
        logger.error(f"Database error adding region: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error adding region: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/delete_region/{region_id}",
    summary="Delete a region from the ParcoRTLS system by its ID",
    description=load_description("delete_region"),
    tags=["triggers"]
)
async def delete_region(region_id: int):
    try:
        result = await call_stored_procedure("maint", "usp_region_delete", region_id)
        if result and isinstance(result, (int, str)):
            return {"message": "Region deleted successfully"}
        raise HTTPException(status_code=500, detail="Failed to delete region")
    except DatabaseError as e:
        logger.error(f"Database error deleting region: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error deleting region: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/edit_region",
    summary="Update an existing region's details in the ParcoRTLS system",
    description=load_description("edit_region"),
    tags=["triggers"]
)
async def edit_region(request: RegionRequest):
    try:
        result = await call_stored_procedure(
            "maint", "usp_region_edit",
            request.region_id, request.zone_id, request.region_name, request.max_x, request.max_y, request.max_z,
            request.min_x, request.min_y, request.min_z, request.trigger_id
        )
        if result and isinstance(result, (int, str)):
            return {"message": "Region edited successfully"}
        raise HTTPException(status_code=500, detail="Failed to edit region")
    except DatabaseError as e:
        logger.error(f"Database error editing region: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error editing region: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_region_by_id/{region_id}",
    summary="Retrieve details of a specific region by its ID in the ParcoRTLS system",
    description=load_description("get_region_by_id"),
    tags=["triggers"]
)
async def get_region_by_id(region_id: int):
    result = await call_stored_procedure("maint", "usp_region_select_by_id", region_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Region not found")

@router.get(
    "/get_regions_by_zone/{zone_id}",
    summary="Fetch all regions and their associated vertices for a given zone ID in the ParcoRTLS system",
    description=load_description("get_regions_by_zone"),
    tags=["triggers"]
)
async def get_regions_by_zone(zone_id: int):
    try:
        logger.debug(f"Fetching regions for zone_id (i_zn) = {zone_id}")
        
        # Fetch regions for the given zone_id (i_zn)
        region_query = """
            SELECT i_rgn, i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z, i_trg
            FROM public.regions
            WHERE i_zn = $1;
        """
        regions = await execute_raw_query("maint", region_query, zone_id)
        if not regions:
            logger.warning(f"No regions found for zone_id (i_zn) = {zone_id}")
            raise HTTPException(status_code=404, detail=f"No regions found for zone ID {zone_id}")
        
        logger.debug(f"Found {len(regions)} regions for zone_id (i_zn) = {zone_id}: {regions}")
        
        # Fetch vertices for all regions
        region_ids = [region["i_rgn"] for region in regions]
        vertex_query = """
            SELECT i_vtx, i_rgn, n_x, n_y, n_z, n_ord
            FROM public.vertices
            WHERE i_rgn = ANY($1)
            ORDER BY i_rgn, n_ord;
        """
        vertices = await execute_raw_query("maint", vertex_query, region_ids)
        logger.debug(f"Found {len(vertices)} vertices for regions {region_ids}: {vertices}")
        
        # Combine regions and vertices into a structured response
        result = []
        for region in regions:
            region_vertices = [v for v in vertices if v["i_rgn"] == region["i_rgn"]]
            for vertex in region_vertices:
                # Combine region and vertex data into a single row, matching usp_regions_select_by_zone output
                combined = {
                    "i_rgn": region["i_rgn"],
                    "i_zn": region["i_zn"],
                    "x_nm_rgn": region["x_nm_rgn"],
                    "n_max_x": float(region["n_max_x"]),
                    "n_max_y": float(region["n_max_y"]),
                    "n_max_z": float(region["n_max_z"]),
                    "n_min_x": float(region["n_min_x"]),
                    "n_min_y": float(region["n_min_y"]),
                    "n_min_z": float(region["n_min_z"]),
                    "i_trg": region["i_trg"],
                    "n_x": float(vertex["n_x"]),
                    "n_y": float(vertex["n_y"]),
                    "n_z": float(vertex["n_z"]),
                    "n_ord": vertex["n_ord"],
                    "i_vtx": vertex["i_vtx"]
                }
                result.append(combined)
        
        # If no vertices, still return regions
        if not result:
            result = regions
        
        logger.info(f"Successfully fetched {len(result)} region-vertex entries for zone_id (i_zn) = {zone_id}")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching regions by zone: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_all_regions",
    summary="Retrieve all regions from the ParcoRTLS system database",
    description=load_description("get_all_regions"),
    tags=["triggers"]
)
async def get_all_regions():
    try:
        logger.debug("Fetching all regions using usp_region_list")
        result = await call_stored_procedure("maint", "usp_region_list")
        logger.debug(f"usp_region_list result: {result}")

        if not result or not isinstance(result, list) or not result:
            logger.warning("No regions found in the database")
            raise HTTPException(status_code=404, detail="No regions found")

        logger.info(f"Successfully fetched {len(result)} regions")
        return result
    except DatabaseError as e:
        logger.error(f"Database error fetching all regions: {e.message}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching all regions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_all_regions_alt",
    summary="Retrieve all regions from the ParcoRTLS system database using an alternative method",
    description=load_description("get_all_regions_alt"),
    tags=["triggers"]
)
async def get_all_regions_alt():
    try:
        logger.debug("Fetching all regions using usp_regions_select")
        result = await call_stored_procedure("maint", "usp_regions_select")
        logger.debug(f"usp_regions_select result: {result}")

        if not result or not isinstance(result, list) or not result:
            logger.warning("No regions found in the database")
            raise HTTPException(status_code=404, detail="No regions found")

        logger.info(f"Successfully fetched {len(result)} regions")
        return result
    except DatabaseError as e:
        logger.error(f"Database error fetching all regions: {e.message}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching all regions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_regions_by_trigger/{trigger_id}",
    summary="Fetch all regions associated with a specific trigger ID in the ParcoRTLS system",
    description=load_description("get_regions_by_trigger"),
    tags=["triggers"]
)
async def get_regions_by_trigger(trigger_id: int):
    try:
        logger.debug(f"Fetching regions for trigger_id = {trigger_id}")
        result = await call_stored_procedure("maint", "usp_regions_select_by_trigger", trigger_id)
        logger.debug(f"usp_regions_select_by_trigger result for trigger_id = {trigger_id}: {result}")

        # Handle the case where the result is a success message dictionary
        if isinstance(result, dict) and "message" in result:
            if "successfully" in result["message"].lower():
                logger.warning(f"No regions found for trigger_id = {trigger_id}")
                raise HTTPException(status_code=404, detail=f"No regions found for trigger ID {trigger_id}")
            else:
                raise HTTPException(status_code=500, detail=f"Unexpected stored procedure response: {result}")

        # Check if result is a list and contains data
        if not result or not isinstance(result, list) or not result:
            logger.warning(f"No regions found for trigger_id = {trigger_id}")
            raise HTTPException(status_code=404, detail=f"No regions found for trigger ID {trigger_id}")

        logger.info(f"Successfully fetched {len(result)} regions for trigger_id = {trigger_id}")
        return result
    except DatabaseError as e:
        logger.error(f"Database error fetching regions by trigger: {e.message}")
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException as e:
        raise e  # Re-raise HTTPException to preserve the original status (e.g., 404)
    except Exception as e:
        logger.error(f"Error fetching regions by trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))