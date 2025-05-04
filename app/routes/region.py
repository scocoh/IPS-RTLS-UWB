# Name: region.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
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

# Ensure DEBUG logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
router = APIRouter(tags=["regions"])

@router.post("/add_region")
async def add_region(request: RegionRequest):
    """
    Add a new region to the ParcoRTLS system, associating it with a zone and optionally a trigger.

    This endpoint creates a new region in the `regions` table, defining its spatial boundaries (min/max coordinates) and linking it to a specific zone and, if applicable, a trigger. Regions are critical in ParcoRTLS for defining spatial areas within zones, such as areas for tracking devices or triggering events. The endpoint uses the stored procedure `usp_region_add` to perform the insertion.

    Parameters:
        request (RegionRequest): A Pydantic model containing the following fields:
            - region_id (int): The unique identifier for the new region (i_rgn). Required.
            - zone_id (int): The ID of the zone (i_zn) this region belongs to. Required.
            - region_name (str): A descriptive name for the region (x_nm_rgn). Required.
            - max_x (float): The maximum x-coordinate of the region's bounding box (n_max_x). Required.
            - max_y (float): The maximum y-coordinate of the region's bounding box (n_max_y). Required.
            - max_z (float): The maximum z-coordinate of the region's bounding box (n_max_z). Required.
            - min_x (float): The minimum x-coordinate of the region's bounding box (n_min_x). Required.
            - min_y (float): The minimum y-coordinate of the region's bounding box (n_min_y). Required.
            - min_z (float): The minimum z-coordinate of the region's bounding box (n_min_z). Required.
            - trigger_id (int, optional): The ID of the trigger (i_trg) associated with this region, if any. Defaults to None.

    Returns:
        dict: A JSON response with the following structure:
            - message (str): A confirmation message indicating success ("Region added successfully").
            - region_id (int or str): The ID of the newly created region (i_rgn).

    Raises:
        HTTPException:
            - 400: If the request data is invalid or the zone_id/trigger_id does not exist.
            - 500: If the database operation fails or an unexpected error occurs.

    Example:
        ```bash
        curl -X POST "http://192.168.210.226:8000/add_region" \
             -H "Content-Type: application/json" \
             -d '{
                   "region_id": 1001,
                   "zone_id": 10,
                   "region_name": "Lobby Area",
                   "max_x": 50.0,
                   "max_y": 50.0,
                   "max_z": 10.0,
                   "min_x": 0.0,
                   "min_y": 0.0,
                   "min_z": 0.0,
                   "trigger_id": null
                 }'
        ```
        Response:
        ```json
        {
          "message": "Region added successfully",
          "region_id": 1001
        }
        ```

    Use Case:
        - **Scenario**: A facility manager needs to define a new region within a zone (e.g., a "Lobby Area" in a building zone) to track device movements or set up a trigger for entry/exit alerts. This endpoint is used to create the region with specific spatial boundaries.
        - **Example**: In a hospital, a region is created for the "Emergency Room" zone to monitor patient tags entering or leaving the area.

    Hint:
        - Ensure the `zone_id` exists in the `zones` table before calling this endpoint. You can verify this using the `/get_parent_zones` endpoint.
        - If associating with a trigger, confirm the `trigger_id` exists in the `triggers` table using `/list_triggers`.
        - The coordinates (min_x, max_x, etc.) should align with the map's coordinate system, which can be checked via `/get_map_metadata/{map_id}`.
    """
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

