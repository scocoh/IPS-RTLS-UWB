"""
/home/parcoadmin/parco_fastapi/app/routes/zone.py
Version: 0.1.5 (Enhanced endpoint documentation for clarity and usability)
Zone management endpoints for ParcoRTLS FastAPI application.
# VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/zone.py 0P.10B.02
# CHANGED: Enhanced endpoint docstrings with detailed descriptions, parameters, return values, examples, use cases, hints, and error handling; bumped to 0.1.5
# PREVIOUS: Added tags=["zones"] to APIRouter for Swagger UI grouping, bumped to 0.1.4
# PREVIOUS: Added HEAD support for /get_map/{zone_id} endpoint, version 0.1.3
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
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from models import ZoneRequest
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["zones"])

@router.get("/get_parents")
async def get_parents():
    """
    Fetch all top-level parent zones from the ParcoRTLSMaint database.

    This endpoint retrieves zones that have no parent zone (i.e., `i_pnt_zn IS NULL`), representing the highest level in the zone hierarchy, such as campuses in the ParcoRTLS system. These zones are typically used as the root nodes for building zone hierarchies in the frontend Zone Viewer or for initializing zone selection in administrative interfaces.

    Parameters:
        None

    Returns:
        dict: A JSON object with a single key "parents" containing a list of dictionaries. Each dictionary represents a parent zone with the following fields:
            - i_zn (int): The unique zone ID.
            - i_typ_zn (int): The zone type ID (e.g., 1 for Campus).
            - x_nm_zn (str): The name of the zone.
        Example: {"parents": [{"i_zn": 1, "i_typ_zn": 1, "x_nm_zn": "Main Campus"}, ...]}

    Raises:
        HTTPException:
            - 500: If an unexpected error occurs during database query execution (e.g., database connectivity issues).

    Example Usage:
        ```bash
        curl -X GET "http://192.168.210.226:8000/api/get_parents" -H "accept: application/json"
        ```
        Response:
        ```json
        {
            "parents": [
                {"i_zn": 1, "i_typ_zn": 1, "x_nm_zn": "Main Campus"},
                {"i_zn": 2, "i_typ_zn": 1, "x_nm_zn": "West Campus"}
            ]
        }
        ```

    Use Case:
        - **Zone Hierarchy Initialization**: The frontend React app (running at http://192.168.210.226:3000) calls this endpoint to populate a dropdown or tree view with top-level zones (e.g., campuses) when a user starts configuring zones or viewing zone maps.
        - **Administrative Dashboard**: An admin uses this endpoint to select a parent zone before adding child zones or assigning devices to a campus-level zone.

    Hint:
        - This endpoint is useful for identifying zones of type `i_typ_zn=1` (Campus), which can be used to check if a tag is located within a campus boundary by combining with `/get_zone_vertices/{zone_id}` to fetch boundary coordinates.
        - Ensure CORS is configured in `app.py` to allow requests from the React frontend.
    """
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
    """
    Fetch all child zones of a specified parent zone.

    This endpoint retrieves all zones that have the specified `parent_id` as their parent zone (`i_pnt_zn`), allowing the construction of a zone hierarchy below a given parent zone. In the ParcoRTLS system, this is used to display sub-zones (e.g., buildings, floors, or rooms) under a parent zone like a campus or building in the Zone Viewer.

    Parameters:
        parent_id (int, required): The ID of the parent zone (`i_zn`) whose child zones are to be retrieved.

    Returns:
        dict: A JSON object with a single key "children" containing a list of child zone dictionaries. Each dictionary includes fields returned by the `usp_zone_children_select` stored procedure, typically:
            - i_zn (int): The unique zone ID.
            - x_nm_zn (str): The name of the zone.
            - i_typ_zn (int): The zone type ID.
            - i_pnt_zn (int): The parent zone ID.
        Example: {"children": [{"i_zn": 3, "x_nm_zn": "Building A", "i_typ_zn": 2, "i_pnt_zn": 1}, ...]}
        If no children are found, returns {"children": []}.

    Raises:
        HTTPException:
            - 404: If no child zones are found for the specified `parent_id` (handled by returning an empty list).
            - 500: If an unexpected error occurs during stored procedure execution.
            - Custom status codes: If a `DatabaseError` occurs, the status code from the error is used (e.g., 400 for invalid input).

    Example Usage:
        ```bash
        curl -X GET "http://192.168.210.226:8000/api/get_children/1" -H "accept: application/json"
        ```
        Response:
        ```json
        {
            "children": [
                {"i_zn": 3, "x_nm_zn": "Building A", "i_typ_zn": 2, "i_pnt_zn": 1},
                {"i_zn": 4, "x_nm_zn": "Building B", "i_typ_zn": 2, "i_pnt_zn": 1}
            ]
        }
        ```

    Use Case:
        - **Zone Hierarchy Navigation**: The frontend uses this endpoint to expand a parent zone in a tree view, showing its child zones (e.g., buildings under a campus or rooms under a floor).
        - **Zone Configuration**: An admin calls this endpoint to list child zones when assigning devices or triggers to specific sub-zones within a parent zone.

    Hint:
        - Combine this endpoint with `/get_zone_vertices/{zone_id}` to fetch the boundaries of child zones for rendering on a map.
        - If the stored procedure `usp_zone_children_select` returns a string, it is JSON-parsed, which may indicate legacy behavior; verify the stored procedure output format in the database schema.
    """
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
    """
    Fetch the map image associated with a selected zone as a downloadable file.

    This endpoint retrieves the binary map image linked to a zone (via its `i_map` field) from the `maps` table in the ParcoRTLSMaint database. It supports both GET (to download the image) and HEAD (to check metadata without downloading) requests, facilitating efficient map rendering in the frontend Zone Viewer. The image is returned as a file attachment with a dynamically generated filename.

    Parameters:
        zone_id (int, required): The ID of the zone (`i_zn`) whose associated map image is to be retrieved.

    Returns:
        Response: A FastAPI Response object containing:
            - content: The binary image data (`img_data` from the `maps` table).
            - media_type: The image format (e.g., "image/png", "image/jpeg") based on `x_format` in the `maps` table.
            - headers: A "Content-Disposition" header specifying the filename (e.g., "attachment; filename=map_zone_5.png").
        For HEAD requests, returns only the headers without the content.

    Raises:
        HTTPException:
            - 404: If the zone is not found (`i_zn` does not exist) or no map is associated with the zone (`i_map` is null or invalid).
            - 500: If an unexpected error occurs during database queries or image retrieval.

    Example Usage:
        ```bash
        curl -X GET "http://192.168.210.226:8000/api/get_map/5" -H "accept: image/png" --output map_zone_5.png
        ```
        ```bash
        curl -X HEAD "http://192.168.210.226:8000/api/get_map/5" -H "accept: image/png"
        ```
        Response (GET):
        - Binary PNG image data, downloadable as "map_zone_5.png".
        Response (HEAD):
        - Headers including "Content-Disposition: attachment; filename=map_zone_5.png".

    Use Case:
        - **Map Visualization**: The React frontend calls this endpoint to display the map image associated with a zone in the Zone Viewer, overlaying zone boundaries or device positions.
        - **Resource Verification**: The frontend uses a HEAD request to check if a map exists for a zone before attempting to load it, optimizing performance.

    Hint:
        - Ensure CORS middleware in `app.py` is configured to allow requests from `http://192.168.210.226:3000` to avoid cross-origin issues.
        - The `x_format` field in the `maps` table determines the media type; verify supported formats (e.g., PNG, JPEG) in the database to handle edge cases.
        - For large maps, consider implementing caching or compression to improve performance.
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
    """
    Fetch vertices for a selected zone to draw its boundary.

    This endpoint retrieves the vertices (coordinates) that define the boundary of a specified zone, using the `usp_zone_vertices_select_by_zone` stored procedure. In the ParcoRTLS system, these vertices are used to render the polygon shape of a zone on a map in the Zone Viewer, enabling visualization of zone boundaries for navigation or device tracking.

    Parameters:
        zone_id (int, required): The ID of the zone (`i_zn`) whose vertices are to be retrieved.

    Returns:
        dict: A JSON object with a single key "vertices" containing a list of dictionaries. Each dictionary represents a vertex with fields returned by the stored procedure, typically:
            - i_vtx (int): The vertex ID.
            - i_rgn (int): The region ID associated with the vertex.
            - n_x (float): The x-coordinate.
            - n_y (float): The y-coordinate.
            - n_z (float): The z-coordinate (may be null for 2D zones).
            - n_ord (int): The order of the vertex in the boundary.
        Example: {"vertices": [{"i_vtx": 1, "i_rgn": 10, "n_x": 0.0, "n_y": 0.0, "n_z": 0.0, "n_ord": 1}, ...]}

    Raises:
        HTTPException:
            - 404: If no vertices are found for the specified `zone_id`.
            - 500: If an unexpected error occurs during stored procedure execution.

    Example Usage:
        ```bash
        curl -X GET "http://192.168.210.226:8000/api/get_zone_vertices/5" -H "accept: application/json"
        ```
        Response:
        ```json
        {
            "vertices": [
                {"i_vtx": 1, "i_rgn": 10, "n_x": 0.0, "n_y": 0.0, "n_z": 0.0, "n_ord": 1},
                {"i_vtx": 2, "i_rgn": 10, "n_x": 10.0, "n_y": 0.0, "n_z": 0.0, "n_ord": 2},
                {"i_vtx": 3, "i_rgn": 10, "n_x": 10.0, "n_y": 10.0, "n_z": 0.0, "n_ord": 3}
            ]
        }
        ```

    Use Case:
        - **Zone Boundary Rendering**: The frontend uses this endpoint to fetch vertex coordinates and draw the polygon shape of a zone on a map, helping users visualize the spatial extent of a zone (e.g., a room or building).
        - **Tag Location Validation**: Combine with `/triggers_by_point` to check if a tag's coordinates fall within a zone's boundary for real-time location tracking.

    Hint:
        - For zones of type `i_typ_zn=1` (Campus), these vertices can be used to determine if a tag is on a campus by checking if its coordinates lie within the polygon.
        - The `n_ord` field indicates the order of vertices, which is critical for correctly drawing the polygon; ensure the frontend respects this order.
    """
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
    """
    Fetch all zone types from the ParcoRTLSMaint database.

    This endpoint retrieves all zone types from the `tlkzonetypes` table, which define the hierarchical levels of zones in the ParcoRTLS system (e.g., Campus, Building, Floor, Room). Each zone type is mapped to an API endpoint for adding triggers, facilitating integration with trigger management.

    Parameters:
        None

    Returns:
        list: A list of dictionaries, each representing a zone type with the following fields:
            - zone_level (int): The zone type ID (`i_typ_zn`, e.g., 1 for Campus, 2 for Building).
            - zone_name (str): The description of the zone type (`x_dsc_zn`, e.g., "Campus").
            - api_endpoint (str): The API endpoint for adding triggers related to this zone type (e.g., "/api/add_trigger").
        Example: [{"zone_level": 1, "zone_name": "Campus", "api_endpoint": "/api/add_trigger"}, ...]
        If no zone types are found, returns an empty list: [].

    Raises:
        HTTPException:
            - 500: If an unexpected error occurs during database query execution.

    Example Usage:
        ```bash
        curl -X GET "http://192.168.210.226:8000/api/get_zone_types" -H "accept: application/json"
        ```
        Response:
        ```json
        [
            {"zone_level": 1, "zone_name": "Campus", "api_endpoint": "/api/add_trigger"},
            {"zone_level": 2, "zone_name": "Building", "api_endpoint": "/api/add_trigger"},
            {"zone_level": 3, "zone_name": "Floor", "api_endpoint": "/api/add_trigger"}
        ]
        ```

    Use Case:
        - **Zone Configuration UI**: The frontend uses this endpoint to populate a dropdown or list of zone types when creating or editing zones, ensuring users select valid zone types.
        - **Trigger Assignment**: The `api_endpoint` field guides the frontend to the correct endpoint for adding triggers to zones of specific types.

    Hint:
        - The `api_mapping` dictionary hardcodes `/api/add_trigger` for all zone types; verify if custom endpoints are needed for specific zone types in future updates.
        - Use this endpoint in conjunction with `/create_zone` to ensure the selected `zone_level` is valid before creating a new zone.
    """
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
    """
    Fetch all top-level parent zones from the ParcoRTLSMaint database.

    Similar to `/get_parents`, this endpoint retrieves zones with no parent zone (`i_pnt_zn IS NULL`), such as campuses, but returns a simpler structure with only zone ID and name. It is used in scenarios where a minimal representation of top-level zones is needed, such as dropdowns or quick selections in the ParcoRTLS frontend.

    Parameters:
        None

    Returns:
        dict: A JSON object with a single key "zones" containing a list of dictionaries. Each dictionary represents a parent zone with:
            - zone_id (int): The unique zone ID (`i_zn`).
            - name (str): The name of the zone (`x_nm_zn`).
        Example: {"zones": [{"zone_id": 1, "name": "Main Campus"}, ...]}
        If no parent zones are found, returns {"zones": []}.

    Raises:
        HTTPException:
            - 500: If an unexpected error occurs during database query execution.

    Example Usage:
        ```bash
        curl -X GET "http://192.168.210.226:8000/api/get_parent_zones" -H "accept: application/json"
        ```
        Response:
        ```json
        {
            "zones": [
                {"zone_id": 1, "name": "Main Campus"},
                {"zone_id": 2, "name": "West Campus"}
            ]
        }
        ```

    Use Case:
        - **Zone Selection**: The frontend uses this endpoint to populate a dropdown for selecting a top-level zone when configuring devices, triggers, or sub-zones.
        - **Simplified Hierarchy View**: Unlike `/get_parents`, this endpoint provides a lightweight response for scenarios where only zone IDs and names are needed.

    Hint:
        - This endpoint is redundant with `/get_parents` but returns fewer fields; consider consolidating or deprecating one in future iterations to reduce API complexity.
        - For campus-level tag tracking, combine with `/get_zone_vertices/{zone_id}` to check if a tag's coordinates are within a campus boundary.
    """
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