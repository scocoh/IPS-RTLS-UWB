# Name: zonebuilder_routes.py
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

# /home/parcoadmin/parco_fastapi/app/routes/zonebuilder_routes.py
# VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/zonebuilder_routes.py 0P.10B.23
# --- CHANGED: Bumped version from 0P.10B.22 to 0P.10B.23
# --- FIXED: Added enhanced documentation for /api/get_all_devices, /api/add_device, /api/edit_device, /api/delete_device, and /validate-support-access endpoints
# --- PREVIOUS: Enhanced endpoint documentation with detailed docstrings, including descriptions, parameters, return values, examples, use cases, hints, and error handling, version 0P.10B.22
# --- PREVIOUS: Added /get_zone_vertices/{zone_id} endpoint to fetch vertices for a specific zone, excluding child zones and trigger regions, version 0P.10B.21
# 
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from fastapi import APIRouter, Depends, HTTPException, Response, Form, Body
from database.db import execute_raw_query, get_async_db_pool
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from PIL import Image
import sys

router = APIRouter()
logger = logging.getLogger(__name__)
logger.debug(f"sys.path: {sys.path}")

# Database connection configuration (adjust as per your setup)
DB_CONFIG = {
    "dbname": "maint",
    "user": "parcoadmin",  # Replace with your DB username
    "password": "parcoMCSE04106!",  # Replace with your DB password
    "host": "localhost",  # Replace with your DB host if different
    "port": "5432"  # Replace with your DB port if different
}

@router.get("/get_maps")
async def get_maps():
    """
    Retrieve a list of all available maps from the ParcoRTLS database.

    This endpoint fetches metadata for all maps stored in the `maps` table of the `maint` schema.
    It is used by the Zone Builder tool in the ParcoRTLS system to display available maps for
    creating or editing zones. Each map is identified by a unique ID and name, which are returned
    in a structured JSON response for use in the React frontend.

    Parameters:
        None

    Returns:
        dict: A JSON object with a single key "maps" containing a list of dictionaries. Each dictionary
              represents a map with the following keys:
              - map_id (int): The unique identifier of the map (i_map).
              - name (str): The name of the map (x_nm_map).

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/get_maps
        ```
        Response:
        ```json
        {
            "maps": [
                {"map_id": 1, "name": "Campus A Floorplan"},
                {"map_id": 2, "name": "Building B Layout"}
            ]
        }
        ```

    Use Case:
        - A facility manager uses the Zone Builder tool to create a new zone (e.g., a room or floor).
          This endpoint provides the list of available maps to select as the base map for the zone,
          ensuring the zone is associated with the correct floorplan or layout.

    Hint:
        - To verify if a map is associated with a specific campus (Zone L1), cross-reference the
          returned map_id with the zones table (i_map column) where i_typ_zn = 1.
        - Ensure the frontend handles cases where the map list is empty by displaying a fallback UI.

    Errors:
        - 500 (Internal Server Error): Raised if there is a database connection issue or an unexpected
          error occurs during query execution. The error message includes details for debugging.
    """
    try:
        maps_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map FROM maps"
        )
        logger.info(f"Fetched {len(maps_data)} maps")
        return {"maps": [{"map_id": m["i_map"], "name": m["x_nm_map"]} for m in maps_data]}
    except Exception as e:
        logger.error(f"Error retrieving maps: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving maps: {str(e)}")

@router.get("/get_map_data/{map_id}")
async def get_map_data(map_id: int):
    """
    Fetch map data for the Zone Builder, including the image URL and coordinate bounds.

    This endpoint retrieves metadata for a specific map, identified by its map_id, from the `maps`
    table in the `maint` schema. It returns the URL to fetch the map image and the map's coordinate
    bounds (min_x, min_y, max_x, max_y), which are used by the Zone Builder tool to render the map
    correctly in the React frontend. Unlike some other endpoints, it does not perform a zone lookup.

    Parameters:
        map_id (int, required, path): The unique identifier of the map (i_map) to fetch data for.

    Returns:
        dict: A JSON object with the following keys:
              - imageUrl (str): The URL to fetch the map image (e.g., /zonebuilder/get_map/{map_id}).
              - bounds (list): A list of two lists representing the map's coordinate bounds:
                - [[min_y, min_x], [max_y, max_x]].

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/get_map_data/1
        ```
        Response:
        ```json
        {
            "imageUrl": "/zonebuilder/get_map/1",
            "bounds": [[0.0, 0.0], [100.0, 200.0]]
        }
        ```

    Use Case:
        - When a user selects a map in the Zone Builder tool to create a new zone, this endpoint
          provides the necessary data to display the map image and align it with the coordinate
          system, allowing the user to draw zone boundaries accurately.

    Hint:
        - The imageUrl returned is relative to the backend server. The frontend should prepend the
          base URL (http://192.168.210.226:8000) to construct the full URL.
        - Use this endpoint in conjunction with /get_map/{map_id} to fetch the actual image data.

    Errors:
        - 404 (Not Found): Raised if no map is found for the provided map_id.
        - 500 (Internal Server Error): Raised if there is a database connection issue or an unexpected
          error occurs during query execution.
    """
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map, min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No map found for map_id={map_id}")
        
        data = map_data[0]
        logger.info(f"Fetched map data for map_id={map_id}: {data['x_nm_map']}")
        return {
            "imageUrl": f"/zonebuilder/get_map/{map_id}",
            "bounds": [[data["min_y"], data["min_x"]], [data["max_y"], data["max_x"]]]
        }
    except Exception as e:
        logger.error(f"Error retrieving map data for map_id={map_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map data: {str(e)}")