@router.delete("/delete_region/{region_id}")
async def delete_region(region_id: int):
    """
    Delete a region from the ParcoRTLS system by its ID.

    This endpoint removes a region from the `regions` table, including any associated vertices, using the stored procedure `usp_region_delete`. Deleting a region is necessary when reorganizing spatial areas or removing outdated regions. Note that associated vertices are also deleted, as they are linked via the `i_rgn` foreign key.

    Parameters:
        region_id (int): Path parameter specifying the ID of the region to delete (i_rgn). Required.

    Returns:
        dict: A JSON response with the following structure:
            - message (str): A confirmation message indicating success ("Region deleted successfully").

    Raises:
        HTTPException:
            - 404: If the region_id does not exist in the `regions` table.
            - 500: If the database operation fails or an unexpected error occurs.

    Example:
        ```bash
        curl -X DELETE "http://192.168.210.226:8000/delete_region/1001"
        ```
        Response:
        ```json
        {
          "message": "Region deleted successfully"
        }
        ```

    Use Case:
        - **Scenario**: A facility manager needs to remove a region that is no longer relevant, such as a temporary event space in a zone.
        - **Example**: In a warehouse, a region defined for a seasonal storage area is deleted after the season ends.

    Hint:
        - Before deleting, verify the region exists using `/get_region_by_id/{region_id}` to avoid unnecessary errors.
        - If the region is associated with a trigger, ensure the trigger is updated or deleted separately using `/delete_trigger/{trigger_id}` to maintain data consistency.
        - Deleting a region will cascade to its vertices, so ensure no critical data is lost.
    """
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

@router.put("/edit_region")
async def edit_region(request: RegionRequest):
    """
    Update an existing region's details in the ParcoRTLS system.

    This endpoint modifies the attributes of a region in the `regions` table, such as its name, spatial boundaries, or associated zone/trigger, using the stored procedure `usp_region_edit`. It is used to adjust region configurations when spatial definitions or associations change.

    Parameters:
        request (RegionRequest): A Pydantic model containing the following fields:
            - region_id (int): The ID of the region to update (i_rgn). Required.
            - zone_id (int): The ID of the zone (i_zn) this region belongs to. Required.
            - region_name (str): A descriptive name for the region (x_nm_rgn). Required.
            - max_x (float): The maximum x-coordinate of the region's bounding box (n_max_x). Required.
            - max_y (float): The maximum y-coordinate of the region's bounding box (n_max_y). Required.
            - max_z (float): The maximum z-coordinate of the region's bounding box (n_max_z). Required.
            - min_x (float): The minimum x-coordinate of the region's bounding box (n_min_x). Required.
            - min_y (float): The minimum y-coordinate of the region's bounding box (n_min_y). Required.
            - min_z (float): The minimum z-coordinate of the region's bounding box (n_min_z). Required.
            - trigger_id (int, optional): The ID of the trigger (i_trg) associated with this region, if any. Defaults to None.

    Returns:
        dict: A JSON response with the following structure:
            - message (str): A confirmation message indicating success ("Region edited successfully").

    Raises:
        HTTPException:
            - 400: If the request data is invalid or the zone_id/trigger_id does not exist.
            - 404: If the region_id does not exist in the `regions` table.
            - 500: If the database operation fails or an unexpected error occurs.

    Example:
        ```bash
        curl -X PUT "http://192.168.210.226:8000/edit_region" \
             -H "Content-Type: application/json" \
             -d '{
                   "region_id": 1001,
                   "zone_id": 10,
                   "region_name": "Updated Lobby Area",
                   "max_x": 60.0,
                   "max_y": 60.0,
                   "max_z": 12.0,
                   "min_x": 0.0,
                   "min_y": 0.0,
                   "min_z": 0.0,
                   "trigger_id": 2001
                 }'
        ```
        Response:
        ```json
        {
          "message": "Region edited successfully"
        }
        ```

    Use Case:
        - **Scenario**: A facility manager needs to expand the boundaries of a region due to a physical expansion of the area or update its name for clarity.
        - **Example**: In a retail store, the region for the "Checkout Area" is updated to include additional checkout counters.

    Hint:
        - Verify the new `zone_id` and `trigger_id` exist using `/get_parent_zones` and `/list_triggers` before updating.
        - Ensure the new coordinates are consistent with the map's coordinate system, which can be validated using `/get_map_metadata/{map_id}`.
        - If vertices need updating, use the `/update_vertices` endpoint in `vertex.py` after editing the region.
    """
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

