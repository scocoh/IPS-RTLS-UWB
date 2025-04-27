"""
/home/parcoadmin/parco_fastapi/app/routes/zoneviewer_routes.py
Version: 0.1.18 (Enhanced endpoint documentation)
Zone Viewer & Editor endpoints for ParcoRTLS FastAPI application.
# VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/zoneviewer_routes.py 0P.10B.03
# --- CHANGED: Bumped version from 0P.10B.02 to 0P.10B.03
# --- ADDED: Enhanced docstrings for all endpoints with detailed descriptions, parameters, return values, examples, use cases, and error handling
# --- PREVIOUS: 0P.10B.02 (Added /get_maps_with_zone_types endpoint)
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
from database.db import execute_raw_query
import logging
from sqlalchemy import create_engine, text
from contextlib import asynccontextmanager
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)

# Ensure logging captures all levels
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)

# Database connection for transaction support
DATABASE_URL = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint"
engine = create_engine(DATABASE_URL)

class AddVertexRequest(BaseModel):
    zone_id: int
    x: float
    y: float
    z: float = 0.0
    order: float

@asynccontextmanager
async def get_db_connection():
    """Provide a transactional scope around a series of operations."""
    connection = engine.connect()
    transaction = connection.begin()
    try:
        yield connection
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        raise e
    finally:
        connection.close()

@router.get("/get_campus_zones")
async def get_campus_zones():
    """
    Retrieve all campus zones with their hierarchical structure.

    **Description**:
    This endpoint fetches all zones from the ParcoRTLS system, organized hierarchically with campuses (zone_type=1)
    at the root and their child zones nested accordingly. It is used in the Zone Viewer to display the campus
    hierarchy for navigation and management. The response includes zone details like ID, name, type, parent zone,
    and map ID, with child zones nested under their parents.

    **Parameters**:
    - None

    **Returns**:
    - JSON object with a single key `campuses`, containing a list of campus objects. Each campus object has:
      - `zone_id` (int): Unique identifier of the zone.
      - `zone_name` (str): Name of the zone.
      - `zone_type` (int): Type of zone (1 for campus, 2 for building, etc.).
      - `parent_zone_id` (int or null): ID of the parent zone, null for campuses.
      - `map_id` (int or null): ID of the associated map.
      - `children` (list): List of child zone objects with the same structure.

    **Example Usage**:
    ```bash
    curl -X GET "http://192.168.210.226:8000/zoneviewer/get_campus_zones" -H "accept: application/json"
    ```
    Response:
    ```json
    {
      "campuses": [
        {
          "zone_id": 1,
          "zone_name": "Main Campus",
          "zone_type": 1,
          "parent_zone_id": null,
          "map_id": 101,
          "children": [
            {
              "zone_id": 2,
              "zone_name": "Building A",
              "zone_type": 2,
              "parent_zone_id": 1,
              "map_id": 102,
              "children": []
            }
          ]
        }
      ]
    }
    ```

    **Use Case**:
    - **Scenario**: A facility manager needs to view all campuses and their buildings in the ParcoRTLS Zone Viewer.
    - **Action**: The frontend React app calls this endpoint to populate the zone navigation tree, allowing the manager
      to select a campus and drill down to specific buildings or floors.
    - **Outcome**: The hierarchical structure enables intuitive navigation and management of zones.

    **Errors**:
    - **404 Not Found**: Raised if no zones are found in the database (`HTTPException`, detail="No zones found").
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - This endpoint is ideal for initializing the Zone Viewer UI. To check if a tag is within a campus (e.g., for Zone L1),
      combine this with vertex data from `/get_vertices_for_campus/{campus_id}` to perform spatial queries.
    """
    try:
        zones_data = await execute_raw_query(
            "maint",
            """
            SELECT z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn, z.i_map
            FROM zones z
            ORDER BY z.i_pnt_zn NULLS FIRST, z.i_zn;
            """
        )
        if not zones_data:
            logger.warning("No zones found")
            raise HTTPException(status_code=404, detail="No zones found")

        zone_map = {z["i_zn"]: {
            "zone_id": z["i_zn"],
            "zone_name": z["x_nm_zn"],
            "zone_type": z["i_typ_zn"],
            "parent_zone_id": z["i_pnt_zn"],
            "map_id": z["i_map"],
            "children": []
        } for z in zones_data}

        campuses = []
        for zone_id, zone_data in zone_map.items():
            if zone_data["zone_type"] == 1:
                campuses.append(zone_data)
            elif zone_data["parent_zone_id"] in zone_map:
                zone_map[zone_data["parent_zone_id"]]["children"].append(zone_data)

        logger.info(f"Retrieved {len(campuses)} campuses with hierarchy")
        return {"campuses": campuses}
    except Exception as e:
        logger.error(f"Error fetching campus zones: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_map/{map_id}")
async def get_map(map_id: int):
    """
    Retrieve the image data for a specific map.

    **Description**:
    This endpoint fetches the binary image data (e.g., PNG, JPEG) for a map identified by `map_id`. It is used in
    the Zone Viewer to display map images as backgrounds for zones, enabling visualization of spatial layouts in
    the ParcoRTLS system.

    **Parameters**:
    - `map_id` (int, path parameter, required): The unique identifier of the map to retrieve.

    **Returns**:
    - Binary response containing the map image data, with the appropriate `Content-Type` header
      (e.g., `image/png`, `image/jpeg`) based on the map's format stored in the database.

    **Example Usage**:
    ```bash
    curl -X GET "http://192.168.210.226:8000/zoneviewer/get_map/101" -o map101.png
    ```
    Response: Binary image data (saved as `map101.png` in the example).

    **Use Case**:
    - **Scenario**: A user selects a building in the Zone Viewer to view its floor plan.
    - **Action**: The React frontend requests the map image using this endpoint and renders it as a background
      for zone polygons.
    - **Outcome**: The map image provides spatial context for zones and tracked entities.

    **Errors**:
    - **404 Not Found**: Raised if no map is found for the given `map_id` (`HTTPException`, detail="No map found for map_id={map_id}").
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - Ensure the frontend handles different image formats (PNG, JPEG) based on the `Content-Type` header.
    - Combine with `/get_map_metadata/{map_id}` to get bounds for proper scaling in the UI.
    """
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
        logger.error(f"Error retrieving map {map_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_map_metadata/{map_id}")
async def get_map_metadata(map_id: int):
    """
    Retrieve metadata (bounds) for a specific map.

    **Description**:
    This endpoint fetches the spatial bounds (min_x, min_y, max_x, max_y) of a map, which define its coordinate
    system in the ParcoRTLS system. The metadata is used to scale and align map images and zone vertices in the
    Zone Viewer UI.

    **Parameters**:
    - `map_id` (int, path parameter, required): The unique identifier of the map.

    **Returns**:
    - JSON object with the following keys:
      - `min_x` (float): Minimum X coordinate of the map.
      - `min_y` (float): Minimum Y coordinate of the map.
      - `max_x` (float): Maximum X coordinate of the map.
      - `max_y` (float): Maximum Y coordinate of the map.

    **Example Usage**:
    ```bash
    curl -X GET "http://192.168.210.226:8000/zoneviewer/get_map_metadata/101" -H "accept: application/json"
    ```
    Response:
    ```json
    {
      "min_x": 0.0,
      "min_y": 0.0,
      "max_x": 100.0,
      "max_y": 50.0
    }
    ```

    **Use Case**:
    - **Scenario**: A developer is rendering a map in the Zone Viewer and needs to align zone polygons with the map image.
    - **Action**: The frontend calls this endpoint to get the map’s bounds and uses them to scale the canvas or SVG.
    - **Outcome**: Accurate alignment of zones and entities on the map.

    **Errors**:
    - **404 Not Found**: Raised if no metadata is found for the given `map_id` (`HTTPException`, detail="No metadata found for map_id={map_id}").
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - Use this endpoint alongside `/get_map/{map_id}` to ensure proper rendering of maps in the UI.
    - The bounds are critical for spatial calculations, such as determining if a tag’s coordinates are within a zone.
    """
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            raise HTTPException(status_code=404, detail=f"No metadata found for map_id={map_id}")
        data = map_data[0]
        return {
            "min_x": float(data["min_x"]),
            "min_y": float(data["min_y"]),
            "max_x": float(data["max_x"]),
            "max_y": float(data["max_y"])
        }
    except Exception as e:
        logger.error(f"Error retrieving map metadata for map_id={map_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_map_data/{map_id}")
async def get_map_data(map_id: int):
    """
    Retrieve map data including image URL and bounds for rendering.

    **Description**:
    This endpoint provides a convenient combination of a map’s image URL and its spatial bounds, formatted for
    direct use in the ParcoRTLS Zone Viewer frontend. It is used to render maps with proper scaling and alignment
    in the React app.

    **Parameters**:
    - `map_id` (int, path parameter, required): The unique identifier of the map.

    **Returns**:
    - JSON object with the following keys:
      - `imageUrl` (str): URL to fetch the map image (points to `/get_map/{map_id}`).
      - `bounds` (list): 2D array of coordinates [[min_y, min_x], [max_y, max_x]] defining the map’s extent.

    **Example Usage**:
    ```bash
    curl -X GET "http://192.168.210.226:8000/zoneviewer/get_map_data/101" -H "accept: application/json"
    ```
    Response:
    ```json
    {
      "imageUrl": "http://192.168.210.226:8000/zoneviewer/get_map/101",
      "bounds": [
        [0.0, 0.0],
        [50.0, 100.0]
      ]
    }
    ```

    **Use Case**:
    - **Scenario**: The Zone Viewer needs to display a map with zones overlaid.
    - **Action**: The React frontend calls this endpoint to get the image URL and bounds, then renders the map
      using a library like Leaflet or Canvas.
    - **Outcome**: The map is displayed with correct scaling, and zones are accurately positioned.

    **Errors**:
    - **404 Not Found**: Raised if no map data is found for the given `map_id` (`HTTPException`, detail="No map data found for map_id={map_id}").
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - This endpoint is optimized for frontend integration. Use the `imageUrl` to fetch the map image and `bounds`
      to configure the map’s coordinate system in the UI.
    """
    try:
        map_data = await execute_raw_query(
            "maint",
            "SELECT min_x, min_y, max_x, max_y FROM maps WHERE i_map = $1",
            map_id
        )
        if not map_data:
            logger.warning(f"No map data found for map_id={map_id}")
            raise HTTPException(status_code=404, detail=f"No map data found for map_id={map_id}")

        logger.info(f"Retrieved map data for map_id={map_id}")
        data = map_data[0]
        return {
            "imageUrl": f"http://192.168.210.226:8000/zoneviewer/get_map/{map_id}",
            "bounds": [
                [float(data["min_y"]), float(data["min_x"])],
                [float(data["max_y"]), float(data["max_x"])]
            ]
        }
    except Exception as e:
        logger.error(f"Error retrieving map data for map_id={map_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_maps_with_zone_types")
async def get_maps_with_zone_types():
    """
    Fetch unique maps with their associated zone types, sorted by hierarchy.

    **Description**:
    This endpoint retrieves a list of unique maps, each associated with the highest-priority zone type (based on a
    predefined hierarchy). It is used in the ParcoRTLS system to provide a summary of maps and their primary zone
    types for selection in the Zone Viewer or for reporting purposes.

    **Parameters**:
    - None

    **Returns**:
    - JSON object with a single key `maps`, containing a list of map objects. Each map object has:
      - `i_map` (int): Unique identifier of the map.
      - `x_nm_map` (str): Name of the map.
      - `i_typ_zn` (int): The highest-priority zone type associated with the map (e.g., 1 for campus, 2 for building).

    **Example Usage**:
    ```bash
    curl -X GET "http://192.168.210.226:8000/zoneviewer/get_maps_with_zone_types" -H "accept: application/json"
    ```
    Response:
    ```json
    {
      "maps": [
        {
          "i_map": 101,
          "x_nm_map": "Main Campus Map",
          "i_typ_zn": 1
        },
        {
          "i_map": 102,
          "x_nm_map": "Building A Floor 1",
          "i_typ_zn": 2
        }
      ]
    }
    ```

    **Use Case**:
    - **Scenario**: A user needs to select a map in the Zone Viewer but wants to filter by zone type (e.g., campus or building).
    - **Action**: The frontend calls this endpoint to populate a dropdown or list of maps, showing their names and zone types.
    - **Outcome**: The user can quickly identify and select the relevant map.

    **Errors**:
    - **404 Not Found**: Raised if no maps are found (`HTTPException`, detail="No maps found").
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - The zone type hierarchy (1=campus, 10=area, 2=building, etc.) is defined in the SQL query. Refer to the
      ParcoRTLS documentation for zone type definitions.
    - Use this endpoint for map selection UI components or reporting tools.
    """
    try:
        maps_data = await execute_raw_query(
            "maint",
            """
            SELECT i_map, x_nm_map, i_typ_zn
            FROM (
                SELECT DISTINCT z.i_map, m.x_nm_map,
                    MIN(CASE z.i_typ_zn
                        WHEN 1 THEN 1
                        WHEN 10 THEN 2
                        WHEN 2 THEN 3
                        WHEN 3 THEN 4
                        WHEN 4 THEN 5
                        WHEN 5 THEN 6
                        ELSE 7
                    END) AS type_order,
                    MIN(z.i_typ_zn) AS i_typ_zn
                FROM public.zones z
                JOIN public.maps m ON z.i_map = m.i_map
                GROUP BY z.i_map, m.x_nm_map
            ) t
            ORDER BY type_order, x_nm_map;
            """
        )
        if not maps_data:
            logger.warning("No maps found")
            raise HTTPException(status_code=404, detail="No maps found")
        logger.info(f"Retrieved {len(maps_data)} unique maps with zone types")
        return {"maps": [{k: v for k, v in m.items() if k != "type_order"} for m in maps_data]}
    except Exception as e:
        logger.error(f"Error retrieving maps with zone types: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_all_zones_for_campus/{campus_id}")
async def get_all_zones_for_campus(campus_id: int):
    """
    Retrieve all zones under a specific campus, including hierarchy.

    **Description**:
    This endpoint fetches all zones under a given campus (identified by `campus_id`), including their hierarchical
    structure (parent-child relationships). It is used in the ParcoRTLS Zone Viewer to display all zones within a
    campus, such as buildings, floors, or rooms.

    **Parameters**:
    - `campus_id` (int, path parameter, required): The unique identifier of the campus.

    **Returns**:
    - JSON object with a single key `zones`, containing a list of zone objects. Each zone object has:
      - `zone_id` (int): Unique identifier of the zone.
      - `zone_name` (str): Name of the zone.
      - `zone_type` (int): Type of zone (e.g., 2 for building, 3 for floor).
      - `parent_zone_id` (int or null): ID of the parent zone.
      - `map_id` (int or null): ID of the associated map.
      - `children` (list): List of child zone objects with the same structure.

    **Example Usage**:
    ```bash
    curl -X GET "http://192.168.210.226:8000/zoneviewer/get_all_zones_for_campus/1" -H "accept: application/json"
    ```
    Response:
    ```json
    {
      "zones": [
        {
          "zone_id": 1,
          "zone_name": "Main Campus",
          "zone_type": 1,
          "parent_zone_id": null,
          "map_id": 101,
          "children": [
            {
              "zone_id": 2,
              "zone_name": "Building A",
              "zone_type": 2,
              "parent_zone_id": 1,
              "map_id": 102,
              "children": []
            }
          ]
        }
      ]
    }
    ```

    **Use Case**:
    - **Scenario**: A security team needs to manage zones within a campus to track assets.
    - **Action**: The frontend calls this endpoint to display all zones under the campus in a tree view.
    - **Outcome**: The team can navigate and manage zones efficiently.

    **Errors**:
    - **404 Not Found**: Not explicitly raised, but an empty `zones` list is returned if no zones are found.
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - Use this endpoint to populate a zone management interface for a specific campus.
    - Combine with `/get_vertices_for_campus/{campus_id}` to get spatial data for zones.
    """
    try:
        zones_data = await execute_raw_query(
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
        if not zones_data:
            logger.warning(f"No zones found for campus_id={campus_id}")
            return {"zones": []}

        zone_map = {z["i_zn"]: {
            "zone_id": z["i_zn"],
            "zone_name": z["x_nm_zn"],
            "zone_type": z["i_typ_zn"],
            "parent_zone_id": z["i_pnt_zn"],
            "map_id": z["i_map"],
            "children": []
        } for z in zones_data}

        zones = []
        for zone_id, zone_data in zone_map.items():
            if zone_data["parent_zone_id"] is None:
                zones.append(zone_data)
            elif zone_data["parent_zone_id"] in zone_map:
                zone_map[zone_data["parent_zone_id"]]["children"].append(zone_data)

        logger.info(f"Retrieved {len(zones)} zones for campus_id={campus_id}")
        return {"zones": zones}
    except Exception as e:
        logger.error(f"Error fetching zones for campus_id={campus_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_vertices_for_campus/{campus_id}")
async def get_vertices_for_campus(campus_id: int):
    """
    Fetch all vertices for zones under a campus, excluding trigger regions.

    **Description**:
    This endpoint retrieves all vertex data (coordinates and order) for zones under a specified campus, excluding
    trigger regions (i_trg IS NULL). It is used in the ParcoRTLS Zone Viewer to render zone polygons on maps.

    **Parameters**:
    - `campus_id` (int, path parameter, required): The unique identifier of the campus.

    **Returns**:
    - JSON object with a single key `vertices`, containing a list of vertex objects. Each vertex object has:
      - `vertex_id` (int): Unique identifier of the vertex.
      - `i_rgn` (int): Region ID associated with the vertex.
      - `x` (float): X coordinate of the vertex.
      - `y` (float): Y coordinate of the vertex.
      - `z` (float): Z coordinate of the vertex (often 0.0).
      - `order` (float): Order of the vertex in the polygon.
      - `zone_id` (int): ID of the zone the vertex belongs to.

    **Example Usage**:
    ```bash
    curl -X GET "http://192.168.210.226:8000/zoneviewer/get_vertices_for_campus/1" -H "accept: application/json"
    ```
    Response:
    ```json
    {
      "vertices": [
        {
          "vertex_id": 1001,
          "i_rgn": 201,
          "x": 10.0,
          "y": 20.0,
          "z": 0.0,
          "order": 1.0,
          "zone_id": 2
        }
      ]
    }
    ```

    **Use Case**:
    - **Scenario**: A user wants to edit zone boundaries in the Zone Viewer.
    - **Action**: The frontend calls this endpoint to fetch vertex data and render zone polygons on the map.
    - **Outcome**: The user can visualize and modify zone shapes.

    **Errors**:
    - **404 Not Found**: Not explicitly raised, but an empty `vertices` list is returned if no vertices are found.
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - Use this endpoint to render zone polygons in the UI. Combine with `/get_map_data/{map_id}` for the map context.
    - The `order` field determines the sequence of vertices in a polygon, critical for correct rendering.
    """
    try:
        vertices_data = await execute_raw_query(
            "maint",
            """
            WITH RECURSIVE zone_hierarchy AS (
                SELECT i_zn FROM zones WHERE i_zn = $1
                UNION ALL
                SELECT z.i_zn FROM zones z
                JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn
            )
            SELECT v.i_vtx AS vertex_id, v.i_rgn, v.n_x AS x, v.n_y AS y, v.n_z AS z, v.n_ord AS "order", r.i_zn AS zone_id
            FROM vertices v
            JOIN regions r ON v.i_rgn = r.i_rgn
            JOIN zone_hierarchy zh ON r.i_zn = zh.i_zn
            WHERE r.i_trg IS NULL
            ORDER BY r.i_zn, v.n_ord
            """,
            campus_id
        )
        if not vertices_data:
            logger.warning(f"No vertices found for campus_id={campus_id}")
            return {"vertices": []}
        logger.info(f"Retrieved {len(vertices_data)} vertices for campus_id={campus_id}")
        return {"vertices": vertices_data}
    except Exception as e:
        logger.error(f"Error fetching vertices for campus_id={campus_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_vertices")
async def update_vertices(vertices: list[dict]):
    """
    Bulk update vertices for zones.

    **Description**:
    This endpoint updates multiple vertices (coordinates and order) in the ParcoRTLS system. It is used in the
    Zone Editor to save changes to zone polygon shapes after user modifications.

    **Parameters**:
    - `vertices` (list[dict], body, required): List of vertex objects to update. Each object must contain:
      - `vertex_id` (int, required): Unique identifier of the vertex.
      - `x` (float, required): New X coordinate.
      - `y` (float, required): New Y coordinate.
      - `z` (float, optional, default=0.0): New Z coordinate.
      - `order` (int, optional, default=1): New order of the vertex in the polygon.

    **Returns**:
    - JSON object with a single key `message` (str): Confirmation message ("Vertices updated successfully").

    **Example Usage**:
    ```bash
    curl -X POST "http://192.168.210.226:8000/zoneviewer/update_vertices" \
      -H "Content-Type: application/json" \
      -d '[
        {"vertex_id": 1001, "x": 15.0, "y": 25.0, "z": 0.0, "order": 1},
        {"vertex_id": 1002, "x": 20.0, "y": 30.0, "z": 0.0, "order": 2}
      ]'
    ```
    Response:
    ```json
    {
      "message": "Vertices updated successfully"
    }
    ```

    **Use Case**:
    - **Scenario**: A user drags vertices in the Zone Editor to adjust a zone’s shape.
    - **Action**: The frontend sends the updated vertex data to this endpoint to persist changes.
    - **Outcome**: The zone’s polygon is updated in the database.

    **Errors**:
    - **400 Bad Request**: Raised if the `vertices` list is empty (`HTTPException`, detail="No vertices provided").
    - **500 Internal Server Error**: Raised if not all vertices are updated or for database errors (`HTTPException`, detail=str(e) or "Partial update: {updated_count}/{len(vertices)}").

    **Hint**:
    - Ensure all `vertex_id` values exist in the database to avoid partial updates.
    - The coordinates are rounded to 6 decimal places for precision.
    """
    try:
        if not vertices:
            raise HTTPException(status_code=400, detail="No vertices provided")
        updated_count = 0
        for vertex in vertices:
            vertex_id = vertex.get("vertex_id")
            x = round(float(vertex.get("x")), 6)
            y = round(float(vertex.get("y")), 6)
            z = round(float(vertex.get("z", 0)), 6)
            order = int(vertex.get("order", 1))
            result = await execute_raw_query(
                "maint",
                """
                UPDATE vertices
                SET n_x = $1, n_y = $2, n_z = $3, n_ord = $4
                WHERE i_vtx = $5
                RETURNING i_vtx
                """,
                x, y, z, order, vertex_id
            )
            if result:
                updated_count += 1
        if updated_count == len(vertices):
            logger.info(f"Updated {updated_count} vertices successfully")
            return {"message": "Vertices updated successfully"}
        logger.error(f"Updated {updated_count} out of {len(vertices)} vertices")
        raise HTTPException(status_code=500, detail=f"Partial update: {updated_count}/{len(vertices)}")
    except Exception as e:
        logger.error(f"Error updating vertices: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_vertex/{vertex_id}")
async def delete_vertex(vertex_id: int):
    """
    Delete a specific vertex by ID.

    **Description**:
    This endpoint removes a vertex from the ParcoRTLS system, used in the Zone Editor to delete a point from a
    zone’s polygon shape.

    **Parameters**:
    - `vertex_id` (int, path parameter, required): The unique identifier of the vertex to delete.

    **Returns**:
    - JSON object with:
      - `message` (str): Confirmation message ("Vertex deleted successfully").
      - `vertex_id` (int): ID of the deleted vertex.

    **Example Usage**:
    ```bash
    curl -X DELETE "http://192.168.210.226:8000/zoneviewer/delete_vertex/1001" -H "accept: application/json"
    ```
    Response:
    ```json
    {
      "message": "Vertex deleted successfully",
      "vertex_id": 1001
    }
    ```

    **Use Case**:
    - **Scenario**: A user removes a vertex from a zone’s polygon to simplify its shape.
    - **Action**: The frontend calls this endpoint to delete the vertex.
    - **Outcome**: The zone’s polygon is updated in the database.

    **Errors**:
    - **404 Not Found**: Raised if the `vertex_id` does not exist (`HTTPException`, detail="Vertex {vertex_id} not found").
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - Deleting a vertex may affect the polygon’s shape. Ensure the remaining vertices maintain a valid polygon.
    - Use with `/get_vertices_for_campus/{campus_id}` to refresh the zone’s vertex data after deletion.
    """
    try:
        result = await execute_raw_query(
            "maint",
            "DELETE FROM vertices WHERE i_vtx = $1 RETURNING i_vtx",
            vertex_id
        )
        if not result:
            logger.warning(f"Vertex {vertex_id} not found")
            raise HTTPException(status_code=404, detail=f"Vertex {vertex_id} not found")
        logger.info(f"Deleted vertex {vertex_id}")
        return {"message": "Vertex deleted successfully", "vertex_id": vertex_id}
    except Exception as e:
        logger.error(f"Error deleting vertex {vertex_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_vertex")
async def add_vertex(request: AddVertexRequest):
    """
    Add a new vertex to a zone.

    **Description**:
    This endpoint adds a new vertex to a zone’s region, used in the Zone Editor to extend a zone’s polygon shape.
    It aligns with the `DataV2.VertexAdd` functionality from the original ParcoRTLS system.

    **Parameters**:
    - `request` (AddVertexRequest, body, required): Pydantic model with:
      - `zone_id` (int, required): ID of the zone to add the vertex to.
      - `x` (float, required): X coordinate of the new vertex.
      - `y` (float, required): Y coordinate of the new vertex.
      - `z` (float, optional, default=0.0): Z coordinate of the new vertex.
      - `order` (float, required): Order of the vertex in the polygon.

    **Returns**:
    - JSON object representing the new vertex, with:
      - `vertex_id` (int): ID of the new vertex.
      - `i_rgn` (int): Region ID the vertex belongs to.
      - `x` (float): X coordinate.
      - `y` (float): Y coordinate.
      - `z` (float): Z coordinate.
      - `order` (float): Order in the polygon.
      - `zone_id` (int): ID of the zone.

    **Example Usage**:
    ```bash
    curl -X POST "http://192.168.210.226:8000/zoneviewer/add_vertex" \
      -H "Content-Type: application/json" \
      -d '{"zone_id": 2, "x": 30.0, "y": 40.0, "z": 0.0, "order": 3}'
    ```
    Response:
    ```json
    {
      "vertex_id": 1003,
      "i_rgn": 201,
      "x": 30.0,
      "y": 40.0,
      "z": 0.0,
      "order": 3.0,
      "zone_id": 2
    }
    ```

    **Use Case**:
    - **Scenario**: A user adds a new point to a zone’s polygon to refine its shape.
    - **Action**: The frontend sends the vertex data to this endpoint to create the vertex.
    - **Outcome**: The zone’s polygon is updated with the new vertex.

    **Errors**:
    - **404 Not Found**: Raised if no region is found for the `zone_id` (`HTTPException`, detail="No region found for zone_id={zone_id}").
    - **400 Bad Request**: Raised if the region ID does not exist (`HTTPException`, detail="Region ID {region_id} does not exist").
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - Ensure the `zone_id` has an associated region in the `regions` table.
    - The `order` field determines the vertex’s position in the polygon sequence.
    """
    try:
        logger.debug(f"Received add_vertex request: {request.dict()}")
        region_data = await execute_raw_query(
            "maint",
            "SELECT i_rgn FROM regions WHERE i_zn = $1 LIMIT 1",
            request.zone_id
        )
        if not region_data:
            logger.warning(f"No region found for zone_id={request.zone_id}")
            raise HTTPException(status_code=404, detail=f"No region found for zone_id={request.zone_id}")
        region_id = region_data[0]["i_rgn"]

        region_exists = await execute_raw_query(
            "maint",
            "SELECT i_rgn FROM public.regions WHERE i_rgn = $1",
            region_id
        )
        if not region_exists:
            logger.warning(f"Region ID {region_id} not found")
            raise HTTPException(status_code=400, detail=f"Region ID {region_id} does not exist")

        query = """
            INSERT INTO public.vertices (i_rgn, n_x, n_y, n_z, n_ord)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING i_vtx AS vertex_id, i_rgn, n_x AS x, n_y AS y, n_z AS z, n_ord AS "order"
        """
        result = await execute_raw_query(
            "maint",
            query,
            region_id,
            request.x,
            request.y,
            request.z,
            int(request.order)
        )
        if not result:
            logger.error("Failed to add vertex: no rows inserted")
            raise HTTPException(status_code=500, detail="Failed to add vertex")

        new_vertex = result[0]
        new_vertex["zone_id"] = request.zone_id
        logger.info(f"Added vertex {new_vertex['vertex_id']} to zone_id={request.zone_id}")
        return new_vertex
    except Exception as e:
        logger.error(f"Error adding vertex to zone_id={request.zone_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_zone_recursive/{zone_id}")
async def delete_zone_recursive(zone_id: int):
    """Delete a zone and all its progeny recursively.

    **Description**:
    This endpoint deletes a zone and all its child zones (progeny), along with associated regions and vertices.
    It is used in the Zone Editor to remove entire zone hierarchies, such as when decommissioning a campus or building.

    **Parameters**:
    - `zone_id` (int, path parameter, required): The unique identifier of the zone to delete.

    **Returns**:
    - JSON object with a single key `message` (str): Confirmation message indicating the zone and its progeny were deleted.

    **Example Usage**:
    ```bash
    curl -X DELETE "http://192.168.210.226:8000/zoneviewer/delete_zone_recursive/1" -H "accept: application/json"
    ```
    Response:
    ```json
    {
      "message": "Deleted zone 1 and its progeny successfully"
    }
    ```

    **Use Case**:
    - **Scenario**: A facility manager needs to remove an obsolete campus from the ParcoRTLS system.
    - **Action**: The frontend calls this endpoint to delete the campus and all its zones.
    - **Outcome**: The database is updated, and the campus is removed from the system.

    **Errors**:
    - **404 Not Found**: Raised if the `zone_id` does not exist (`HTTPException`, detail="Zone {zone_id} not found").
    - **500 Internal Server Error**: Raised for database errors or unexpected failures (`HTTPException`, detail=str(e)).

    **Hint**:
    - Use with caution, as this endpoint permanently deletes zones and their data.
    - Ensure no active tags or entities are associated with the zones before deletion."""
    try:
        logger.info(f"Attempting to delete zone {zone_id} and its progeny")

        async with get_db_connection() as connection:
            result = connection.execute(
                text("""
                WITH RECURSIVE zone_hierarchy AS (
                    SELECT i_zn FROM zones WHERE i_zn = :zone_id
                    UNION ALL
                    SELECT z.i_zn FROM zones z
                    JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn
                )
                SELECT i_zn FROM zone_hierarchy
                """),
                {"zone_id": zone_id}
            )
            zones_to_delete = result.fetchall()
            if not zones_to_delete:
                logger.warning(f"No zones found to delete for zone_id={zone_id}")
                raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found")

            zone_ids = [row[0] for row in zones_to_delete]
            logger.debug(f"Zones to delete: {zone_ids}")

            connection.execute(
                text("""
                DELETE FROM vertices
                USING regions r
                WHERE vertices.i_rgn = r.i_rgn AND r.i_zn IN :zone_ids
                """),
                {"zone_ids": tuple(zone_ids)}
            )

            connection.execute(
                text("DELETE FROM regions WHERE i_zn IN :zone_ids"),
                {"zone_ids": tuple(zone_ids)}
            )

            connection.execute(
                text("DELETE FROM zones WHERE i_zn IN :zone_ids"),
                {"zone_ids": tuple(zone_ids)}
            )

        logger.info(f"Successfully deleted zone {zone_id} and its {len(zone_ids)} progeny")
        return {"message": f"Deleted zone {zone_id} and its progeny successfully"}
    except Exception as e:
        logger.error(f"Error deleting zone {zone_id} and its progeny: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))