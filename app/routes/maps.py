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

router = APIRouter(tags=["maps"])
logger = logging.getLogger(__name__)

class MapNameUpdateRequest(BaseModel):
    map_id: int
    name: str

@router.post("/update_map_name")
async def update_map_name(request: MapNameUpdateRequest):
    """
    Updates the name of a map in the ParcoRTLS system.

    This endpoint allows administrators to rename a map identified by its map_id. The new name is validated for non-empty content and length constraints before updating the database. It is used to maintain accurate map labels displayed in the React frontend for visualization and zone management.

    Parameters:
    - request (MapNameUpdateRequest): The request body containing:
        - map_id (int, required): The unique identifier of the map to update.
        - name (str, required): The new name for the map, must be non-empty and less than 100 characters.

    Returns:
    - dict: A JSON response with a success message.
        - message (str): Confirmation that the map name was updated successfully.

    Raises:
    - HTTPException (400): If the map name is empty or exceeds 100 characters.
    - HTTPException (404): If the specified map_id does not exist in the database.
    - HTTPException (500): If an unexpected error occurs during the database operation.

    Example:
    ```bash
    curl -X POST "http://192.168.210.226:8000/api/update_map_name" \
         -H "Content-Type: application/json" \
         -d '{"map_id": 1, "name": "Campus Main Building"}'
    ```
    Response:
    ```json
    {"message": "Map name updated successfully"}
    ```

    Use Case:
    - An administrator updates the name of a map from "Building A" to "Campus Main Building" to reflect a new naming convention in the ParcoRTLS system. This ensures the map is correctly labeled in the React frontend when users view zone layouts or track tags.

    Hint:
    - Ensure the map_id corresponds to an existing map in the `maps` table. You can verify map IDs using the `/get_maps` endpoint.
    - Map names should be descriptive to help users identify the physical location in the RTLS interface.
    """
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

@router.get("/get_maps")
async def get_maps():
    """
    Retrieves a list of all maps in the ParcoRTLS system.

    This endpoint queries the database to fetch all maps stored in the `maps` table, typically used to populate a dropdown or list in the React frontend for map selection or management.

    Parameters:
    - None

    Returns:
    - List[dict]: A list of maps, each containing details such as:
        - i_map (int): The unique map identifier.
        - x_nm_map (str): The name of the map.
        - Other fields as returned by the `usp_map_list` stored procedure.

    Raises:
    - HTTPException (404): If no maps are found in the database.
    - HTTPException (500): If an unexpected error occurs during the database operation.

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/api/get_maps"
    ```
    Response:
    ```json
    [
        {"i_map": 1, "x_nm_map": "Campus Main Building", ...},
        {"i_map": 2, "x_nm_map": "Parking Lot A", ...}
    ]
    ```

    Use Case:
    - A frontend developer uses this endpoint to populate a map selection menu in the ParcoRTLS interface, allowing users to choose a map for viewing zone layouts or tracking assets.
    - An administrator uses this to verify all available maps before assigning them to zones.

    Hint:
    - The response format depends on the `usp_map_list` stored procedure. Check the stored procedure definition in the Parco database to understand the exact fields returned.
    """
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

@router.get("/get_map/{map_id}")
async def get_map(map_id: int):
    """
    Retrieves the stored image for a specific map in the ParcoRTLS system.

    This endpoint serves the binary image data of a map, which is used by the React frontend to display the map in the user interface for zone visualization or tag tracking.

    Parameters:
    - map_id (int, path parameter, required): The unique identifier of the map whose image is to be retrieved.

    Returns:
    - Response: A binary response containing the map image with the appropriate media type (e.g., `image/png`, `image/jpeg`).

    Raises:
    - HTTPException (404): If no image is found for the specified map_id.
    - HTTPException (500): If an unexpected error occurs during the database operation.

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/api/get_map/1" --output map_image.png
    ```
    Response: Binary image data (saved as `map_image.png` in the example).

    Use Case:
    - The React frontend calls this endpoint to fetch the map image for a specific map_id, displaying it as the background for zone layouts or real-time tag tracking in the ParcoRTLS interface.

    Hint:
    - Ensure the `x_format` field in the `maps` table is correctly set (e.g., 'png', 'jpeg') to serve the image with the correct media type.
    - Large images may impact performance; consider optimizing image sizes in the database.
    """
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