@router.get("/get_region_by_id/{region_id}")
async def get_region_by_id(region_id: int):
    """
    Retrieve details of a specific region by its ID in the ParcoRTLS system.

    This endpoint fetches the details of a region from the `regions` table using the stored procedure `usp_region_select_by_id`. It returns attributes such as the region's name, zone ID, spatial boundaries, and associated trigger (if any). This is useful for inspecting or validating a region's configuration.

    Parameters:
        region_id (int): Path parameter specifying the ID of the region to retrieve (i_rgn). Required.

    Returns:
        dict: A JSON response containing the region's details, with fields such as:
            - i_rgn (int): Region ID.
            - i_zn (int): Zone ID.
            - x_nm_rgn (str): Region name.
            - n_max_x (float): Maximum x-coordinate.
            - n_max_y (float): Maximum y-coordinate.
            - n_max_z (float): Maximum z-coordinate.
            - n_min_x (float): Minimum x-coordinate.
            - n_min_y (float): Minimum y-coordinate.
            - n_min_z (float): Minimum z-coordinate.
            - i_trg (int, optional): Trigger ID, if associated.

    Raises:
        HTTPException:
            - 404: If the region_id does not exist in the `regions` table.
            - 500: If the database operation fails or an unexpected error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_region_by_id/1001"
        ```
        Response:
        ```json
        {
          "i_rgn": 1001,
          "i_zn": 10,
          "x_nm_rgn": "Lobby Area",
          "n_max_x": 50.0,
          "n_max_y": 50.0,
          "n_max_z": 10.0,
          "n_min_x": 0.0,
          "n_min_y": 0.0,
          "n_min_z": 0.0,
          "i_trg": null
        }
        ```

    Use Case:
        - **Scenario**: A developer needs to verify the configuration of a region before associating it with a new trigger or updating its vertices.
        - **Example**: In a museum, the region for an "Exhibit Hall" is checked to ensure its boundaries align with the physical space.

    Hint:
        - Use this endpoint to confirm a region's details before editing it with `/edit_region` or deleting it with `/delete_region`.
        - To retrieve the vertices associated with this region, use `/get_zone_vertices/{zone_id}` or `/get_regions_by_zone/{zone_id}`.
    """
    result = await call_stored_procedure("maint", "usp_region_select_by_id", region_id)
    if result and isinstance(result, list) and result:
        return result[0]
    raise HTTPException(status_code=404, detail="Region not found")

@router.get("/get_regions_by_zone/{zone_id}")
async def get_regions_by_zone(zone_id: int):
    """
    Fetch all regions and their associated vertices for a given zone ID in the ParcoRTLS system.

    This endpoint retrieves all regions associated with a specified zone from the `regions` table and their corresponding vertices from the `vertices` table. It uses raw SQL queries to ensure accurate filtering by `i_zn` (zone ID), combining region and vertex data into a structured response. This is essential for visualizing or analyzing the spatial layout of regions within a zone.

    Parameters:
        zone_id (int): Path parameter specifying the ID of the zone (i_zn) to filter regions by. Required.

    Returns:
        list: A list of dictionaries, each containing combined region and vertex details. If vertices exist, each dictionary includes:
            - i_rgn (int): Region ID.
            - i_zn (int): Zone ID.
            - x_nm_rgn (str): Region name.
            - n_max_x (float): Maximum x-coordinate.
            - n_max_y (float): Maximum y-coordinate.
            - n_max_z (float): Maximum z-coordinate.
            - n_min_x (float): Minimum x-coordinate.
            - n_min_y (float): Minimum y-coordinate.
            - n_min_z (float): Minimum z-coordinate.
            - i_trg (int, optional): Trigger ID, if associated.
            - i_vtx (int): Vertex ID.
            - n_x (float): Vertex x-coordinate.
            - n_y (float): Vertex y-coordinate.
            - n_z (float): Vertex z-coordinate.
            - n_ord (int): Vertex order.
        If no vertices exist, the list contains region details only (same fields minus vertex-specific ones).

    Raises:
        HTTPException:
            - 404: If no regions are found for the specified zone_id.
            - 500: If the database query fails or an unexpected error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_regions_by_zone/10"
        ```
        Response:
        ```json
        [
          {
            "i_rgn": 1001,
            "i_zn": 10,
            "x_nm_rgn": "Lobby Area",
            "n_max_x": 50.0,
            "n_max_y": 50.0,
            "n_max_z": 10.0,
            "n_min_x": 0.0,
            "n_min_y": 0.0,
            "n_min_z": 0.0,
            "i_trg": null,
            "i_vtx": 5001,
            "n_x": 0.0,
            "n_y": 0.0,
            "n_z": 0.0,
            "n_ord": 1
          },
          ...
        ]
        ```

    Use Case:
        - **Scenario**: A facility manager needs to visualize all regions within a zone, including their vertices, to plan device placements or trigger configurations.
        - **Example**: In an office building, this endpoint is used to retrieve all regions in the "Main Floor" zone to display their boundaries on a map in the Zone Viewer.

    Hint:
        - This endpoint is particularly useful for rendering region boundaries in the React frontend. Use the returned vertices to draw polygons on a map.
        - To check if a tag is within a region (e.g., for Zone L1 zones), combine this endpoint with `/trigger_contains_point/{trigger_id}` or `/zones_by_point`.
        - The endpoint uses raw queries instead of `usp_regions_select_by_zone` due to a previous issue where zone_id was misinterpreted as i_rgn. This ensures accurate filtering.
    """
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