@router.get("/get_map_metadata/{map_id}")
async def get_map_metadata(map_id: int):
    """
    Retrieve metadata for a specific map, including its ID, name, and coordinate bounds.

    This endpoint fetches metadata for a map identified by its map_id from the `maps` table in the
    `maint` schema. It provides detailed information such as the map's name and coordinate bounds
    (min_x, min_y, max_x, max_y), which are used by the Zone Builder tool to configure map displays
    or validate zone placements in the ParcoRTLS system.

    Parameters:
        map_id (int, required, path): The unique identifier of the map (i_map) to fetch metadata for.

    Returns:
        dict: A JSON object with the following keys:
              - map_id (int): The unique identifier of the map.
              - name (str): The name of the map (x_nm_map).
              - min_x (float): The minimum x-coordinate of the map.
              - min_y (float): The minimum y-coordinate of the map.
              - max_x (float): The maximum x-coordinate of the map.
              - max_y (float): The maximum y-coordinate of the map.

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/get_map_metadata/1
        ```
        Response:
        ```json
        {
            "map_id": 1,
            "name": "Campus A Floorplan",
            "min_x": 0.0,
            "min_y": 0.0,
            "max_x": 200.0,
            "max_y": 100.0
        }
        ```

    Use Case:
        - A developer integrating the Zone Builder tool needs to display map metadata in the UI or
          validate that a zone's vertices fall within the map's bounds. This endpoint provides the
          necessary metadata for such tasks.

    Hint:
        - Use this endpoint to pre-validate map coordinates before creating zones or vertices to
          ensure they align with the map's bounds.
        - For campus-level checks (Zone L1), verify the map_id is associated with a zone where
          i_typ_zn = 1 in the zones table.

    Errors:
        - 404 (Not Found): Raised if no metadata is found for the provided map_id.
        - 500 (Internal Server Error): Raised if there is a database connection issue or an unexpected
          error occurs during query execution.
    """
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT i_map, x_nm_map, min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No metadata found for map_id={map_id}")
        data = map_data[0]
        logger.info(f"Fetched map metadata for map_id={map_id}: {data['x_nm_map']}")
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
    """
    Fetch all zones to allow selection as parent zones in the Zone Builder.

    This endpoint retrieves a list of all zones from the `zones` table in the `maint` schema,
    sorted by zone type and name. It is used in the Zone Builder tool to populate a dropdown or
    list of potential parent zones when creating a new zone, supporting the hierarchical structure
    of zones in the ParcoRTLS system (e.g., campuses, buildings, floors).

    Parameters:
        None

    Returns:
        dict: A JSON object with a single key "zones" containing a list of dictionaries. Each dictionary
              represents a zone with the following keys:
              - zone_id (int): The unique identifier of the zone (i_zn).
              - name (str): The name of the zone (x_nm_zn).
              - level (int): The zone type (i_typ_zn, e.g., 1 for campus, 2 for building).

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/get_parent_zones
        ```
        Response:
        ```json
        {
            "zones": [
                {"zone_id": 1, "name": "Main Campus", "level": 1},
                {"zone_id": 2, "name": "Building A", "level": 2}
            ]
        }
        ```

    Use Case:
        - When creating a new zone in the Zone Builder, a user needs to specify a parent zone (e.g.,
          a floor zone under a building). This endpoint provides the list of all zones that can be
          selected as parents, ensuring the zone hierarchy is maintained.

    Hint:
        - For campus-level operations (Zone L1), filter the response to include only zones where
          level = 1 to identify top-level campuses.
        - The frontend should handle cases where no zones are returned by prompting the user to create
          a top-level zone first.

    Errors:
        - 500 (Internal Server Error): Raised if the database pool is unavailable or an unexpected
          error occurs during query execution. The error message includes details for debugging.
    """
    try:
        logger.debug("Attempting to get database pool for maint in get_parent_zones")
        pool = await get_async_db_pool("maint")
        if not pool:
            logger.error("Database pool unavailable for maint in get_parent_zones")
            raise HTTPException(status_code=500, detail="Database pool unavailable")
        async with pool.acquire() as conn:
            logger.debug("Executing query: SELECT i_zn, x_nm_zn, i_typ_zn FROM zones ORDER BY i_typ_zn, x_nm_zn")
            zones = await conn.fetch(
                "SELECT i_zn, x_nm_zn, i_typ_zn FROM zones ORDER BY i_typ_zn, x_nm_zn"
            )
            logger.info(f"Fetched {len(zones)} parent zones")
            return {
                "zones": [
                    {
                        "zone_id": zone["i_zn"],
                        "name": zone["x_nm_zn"],
                        "level": zone["i_typ_zn"]
                    }
                    for zone in zones
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching parent zones: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/get_parent_zones_for_trigger_demo")
async def get_parent_zones_for_trigger_demo():
    """
    Fetch all zones with additional metadata for trigger demo purposes.

    This endpoint retrieves a list of all zones from the `zones` table, including their map ID and
    parent zone ID, sorted by zone type and name. It is designed for experimental or demonstration
    purposes in the ParcoRTLS system, particularly for testing trigger-related functionalities in the
    Zone Builder tool, where additional zone metadata (e.g., map associations) is required.

    Parameters:
        None

    Returns:
        dict: A JSON object with a single key "zones" containing a list of dictionaries. Each dictionary
              represents a zone with the following keys:
              - zone_id (int): The unique identifier of the zone (i_zn).
              - name (str): The name of the zone (x_nm_zn).
              - level (int): The zone type (i_typ_zn, e.g., 1 for campus).
              - i_map (int): The map ID associated with the zone (i_map).
              - parent_zone_id (int or None): The ID of the parent zone (i_pnt_zn), or None if top-level.

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/get_parent_zones_for_trigger_demo
        ```
        Response:
        ```json
        {
            "zones": [
                {
                    "zone_id": 1,
                    "name": "Main Campus",
                    "level": 1,
                    "i_map": 1,
                    "parent_zone_id": null
                },
                {
                    "zone_id": 2,
                    "name": "Building A",
                    "level": 2,
                    "i_map": 1,
                    "parent_zone_id": 1
                }
            ]
        }
        ```

    Use Case:
        - During a demonstration of trigger functionality, a developer needs to select zones to
          associate with triggers (e.g., entry/exit alerts). This endpoint provides comprehensive zone
          data, including map and hierarchy information, to facilitate testing trigger configurations.

    Hint:
        - Use this endpoint for trigger-related demos to ensure zones are correctly associated with
          maps. Cross-reference i_map with the /get_map_metadata endpoint for map details.
        - For campus-level checks, filter zones where level = 1 and parent_zone_id is null.

    Errors:
        - 500 (Internal Server Error): Raised if the database pool is unavailable or an unexpected
          error occurs during query execution. The error message includes details for debugging.
    """
    try:
        logger.debug("Starting get_parent_zones_for_trigger_demo")
        logger.debug("Attempting to get database pool for maint")
        pool = await get_async_db_pool("maint")
        if not pool:
            logger.error("Database pool unavailable for maint")
            raise HTTPException(status_code=500, detail="Database pool unavailable for maint")
        logger.debug("Successfully acquired database pool")
        async with pool.acquire() as conn:
            logger.debug("Acquired connection from pool")
            logger.debug("Executing query: SELECT i_zn, x_nm_zn, i_typ_zn, i_map, i_pnt_zn FROM zones ORDER BY i_typ_zn, x_nm_zn")
            zones = await conn.fetch(
                "SELECT i_zn, x_nm_zn, i_typ_zn, i_map, i_pnt_zn FROM zones ORDER BY i_typ_zn, x_nm_zn"
            )
            logger.info(f"Fetched {len(zones)} parent zones for trigger demo")
            return {
                "zones": [
                    {
                        "zone_id": zone["i_zn"],
                        "name": zone["x_nm_zn"],
                        "level": zone["i_typ_zn"],
                        "i_map": zone["i_map"],
                        "parent_zone_id": zone["i_pnt_zn"]
                    }
                    for zone in zones
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching parent zones for trigger demo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/test_db_connection")
async def test_db_connection():
    """
    Test the database connection to the `maint` schema.

    This endpoint performs a simple query to verify connectivity to the `maint` schema in the
    ParcoRTLS database. It is primarily used for debugging and ensuring the backend can communicate
    with the PostgreSQL database, which is critical for all Zone Builder operations.

    Parameters:
        None

    Returns:
        dict: A JSON object with the following keys:
              - status (str): Indicates the connection status ("success").
              - result (int): The result of the test query (typically 1).

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/test_db_connection
        ```
        Response:
        ```json
        {
            "status": "success",
            "result": 1
        }
        ```

    Use Case:
        - A system administrator troubleshooting connectivity issues between the FastAPI backend and
          the PostgreSQL database uses this endpoint to confirm that the database pool is operational
          before deploying new Zone Builder features.

    Hint:
        - Run this endpoint after server restarts or configuration changes to verify database
          connectivity.
        - If this endpoint fails, check the DB_CONFIG settings and ensure the PostgreSQL server is
          running at localhost:5432.

    Errors:
        - 500 (Internal Server Error): Raised if the database pool is unavailable or the test query
          fails. The error message includes details for debugging.
    """
    try:
        logger.debug("Testing database connection for maint")
        pool = await get_async_db_pool("maint")
        if not pool:
            logger.error("Database pool unavailable for maint in test_db_connection")
            raise HTTPException(status_code=500, detail="Database pool unavailable")
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            logger.info("Database connection test successful")
            return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error testing database connection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/get_zone_types")
async def get_zone_types():
    """
    Fetch all zone types from the ParcoRTLS database.

    This endpoint retrieves a list of zone types from the `tlkzonetypes` table in the `maint` schema.
    Zone types define the hierarchical levels of zones (e.g., campus, building, floor) in the
    ParcoRTLS system. The endpoint is used by the Zone Builder tool to populate a dropdown or list
    of zone types when creating or editing zones.

    Parameters:
        None

    Returns:
        list: A list of dictionaries, each representing a zone type with the following keys:
              - zone_level (int): The zone type ID (i_typ_zn, e.g., 1 for campus).
              - zone_name (str): The description of the zone type (x_dsc_zn).
              - api_endpoint (str): The endpoint to create a zone (hardcoded as "/create_zone").

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/get_zone_types
        ```
        Response:
        ```json
        [
            {"zone_level": 1, "zone_name": "Campus", "api_endpoint": "/create_zone"},
            {"zone_level": 2, "zone_name": "Building", "api_endpoint": "/create_zone"}
        ]
        ```

    Use Case:
        - When creating a new zone in the Zone Builder, a user needs to select the zone type (e.g.,
          campus or floor). This endpoint provides the available zone types to ensure the zone is
          correctly categorized in the hierarchy.

    Hint:
        - For campus-level zones, select zone_level = 1. This can be used to check if a tag is on a
          campus by associating devices with zones of this type.
        - The api_endpoint field is currently hardcoded. Future enhancements could make it dynamic
          based on zone type.

    Errors:
        - 500 (Internal Server Error): Raised if there is a database connection issue or an unexpected
          error occurs during query execution.
    """
    try:
        zone_types = await execute_raw_query(
            "maint",
            "SELECT i_typ_zn, x_dsc_zn FROM tlkzonetypes ORDER BY i_typ_zn"
        )
        logger.info(f"Fetched {len(zone_types)} zone types")
        return [{"zone_level": z["i_typ_zn"], "zone_name": z["x_dsc_zn"], "api_endpoint": "/create_zone"} for z in zone_types]
    except Exception as e:
        logger.error(f"Error retrieving zone types: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving zone types: {str(e)}")

@router.get("/get_zone_vertices/{zone_id}")
async def get_zone_vertices(zone_id: int):
    """
    Fetch vertices for a specific zone, excluding child zones and trigger regions.

    This endpoint retrieves the vertices defining the boundary of a specific zone from the `vertices`
    and `regions` tables in the `maint` schema. It excludes vertices from child zones and trigger-related
    regions, ensuring only the target zone's boundary is returned. This is used in the Zone Builder
    tool to display or edit a zone's shape in the ParcoRTLS system.

    Parameters:
        zone_id (int, required, path): The unique identifier of the zone (i_zn) to fetch vertices for.

    Returns:
        dict: A JSON object with a single key "vertices" containing a list of dictionaries. Each dictionary
              represents a vertex with the following keys:
              - i_vtx (int): The vertex ID.
              - i_rgn (int): The region ID associated with the vertex.
              - n_x (float): The x-coordinate.
              - n_y (float): The y-coordinate.
              - n_z (float): The z-coordinate (typically 0 for 2D zones).
              - n_ord (int): The order of the vertex in the boundary.

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/get_zone_vertices/1
        ```
        Response:
        ```json
        {
            "vertices": [
                {"i_vtx": 1, "i_rgn": 1, "n_x": 0.0, "n_y": 0.0, "n_z": 0.0, "n_ord": 1},
                {"i_vtx": 2, "i_rgn": 1, "n_x": 10.0, "n_y": 0.0, "n_z": 0.0, "n_ord": 2}
            ]
        }
        ```

    Use Case:
        - A user editing a zone's boundary in the Zone Builder needs to visualize the current shape.
          This endpoint provides the vertex coordinates to render the zone's polygon on the map.

    Hint:
        - For campus-level zones (i_typ_zn = 1), use this endpoint to check if a tag's coordinates
          (from positionhistory) fall within the zone's boundary using a point-in-polygon algorithm.
        - If no vertices are returned, the zone may not have a defined boundary yet.

    Errors:
        - 500 (Internal Server Error): Raised if there is a database connection issue or an unexpected
          error occurs during query execution.
        - Returns {"vertices": []} if no vertices are found for the zone_id (not an error).
    """
    try:
        vertices_data = await execute_raw_query(
            "maint",
            """
            SELECT v.i_vtx, v.i_rgn, v.n_x, v.n_y, v.n_z, v.n_ord
            FROM vertices v
            JOIN regions r ON v.i_rgn = r.i_rgn
            WHERE r.i_zn = $1 AND r.i_trg IS NULL
            ORDER BY v.n_ord
            """,
            zone_id
        )
        if not vertices_data:
            logger.warning(f"No vertices found for zone_id={zone_id}")
            return {"vertices": []}
        logger.info(f"Retrieved {len(vertices_data)} vertices for zone_id={zone_id}")
        return {"vertices": vertices_data}
    except Exception as e:
        logger.error(f"Error fetching vertices for zone_id={zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/internal-metadata", include_in_schema=False)
async def get_internal_metadata(format: str = None):
    """
    Extract concealed text from the metadata of a default PNG file (hidden endpoint).

    This internal endpoint retrieves concealed text embedded in the metadata of the
    `static/default_grid_box.png` file. It is not exposed in the Swagger UI and is intended for
    internal debugging or administrative purposes in the ParcoRTLS system. The response can be
    formatted as JSON or HTML based on the `format` query parameter.

    Parameters:
        format (str, optional, query): Specifies the response format. Set to "html" for an HTML page,
                                      otherwise returns JSON. Defaults to None (JSON).

    Returns:
        - If format="html": An HTML page (Response with media_type="text/html") containing the concealed
          text in a formatted <pre> tag.
        - Otherwise: A JSON object with a single key:
          - internal_metadata (str): The concealed text extracted from the PNG metadata.

    Example:
        ```bash
        curl -X GET "http://192.168.210.226:8000/zonebuilder/internal-metadata?format=html"
        ```
        Response (HTML):
        ```html
        <html>
          <head>
            <title>Internal Metadata</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              pre { background-color: #f4f4f4; padding: 1em; border: 1px solid #ccc; }
            </style>
          </head>
          <body>
            <h1>Internal Metadata</h1>
            <pre>Hidden text here</pre>
          </body>
        </html>
        ```

        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/internal-metadata
        ```
        Response (JSON):
        ```json
        {"internal_metadata": "Hidden text here"}
        ```

    Use Case:
        - A developer debugging the Zone Builder tool needs to access hidden configuration data or
          debug information embedded in the default PNG file used for map rendering.

    Hint:
        - Ensure the `static/default_grid_box.png` file exists in the correct directory and contains
          the expected metadata.
        - This endpoint is hidden from Swagger UI (include_in_schema=False) to prevent public exposure.

    Errors:
        - 404 (Not Found): Raised if the concealed metadata is not found in the PNG file.
        - 500 (Internal Server Error): Raised if there is an issue opening the PNG file or an unexpected
          error occurs.
    """
    try:
        with Image.open("static/default_grid_box.png") as img:
            concealed_text = img.text.get("concealed_text")
            if not concealed_text:
                raise HTTPException(status_code=404, detail="Concealed metadata not found")
            
            if format == "html":
                html_output = f"""
                <html>
                  <head>
                    <title>Internal Metadata</title>
                    <style>
                      body {{ font-family: Arial, sans-serif; margin: 20px; }}
                      pre {{ background-color: #f4f4f4; padding: 1em; border: 1px solid #ccc; }}
                    </style>
                  </head>
                  <body>
                    <h1>Internal Metadata</h1>
                    <pre>{concealed_text}</pre>
                  </body>
                </html>
                """
                return Response(content=html_output, media_type="text/html")
            else:
                return {"internal_metadata": concealed_text}
    except Exception as e:
        logger.error(f"Error retrieving internal metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_zone")
async def create_zone(data: dict):
    """
    Create a new zone with associated region and vertices.

    This endpoint creates a new zone in the `zones` table, an associated region in the `regions` table,
    and vertices in the `vertices` table in the `maint` schema. It is a core function of the Zone Builder
    tool, allowing users to define new zones (e.g., rooms, floors, campuses) with specific boundaries
    and hierarchical relationships in the ParcoRTLS system.

    Parameters:
        data (dict, required, body): A JSON object containing the following keys:
            - zone_name (str, required): The name of the zone (x_nm_zn).
            - map_id (int, required): The ID of the associated map (i_map).
            - zone_level (int, required): The zone type (i_typ_zn, e.g., 1 for campus).
            - parent_zone_id (int, optional): The ID of the parent zone (i_pnt_zn), or null for top-level zones.
            - vertices (list, optional): A list of dictionaries, each with:
                - n_x (float): The x-coordinate.
                - n_y (float): The y-coordinate.
                - n_z (float): The z-coordinate (typically 0 for 2D zones).

    Returns:
        dict: A JSON object with the following keys:
              - zone_id (int): The ID of the newly created zone (i_zn).
              - message (str): A success message ("Zone created successfully").

    Example:
        ```bash
        curl -X POST http://192.168.210.226:8000/zonebuilder/create_zone \
        -H "Content-Type: application/json" \
        -d '{
            "zone_name": "Room 101",
            "map_id": 1,
            "zone_level": 4,
            "parent_zone_id": 2,
            "vertices": [
                {"n_x": 0.0, "n_y": 0.0, "n_z": 0.0},
                {"n_x": 10.0, "n_y": 0.0, "n_z": 0.0},
                {"n_x": 10.0, "n_y": 10.0, "n_z": 0.0}
            ]
        }'
        ```
        Response:
        ```json
        {
            "zone_id": 3,
            "message": "Zone created successfully"
        }
        ```

    Use Case:
        - A facility manager uses the Zone Builder to create a new room zone within a building. They
          specify the room's name, associate it with a floorplan (map_id), set its type as a room
          (zone_level=4), link it to a parent building (parent_zone_id), and define its boundary
          with vertices.

    Hint:
        - For campus-level zones (zone_level=1), set parent_zone_id to null to indicate a top-level
          zone. This is useful for checking if tags are within a campus boundary.
        - Validate vertices against the map's bounds (from /get_map_metadata) before submission to
          ensure they are within the map's coordinate system.

    Errors:
        - 400 (Bad Request): Raised if required fields (zone_name, map_id, zone_level) are missing or
          if map_id or zone_level are not integers.
        - 500 (Internal Server Error): Raised if zone creation fails due to database issues or unexpected
          errors.
    """
    try:
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

        logger.info(f"Creating zone with data: {data}")

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
    """
    Fetch the binary image data for a specific map.

    This endpoint retrieves the binary image data and format for a map identified by its map_id from
    the `maps` table in the `maint` schema. It returns the image as a response, which is used by the
    Zone Builder tool to display the map in the React frontend for zone creation or editing.

    Parameters:
        map_id (int, required, path): The unique identifier of the map (i_map) to fetch.

    Returns:
        Response: A FastAPI Response object containing the binary image data with the appropriate
                  media type (e.g., image/png, image/jpeg) based on the map's format (x_format).

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/get_map/1 --output map.png
        ```
        Response: Binary image data (saved as map.png in the example).

    Use Case:
        - When a user selects a map in the Zone Builder to create or edit a zone, this endpoint
          provides the actual image data to render the map in the UI, allowing the user to visualize
          the floorplan or layout.

    Hint:
        - Use this endpoint in conjunction with /get_map_data or /get_map_metadata to get the map's
          bounds for proper scaling and alignment in the frontend.
        - Ensure CORS is configured to allow the React frontend (http://192.168.210.226:3000) to
          access the image.

    Errors:
        - 404 (Not Found): Raised if no map is found for the provided map_id.
        - 500 (Internal Server Error): Raised if there is a database connection issue or an unexpected
          error occurs during query execution.
    """
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT img_data, x_format FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No map found for map_id={map_id}")
        logger.info(f"Fetched map image for map_id={map_id}")
        return Response(content=map_data[0]["img_data"], media_type=f"image/{map_data[0]['x_format'].lower()}")
    except Exception as e:
        logger.error(f"Error retrieving map {map_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving map: {str(e)}")

@router.post("/api/add_device_type")
async def add_device_type(data: dict):
    """
    Add a new device type to the ParcoRTLS database.

    This endpoint inserts a new device type into the `tlkdevicetypes` table in the `maint` schema.
    Device types categorize devices (e.g., tags, anchors) in the ParcoRTLS system, and this endpoint
    is used in the Zone Builder to define new categories for devices associated with zones.

    Parameters:
        data (dict, required, body): A JSON object with the following key:
            - description (str, required): The description of the device type (x_dsc_dev, max 50 characters).

    Returns:
        dict: A JSON object with the following key:
              - type_id (int): The ID of the newly created device type (i_typ_dev).

    Example:
        ```bash
        curl -X POST http://192.168.210.226:8000/zonebuilder/api/add_device_type \
        -H "Content-Type: application/json" \
        -d '{"description": "UWB Tag"}'
        ```
        Response:
        ```json
        {"type_id": 1}
        ```

    Use Case:
        - An administrator configuring the ParcoRTLS system adds a new device type (e.g., "UWB Tag")
          to categorize tracking devices used in zones, ensuring accurate device management.

    Hint:
        - Validate the description length (≤50 characters) on the frontend to avoid 400 errors.
        - After adding a device type, use /api/get_all_devices to verify devices associated with the
          new type.

    Errors:
        - 400 (Bad Request): Raised if the description is missing or exceeds 50 characters.
        - 500 (Internal Server Error): Raised if the insertion fails due to database issues or
          unexpected errors.
    """
    try:
        description = data.get("description")
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        if len(description) > 50:
            raise HTTPException(status_code=400, detail="Description must be 50 characters or less")
        
        result = await execute_raw_query(
            "maint",
            "INSERT INTO tlkdevicetypes (x_dsc_dev) VALUES ($1) RETURNING i_typ_dev",
            description
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to insert device type")
        
        type_id = result[0]["i_typ_dev"]
        logger.info(f"Added device type: {description} with ID {type_id}")
        return {"type_id": type_id}
    except Exception as e:
        logger.error(f"Error adding device type: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/api/get_all_devices")
async def get_all_devices():
    """
    Fetch all devices with their associated zone IDs from the ParcoRTLS database.

    This endpoint retrieves a comprehensive list of all devices stored in the `devices` table of the
    `maint` schema, including their associated zone IDs. It primarily uses the `usp_device_select_all`
    stored procedure to fetch device data, with a fallback to a raw SQL query if the stored procedure
    fails. This endpoint is integral to the Zone Builder tool, enabling users to view and manage devices
    (e.g., UWB tags, anchors) within specific zones for real-time location tracking in the ParcoRTLS system.

    Parameters:
        None

    Returns:
        list: A list of dictionaries, each representing a device with the following keys:
              - x_id_dev (str): The unique identifier of the device (x_id_dev).
              - i_typ_dev (int): The device type ID (i_typ_dev, from tlkdevicetypes).
              - x_nm_dev (str or None): The name of the device (x_nm_dev).
              - d_srv_bgn (str or None): The start date of service in ISO format (d_srv_bgn).
              - d_srv_end (str or None): The end date of service in ISO format (d_srv_end).
              - n_moe_x (float or None): The x-coordinate margin of error (n_moe_x).
              - n_moe_y (float or None): The y-coordinate margin of error (n_moe_y).
              - n_moe_z (float or None): The z-coordinate margin of error (n_moe_z).
              - f_log (bool): Flag indicating whether logging is enabled (f_log).
              - zone_id (int or None): The ID of the associated zone (zone_id).

    Example:
        ```bash
        curl -X GET http://192.168.210.226:8000/zonebuilder/api/get_all_devices
        ```
        Response:
        ```json
        [
            {
                "x_id_dev": "TAG001",
                "i_typ_dev": 1,
                "x_nm_dev": "Tag 1",
                "d_srv_bgn": "2025-04-01T00:00:00",
                "d_srv_end": null,
                "n_moe_x": 10.0,
                "n_moe_y": 20.0,
                "n_moe_z": 0.0,
                "f_log": false,
                "zone_id": 1
            },
            {
                "x_id_dev": "TAG002",
                "i_typ_dev": 1,
                "x_nm_dev": "Tag 2",
                "d_srv_bgn": "2025-04-02T00:00:00",
                "d_srv_end": null,
                "n_moe_x": 15.0,
                "n_moe_y": 25.0,
                "n_moe_z": 0.0,
                "f_log": false,
                "zone_id": 2
            }
        ]
        ```

    Use Case:
        - A facility manager uses the Zone Builder tool to review all devices deployed across a campus
          (zone_id with i_typ_zn=1) to ensure each UWB tag is correctly assigned to its respective zone
          for accurate tracking. This endpoint provides a complete inventory of devices for monitoring
          and maintenance purposes.

    Hint:
        - To check if a tag is on a campus, filter devices where `zone_id` corresponds to a zone with
          `i_typ_zn=1` in the `zones` table. Combine with `/get_zone_vertices/{zone_id}` to verify if
          the tag's coordinates (n_moe_x, n_moe_y) are within the campus boundary.
        - The fallback mechanism ensures robustness. If the stored procedure fails, the raw query
          retrieves data directly from the `devices` table, but it may lack additional processing
          provided by `usp_device_select_all`.

    Errors:
        - 500 (Internal Server Error): Raised if both the stored procedure and the fallback raw query
          fail due to database connectivity issues or other unexpected errors. The error message
          includes details for debugging.
    """
    try:
        devices_data = await execute_raw_query(
            "maint",
            "SELECT * FROM usp_device_select_all()"
        )
        logger.info(f"Raw devices data: {devices_data}")
        response = [
            {
                "x_id_dev": d["x_id_dev"],
                "i_typ_dev": d["i_typ_dev"],
                "x_nm_dev": d["x_nm_dev"],
                "d_srv_bgn": d["d_srv_bgn"].isoformat() if d["d_srv_bgn"] else None,
                "d_srv_end": d["d_srv_end"].isoformat() if d["d_srv_end"] else None,
                "n_moe_x": float(d["n_moe_x"]) if d["n_moe_x"] is not None else None,
                "n_moe_y": float(d["n_moe_y"]) if d["n_moe_y"] is not None else None,
                "n_moe_z": float(d["n_moe_z"]) if d["n_moe_z"] is not None else None,
                "f_log": d["f_log"],
                "zone_id": d.get("zone_id", None)
            } for d in devices_data
        ]
        logger.info(f"Fetched {len(devices_data)} devices: {[d['x_id_dev'] for d in devices_data]}")
        logger.info(f"Response devices: {response}")
        return response
    except Exception as e:
        logger.error(f"Error retrieving devices: {e}")
        # Fallback to raw query if the function fails
        logger.info("Falling back to raw SELECT * FROM devices")
        devices_data = await execute_raw_query(
            "maint",
            "SELECT * FROM devices"
        )
        response = [
            {
                "x_id_dev": d["x_id_dev"],
                "i_typ_dev": d["i_typ_dev"],
                "x_nm_dev": d["x_nm_dev"],
                "d_srv_bgn": d["d_srv_bgn"].isoformat() if d["d_srv_bgn"] else None,
                "d_srv_end": d["d_srv_end"].isoformat() if d["d_srv_end"] else None,
                "n_moe_x": float(d["n_moe_x"]) if d["n_moe_x"] is not None else None,
                "n_moe_y": float(d["n_moe_y"]) if d["n_moe_y"] is not None else None,
                "n_moe_z": float(d["n_moe_z"]) if d["n_moe_z"] is not None else None,
                "f_log": d["f_log"],
                "zone_id": d.get("zone_id", None)
            } for d in devices_data
        ]
        logger.info(f"Fallback response devices: {response}")
        return response

@router.post("/api/add_device")
async def add_device(
    device_id: str = Form(...),
    device_type: int = Form(...),
    device_name: str = Form(None),
    n_moe_x: float = Form(None),
    n_moe_y: float = Form(None),
    n_moe_z: float = Form(0),
    zone_id: int = Form(...)
):
    """
    Add a new device with an associated zone ID to the ParcoRTLS database.

    This endpoint inserts a new device into the `devices` table in the `maint` schema, linking it to a
    specific zone for real-time location tracking. It is a critical function in the Zone Builder tool,
    enabling the registration of new devices such as UWB tags or anchors within the ParcoRTLS system.
    The device is assigned a zone ID to associate it with a specific location (e.g., a room or campus).

    Parameters:
        device_id (str, required, form): The unique identifier for the device (x_id_dev).
        device_type (int, required, form): The device type ID (i_typ_dev), referencing a type in the
                                          `tlkdevicetypes` table.
        device_name (str, optional, form): The human-readable name of the device (x_nm_dev).
        n_moe_x (float, optional, form): The x-coordinate margin of error (n_moe_x), representing the
                                         device's initial position.
        n_moe_y (float, optional, form): The y-coordinate margin of error (n_moe_y).
        n_moe_z (float, optional, form): The z-coordinate margin of error (n_moe_z), defaults to 0 for
                                         2D tracking.
        zone_id (int, required, form): The ID of the zone (zone_id) to associate the device with,
                                       referencing the `zones` table.

    Returns:
        dict: A JSON object with the following keys:
              - x_id_dev (str): The ID of the newly created device.
              - message (str): A success message ("Device added successfully").

    Example:
        ```bash
        curl -X POST http://192.168.210.226:8000/zonebuilder/api/add_device \
        -F "device_id=TAG001" \
        -F "device_type=1" \
        -F "device_name=Tag 1" \
        -F "n_moe_x=10.0" \
        -F "n_moe_y=20.0" \
        -F "n_moe_z=0.0" \
        -F "zone_id=1"
        ```
        Response:
        ```json
        {
            "x_id_dev": "TAG001",
            "message": "Device added successfully"
        }
        ```

    Use Case:
        - A technician deploys a new UWB tag in a hospital room (zone_id corresponding to a room zone).
          This endpoint registers the tag in the ParcoRTLS system, associating it with the room for
          tracking patients or equipment within that space.

    Hint:
        - Before submitting, verify that the `zone_id` exists in the `zones` table and that the
          `device_type` is valid in the `tlkdevicetypes` table to avoid database errors.
        - For campus-level tracking, use a `zone_id` corresponding to a zone with `i_typ_zn=1` to
          associate devices with a campus, enabling broad location checks.

    Errors:
        - 500 (Internal Server Error): Raised if the insertion fails due to database connectivity issues,
          duplicate `device_id`, invalid `zone_id`, or other unexpected errors. The error message
          includes details for debugging.
    """
    try:
        logger.info(f"Received add_device request: device_id={device_id}, device_type={device_type}, device_name={device_name}, n_moe_x={n_moe_x}, n_moe_y={n_moe_y}, n_moe_z={n_moe_z}, zone_id={zone_id}, type(zone_id)={type(zone_id)}")
        
        # Define the INSERT query with all relevant columns, including zone_id
        query = """
            INSERT INTO devices (x_id_dev, i_typ_dev, x_nm_dev, zone_id, f_log, d_srv_bgn, n_moe_x, n_moe_y, n_moe_z)
            VALUES ($1, $2, $3, $4, $5, NOW(), $6, $7, $8)
            RETURNING x_id_dev, zone_id;
        """
        params = (device_id, device_type, device_name, zone_id, False, n_moe_x, n_moe_y, n_moe_z)
        
        # Execute the query using execute_raw_query
        logger.info(f"Executing query: {query} with params: {params}")
        result = await execute_raw_query("maint", query, *params)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to add device")
        
        logger.info(f"Inserted device: {device_id}, returned zone_id: {result[0]['zone_id']}")
        return {"x_id_dev": result[0]["x_id_dev"], "message": "Device added successfully"}
    
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding device: {str(e)}")

@router.put("/api/edit_device/{device_id}")
async def edit_device(
    device_id: str,
    device_name: str = Form(None),
    n_moe_x: float = Form(None),
    n_moe_y: float = Form(None),
    n_moe_z: float = Form(None),
    zone_id: int = Form(...)
):
    """
    Edit an existing device's details, including its zone association, in the ParcoRTLS database.

    This endpoint updates the information of a device in the `devices` table of the `maint` schema,
    allowing modifications to its name, position coordinates (margin of error), and associated zone ID.
    It uses a direct `psycopg2` connection for the update operation, which is part of the Zone Builder
    tool's functionality to manage device configurations in the ParcoRTLS system.

    Parameters:
        device_id (str, required, path): The unique identifier of the device to edit (x_id_dev).
        device_name (str, optional, form): The updated human-readable name of the device (x_nm_dev).
        n_moe_x (float, optional, form): The updated x-coordinate margin of error (n_moe_x).
        n_moe_y (float, optional, form): The updated y-coordinate margin of error (n_moe_y).
        n_moe_z (float, optional, form): The updated z-coordinate margin of error (n_moe_z).
        zone_id (int, required, form): The updated ID of the associated zone (zone_id), referencing
                                       the `zones` table.

    Returns:
        dict: A JSON object with the following keys:
              - x_id_dev (str): The ID of the updated device.
              - message (str): A success message ("Device updated successfully").

    Example:
        ```bash
        curl -X PUT http://192.168.210.226:8000/zonebuilder/api/edit_device/TAG001 \
        -F "device_name=Updated Tag 1" \
        -F "n_moe_x=15.0" \
        -F "n_moe_y=25.0" \
        -F "n_moe_z=0.0" \
        -F "zone_id=2"
        ```
        Response:
        ```json
        {
            "x_id_dev": "TAG001",
            "message": "Device updated successfully"
        }
        ```

    Use Case:
        - A technician relocates a UWB tag from one room to another within a building (different zone_id).
          This endpoint updates the tag's zone association and position coordinates to reflect its new
          location, ensuring accurate tracking in the ParcoRTLS system.

    Hint:
        - Before updating, verify that the `zone_id` exists in the `zones` table to prevent database
          errors. Use `/get_parent_zones` to retrieve valid zone IDs.
        - For campus-level updates, ensure the new `zone_id` corresponds to a zone with `i_typ_zn=1`
          if the device is being reassigned to a campus for broader tracking purposes.

    Errors:
        - 404 (Not Found): Raised if the `device_id` does not exist in the `devices` table.
        - 500 (Internal Server Error): Raised if the update fails due to database connectivity issues,
          invalid `zone_id`, or other unexpected errors. The error message includes details for debugging.
    """
    try:
        logger.info(f"Received edit_device request: device_id={device_id}, device_name={device_name}, n_moe_x={n_moe_x}, n_moe_y={n_moe_y}, n_moe_z={n_moe_z}, zone_id={zone_id}, type(zone_id)={type(zone_id)}")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            UPDATE devices
            SET x_nm_dev = %s, n_moe_x = %s, n_moe_y = %s, n_moe_z = %s, zone_id = %s
            WHERE x_id_dev = %s
            RETURNING x_id_dev, zone_id;
        """
        params = (device_name, n_moe_x, n_moe_y, n_moe_z, zone_id, device_id)
        logger.info(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if not result:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        logger.info(f"Updated device: {device_id}, result: {result}")
        logger.info(f"Returned zone_id: {result['zone_id']}")
        return {"x_id_dev": result["x_id_dev"], "message": "Device updated successfully"}
    except Exception as e:
        logger.error(f"Error editing device: {e}")
        if 'conn' in locals():
            conn.close()
        raise HTTPException(status_code=500, detail=f"Error editing device: {str(e)}")

@router.delete("/api/delete_device/{device_id}")
async def delete_device(device_id: str):
    """
    Delete a device and its associated assignments from the ParcoRTLS database.

    This endpoint removes a device from the `devices` table and its related assignments from the
    `deviceassmts` table in the `maint` schema. It is used in the Zone Builder tool to decommission
    devices (e.g., UWB tags or anchors) that are no longer in use, ensuring they are removed from the
    ParcoRTLS system's tracking data.

    Parameters:
        device_id (str, required, path): The unique identifier of the device to delete (x_id_dev).

    Returns:
        dict: A JSON object with the following key:
              - message (str): A success message indicating the device was deleted
                               ("Device {device_id} deleted successfully").

    Example:
        ```bash
        curl -X DELETE http://192.168.210.226:8000/zonebuilder/api/delete_device/TAG001
        ```
        Response:
        ```json
        {
            "message": "Device TAG001 deleted successfully"
        }
        ```

    Use Case:
        - A facility manager identifies a faulty UWB tag that needs to be removed from the system. This
          endpoint deletes the tag and its assignments, ensuring it no longer appears in tracking reports
          or zone associations.

    Hint:
        - Before deletion, use `/api/get_all_devices` to confirm the device's details and its current
          zone association to avoid accidental removal.
        - For campus-level cleanup, target devices associated with zones where `i_typ_zn=1` to remove
          all tags from a specific campus.

    Errors:
        - 404 (Not Found): Raised if the `device_id` does not exist in the `devices` table.
        - 500 (Internal Server Error): Raised if the deletion fails due to database connectivity issues
          or other unexpected errors. The error message includes details for debugging.
    """
    try:
        logger.info(f"Received delete_device request for device_id={device_id}")
        await execute_raw_query(
            "maint",
            "DELETE FROM deviceassmts WHERE x_id_dev = $1",
            device_id
        )
        
        result = await execute_raw_query(
            "maint",
            "DELETE FROM devices WHERE x_id_dev = $1 RETURNING x_id_dev",
            device_id
        )
        if not result:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        logger.info(f"Deleted device: {device_id}")
        return {"message": f"Device {device_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting device: {str(e)}")

@router.post("/validate-support-access", include_in_schema=False)
async def validate_support_access(payload: dict = Body(...)):
    """
    Validate support access with a secret password (hidden endpoint).

    This internal endpoint verifies a provided password against a hardcoded secret password to grant
    support access. It is not exposed in the Swagger UI and is intended for administrative or support
    purposes within the ParcoRTLS system, such as accessing restricted debugging features or
    configurations in the Zone Builder tool.

    Parameters:
        payload (dict, required, body): A JSON object with the following key:
            - password (str, required): The password to validate against the secret password.

    Returns:
        dict: A JSON object with the following key:
              - status (str): Indicates successful validation ("ok") if the password is correct.

    Example:
        ```bash
        curl -X POST http://192.168.210.226:8000/zonebuilder/validate-support-access \
        -H "Content-Type: application/json" \
        -d '{"password": "gene"}'
        ```
        Response:
        ```json
        {
            "status": "ok"
        }
        ```

    Use Case:
        - A support engineer needs to access restricted debugging tools or configuration settings in the
          Zone Builder to troubleshoot issues with zone or device management. This endpoint validates
          their credentials to unlock these features.

    Hint:
        - The secret password is currently hardcoded as "gene". For production environments, consider
          replacing it with a secure, environment-variable-based secret to enhance security.
        - Since this endpoint is hidden (include_in_schema=False), it is not visible in the Swagger UI,
          reducing the risk of unauthorized access. Ensure only authorized personnel know the endpoint URL.

    Errors:
        - 403 (Forbidden): Raised if the provided password does not match the secret password.
    """
    secret_password = "gene"
    if payload.get("password") == secret_password:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=403, detail="Invalid password")