@router.get("/get_map_data/{zone_id}")
async def get_map_data(zone_id: int):
    """
    Retrieves map data (image URL and bounds) for a specific zone in the ParcoRTLS system.

    This endpoint is designed for the React frontend's `Map.js` component, providing the URL to fetch the map image and the geographical bounds for rendering the map correctly.

    Parameters:
    - zone_id (int, path parameter, required): The unique identifier of the zone whose associated map data is to be retrieved.

    Returns:
    - dict: A JSON response containing:
        - imageUrl (str): The URL to fetch the map image (points to `/get_map/{zone_id}`).
        - bounds (List[List[float]]): The geographical bounds of the map as [[min_y, min_x], [max_y, max_x]].

    Raises:
    - HTTPException (404): If the zone or its associated map is not found.
    - HTTPException (500): If an unexpected error occurs during the database operation.

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/api/get_map_data/1"
    ```
    Response:
    ```json
    {
        "imageUrl": "http://192.168.210.226:8000/api/get_map/1",
        "bounds": [[0, 0], [100, 100]]
    }
    ```

    Use Case:
    - The React frontend uses this endpoint to fetch map data for a specific zone, enabling the `Map.js` component to render the map with correct scaling and positioning for tag tracking or zone visualization.

    Hint:
    - Ensure the zone_id is valid and linked to a map in the `zones` and `maps` tables. Use `/get_campus_zones/{campus_id}` to verify zone mappings.
    - Default bounds (e.g., [0, 0], [100, 100]) are used if database values are null; verify map metadata for accuracy.
    """
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

@router.post("/add_map")
async def add_map(request: MapAddRequest):
    """
    Adds a new map to the ParcoRTLS system.

    This endpoint allows administrators to insert a new map with a name and image into the database, typically used when onboarding new physical locations or updating map assets.

    Parameters:
    - request (MapAddRequest): The request body containing:
        - name (str, required): The name of the new map.
        - image (str, required): The image data or reference for the map (handled by `usp_map_insert`).

    Returns:
    - dict: A JSON response with a success message.
        - message (str): Confirmation that the map was added successfully.

    Raises:
    - HTTPException (500): If the map insertion fails or an unexpected error occurs.

    Example:
    ```bash
    curl -X POST "http://192.168.210.226:8000/api/add_map" \
         -H "Content-Type: application/json" \
         -d '{"name": "New Campus Map", "image": "base64_encoded_image_data"}'
    ```
    Response:
    ```json
    {"message": "Map added successfully"}
    ```

    Use Case:
    - An administrator adds a new map for a recently constructed building, enabling the ParcoRTLS system to track tags within its zones.

    Hint:
    - The `image` field format depends on the `usp_map_insert` stored procedure. Verify whether it expects base64-encoded data or a file path.
    - Ensure the map name is unique to avoid confusion in the frontend interface.
    """
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

@router.delete("/delete_map/{map_id}")
async def delete_map(map_id: int):
    """
    Deletes a map from the ParcoRTLS system.

    This endpoint removes a map identified by its map_id, typically used when a map is no longer needed or was added in error.

    Parameters:
    - map_id (int, path parameter, required): The unique identifier of the map to delete.

    Returns:
    - dict: A JSON response with a success message.
        - message (str): Confirmation that the map was deleted successfully.

    Raises:
    - HTTPException (404): If the specified map_id does not exist.
    - HTTPException (500): If an unexpected error occurs during the database operation.

    Example:
    ```bash
    curl -X DELETE "http://192.168.210.226:8000/api/delete_map/1"
    ```
    Response:
    ```json
    {"message": "Map 1 deleted successfully"}
    ```

    Use Case:
    - An administrator deletes an outdated map that is no longer relevant due to a building demolition or map replacement.

    Hint:
    - Ensure no zones are linked to the map before deletion, as this may cause orphaned zones. Check with `/get_campus_zones/{campus_id}`.
    """
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