@router.get("/get_all_regions")
async def get_all_regions():
    """
    Retrieve all regions from the ParcoRTLS system database.

    This endpoint fetches all regions from the `regions` table using the stored procedure `usp_region_list`. It provides a comprehensive list of all regions, including their attributes, which is useful for system-wide analysis or auditing.

    Parameters:
        None

    Returns:
        list: A list of dictionaries, each containing region details with fields such as:
            - i_rgn (int): Region ID.
            - i_zn (int): Zone ID.
            - x_nm_rgn (str): Region name.
            - n_max_x (float): Maximum x-coordinate.
            - n_max_y (float): Maximum y-coordinate.
            - n_max_z (float): Maximum z-coordinate.
            - n_min_x (float): Minimum x-coordinate.
            - n_min_y (float): Minimum y-coordinate.
            - n_min_z (float): Minimum z-coordinate.
            - i_trg (int, optional): Trigger ID, if associated.

    Raises:
        HTTPException:
            - 404: If no regions are found in the database.
            - 500: If the database query fails or an unexpected error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_all_regions"
        ```
        Response:
        ```json
        [
          {
            "i_rgn": 1001,
            "i_zn": 10,
            "x_nm_rgn": "Lobby Area",
            "n_max_x": 50.0,
            "n_max_y": 50.0,
            "n_max_z": 10.0,
            "n_min_x": 0.0,
            "n_min_y": 0.0,
            "n_min_z": 0.0,
            "i_trg": null
          },
          ...
        ]
        ```

    Use Case:
        - **Scenario**: A system administrator needs to audit all regions in the system to ensure proper configuration or to generate a report.
        - **Example**: In a university campus, this endpoint is used to list all regions across all buildings for a spatial analysis report.

    Hint:
        - Use this endpoint for bulk operations or when initializing a frontend application that needs a complete list of regions.
        - To fetch vertices for these regions, iterate over the returned `i_zn` values and call `/get_regions_by_zone/{zone_id}`.
        - For a campus-level overview, combine with `/get_campus_zones` from `zoneviewer_routes.py`.
    """
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

@router.get("/get_all_regions_alt")
async def get_all_regions_alt():
    """
    Retrieve all regions from the ParcoRTLS system database using an alternative method.

    This endpoint serves as an alternative to `/get_all_regions`, fetching all regions from the `regions` table using the stored procedure `usp_regions_select`. It provides the same data but may differ in implementation details or performance characteristics, offering flexibility for different use cases.

    Parameters:
        None

    Returns:
        list: A list of dictionaries, each containing region details with fields such as:
            - i_rgn (int): Region ID.
            - i_zn (int): Zone ID.
            - x_nm_rgn (str): Region name.
            - n_max_x (float): Maximum x-coordinate.
            - n_max_y (float): Maximum y-coordinate.
            - n_max_z (float): Maximum z-coordinate.
            - n_min_x (float): Minimum x-coordinate.
            - n_min_y (float): Minimum y-coordinate.
            - n_min_z (float): Minimum z-coordinate.
            - i_trg (int, optional): Trigger ID, if associated.

    Raises:
        HTTPException:
            - 404: If no regions are found in the database.
            - 500: If the database query fails or an unexpected error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_all_regions_alt"
        ```
        Response:
        ```json
        [
          {
            "i_rgn": 1001,
            "i_zn": 10,
            "x_nm_rgn": "Lobby Area",
            "n_max_x": 50.0,
            "n_max_y": 50.0,
            "n_max_z": 10.0,
            "n_min_x": 0.0,
            "n_min_y": 0.0,
            "n_min_z": 0.0,
            "i_trg": null
          },
          ...
        ]
        ```

    Use Case:
        - **Scenario**: A developer needs an alternative method to fetch all regions for testing or performance optimization.
        - **Example**: In a large-scale deployment, this endpoint is tested to compare query performance against `/get_all_regions`.

    Hint:
        - Use this endpoint when experimenting with different database access patterns or when `usp_region_list` is unavailable.
        - The data returned is identical to `/get_all_regions`, so the same frontend processing logic can be applied.
        - For campus-specific filtering, combine with `/get_campus_zones/{campus_id}` from `zoneviewer_routes.py`.
    """
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

@router.get("/get_regions_by_trigger/{trigger_id}")
async def get_regions_by_trigger(trigger_id: int):
    """
    Fetch all regions associated with a specific trigger ID in the ParcoRTLS system.

    This endpoint retrieves regions linked to a given trigger from the `regions` table using the stored procedure `usp_regions_select_by_trigger`. It returns region details, including any associated vertices, which is useful for analyzing trigger-related spatial configurations.

    Parameters:
        trigger_id (int): Path parameter specifying the ID of the trigger (i_trg) to filter regions by. Required.

    Returns:
        list: A list of dictionaries containing region and vertex details, with fields such as:
            - i_rgn (int): Region ID.
            - i_zn (int): Zone ID.
            - x_nm_rgn (str): Region name.
            - n_max_x (float): Maximum x-coordinate.
            - n_max_y (float): Maximum y-coordinate.
            - n_max_z (float): Maximum z-coordinate.
            - n_min_x (float): Minimum x-coordinate.
            - n_min_y (float): Minimum y-coordinate.
            - n_min_z (float): Minimum z-coordinate.
            - i_trg (int): Trigger ID.
            - Additional vertex fields (if applicable), such as i_vtx, n_x, n_y, n_z, n_ord.

    Raises:
        HTTPException:
            - 404: If no regions are found for the specified trigger_id.
            - 500: If the database query fails, the stored procedure returns an unexpected response, or an unexpected error occurs.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/get_regions_by_trigger/2001"
        ```
        Response:
        ```json
        [
          {
            "i_rgn": 1002,
            "i_zn": 10,
            "x_nm_rgn": "Trigger Region",
            "n_max_x": 30.0,
            "n_max_y": 30.0,
            "n_max_z": 5.0,
            "n_min_x": 10.0,
            "n_min_y": 10.0,
            "n_min_z": 0.0,
            "i_trg": 2001,
            "i_vtx": 5002,
            "n_x": 10.0,
            "n_y": 10.0,
            "n_z": 0.0,
            "n_ord": 1
          },
          ...
        ]
        ```

    Use Case:
        - **Scenario**: A security team needs to inspect all regions associated with a specific trigger to verify its spatial coverage.
        - **Example**: In a hospital, this endpoint is used to check the regions linked to an "Emergency Alert" trigger to ensure they cover all critical areas.

    Hint:
        - Verify the `trigger_id` exists using `/list_triggers` before calling this endpoint.
        - To check if a tag is within a trigger's region (e.g., for Zone L1 zones), combine this endpoint with `/trigger_contains_point/{trigger_id}`.
        - The endpoint handles cases where the stored procedure returns a success message dictionary, ensuring proper 404 handling.
    """
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