@router.get("/get_map_metadata/{map_id}")
async def get_map_metadata(map_id: int):
    """
    Retrieves metadata for a specific map in the ParcoRTLS system.

    This endpoint fetches metadata such as dimensions and scaling factors, used for configuring map rendering in the frontend or validating map properties.

    Parameters:
    - map_id (int, path parameter, required): The unique identifier of the map whose metadata is to be retrieved.

    Returns:
    - List[dict]: Metadata details as returned by the `usp_map_metadata` stored procedure, typically including dimensions and scaling factors.

    Raises:
    - HTTPException (404): If no metadata is found for the specified map_id.
    - HTTPException (500): If an unexpected error occurs during the database operation.

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/api/get_map_metadata/1"
    ```
    Response:
    ```json
    [{"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100, ...}]
    ```

    Use Case:
    - A developer uses this endpoint to fetch map dimensions for scaling the map image correctly in the React frontend.

    Hint:
    - The exact metadata fields depend on the `usp_map_metadata` stored procedure. Review its definition for clarity.
    """
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
    Updates metadata for a specific map in the ParcoRTLS system.

    This endpoint allows administrators to update map metadata, such as geographical bounds, to ensure accurate rendering in the frontend.

    Parameters:
    - request (MapUpdateRequest): The request body containing:
        - map_id (int, required): The unique identifier of the map.
        - min_x (float, required): The minimum X coordinate of the map.
        - min_y (float, required): The minimum Y coordinate of the map.
        - max_x (float, required): The maximum X coordinate of the map.
        - max_y (float, required): The maximum Y coordinate of the map.

    Returns:
    - dict: A JSON response with a success message.
        - message (str): Confirmation that the metadata was updated successfully.

    Raises:
    - HTTPException (404): If the metadata update fails (e.g., map_id not found).
    - HTTPException (500): If an unexpected error occurs during the database operation.

    Example:
    ```bash
    curl -X PUT "http://192.168.210.226:8000/api/update_map_metadata" \
         -H "Content-Type: application/json" \
         -d '{"map_id": 1, "min_x": 0, "min_y": 0, "max_x": 200, "max_y": 150}'
    ```
    Response:
    ```json
    {"message": "Map metadata updated successfully"}
    ```

    Use Case:
    - An administrator updates the bounds of a map to reflect a resized or reoriented physical layout, ensuring accurate tag positioning in the frontend.

    Hint:
    - Validate the coordinate values to ensure they are meaningful for the map’s physical layout.
    """
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

@router.get("/get_campus_zones/{campus_id}")
async def get_campus_zones(campus_id: int):
    """
    Retrieves the zone hierarchy for a specific campus in the ParcoRTLS system.

    This endpoint fetches all zones associated with a campus, organized hierarchically by parent-child relationships, used for displaying zone structures in the frontend or checking tag locations.

    Parameters:
    - campus_id (int, path parameter, required): The unique identifier of the campus whose zones are to be retrieved.

    Returns:
    - dict: A JSON response containing:
        - zones (List[dict]): A list of top-level zones, each with:
            - zone_id (int): The zone identifier.
            - zone_name (str): The name of the zone.
            - zone_type (int): The type of zone.
            - parent_zone_id (int or None): The ID of the parent zone.
            - map_id (int or None): The associated map ID.
            - children (List[dict]): Child zones in the hierarchy.

    Raises:
    - HTTPException (404): If no zones are found for the specified campus_id.
    - HTTPException (500): If an unexpected error occurs during the database operation.

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/api/get_campus_zones/1"
    ```
    Response:
    ```json
    {
        "zones": [
            {
                "zone_id": 1,
                "zone_name": "Campus Main",
                "zone_type": 1,
                "parent_zone_id": null,
                "map_id": 1,
                "children": [
                    {
                        "zone_id": 2,
                        "zone_name": "Building A",
                        "zone_type": 2,
                        "parent_zone_id": 1,
                        "map_id": 1,
                        "children": []
                    }
                ]
            }
        ]
    }
    ```

    Use Case:
    - The frontend uses this endpoint to display a tree view of zones for a campus, allowing users to navigate the zone hierarchy or check if a tag is within a specific campus zone (e.g., Zone L1 zones).
    - An administrator uses this to verify zone-to-map assignments before updating map metadata.

    Hint:
    - This endpoint is useful for checking if a tag is on a campus by traversing the zone hierarchy and verifying tag locations against Zone L1 zones.
    - The recursive CTE in the query ensures all child zones are included; ensure the `zones` table has correct `i_pnt_zn` values for hierarchy integrity.
    """
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