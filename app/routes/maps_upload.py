# VERSION 250426 /home/parcoadmin/parco_fastapi/app/routes/maps_upload.py 0P.1B.02
# Changelog:
# - 250426 (0P.1B.02): Enhanced docstrings for all endpoints with detailed descriptions, parameters, return values, examples, use cases, error handling, and hints.
# - 250309 (0P.1B.01): Initial implementation with upload, retrieve, edit, delete, and metadata endpoints for map management.
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
logger = logging.getLogger(__name__)

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
    """
    Upload a new map image and its metadata to the ParcoRTLS system.

    This endpoint allows users to upload a map image (e.g., a floor plan or campus layout) along with its metadata, such as name, geographic coordinates, and spatial boundaries. The map is stored in the PostgreSQL 'maint' schema in the 'maps' table, with the image stored as binary data. This endpoint is critical for defining the spatial context in which ParcoRTLS tracks entities (e.g., tags, devices) within zones, regions, or triggers.

    Parameters:
    - name (str, required): The name of the map (e.g., "Building A Floor 1").
    - lat_origin (float, optional): Latitude of the map's origin point (e.g., bottom-left corner). Defaults to None.
    - lon_origin (float, optional): Longitude of the map's origin point. Defaults to None.
    - min_x (float, optional): Minimum X-coordinate of the map's spatial boundary. Defaults to None.
    - min_y (float, optional): Minimum Y-coordinate of the map's spatial boundary. Defaults to None.
    - min_z (float, optional): Minimum Z-coordinate (e.g., for 3D maps). Defaults to None.
    - max_x (float, optional): Maximum X-coordinate of the map's spatial boundary. Defaults to None.
    - max_y (float, optional): Maximum Y-coordinate of the map's spatial boundary. Defaults to None.
    - max_z (float, optional): Maximum Z-coordinate of the map. Defaults to None.
    - file (UploadFile, required): The map image file to upload. Supported formats: PNG, JPG, JPEG, GIF.

    Returns:
    - JSON object with:
      - message (str): Confirmation message ("Map uploaded successfully").
      - map_id (int): The unique ID of the newly created map record.

    Raises:
    - HTTPException (400): If the file format is not supported (e.g., not PNG, JPG, JPEG, or GIF).
    - HTTPException (500): If the map upload fails due to database errors or other issues.

    Example:
    ```bash
    curl -X POST "http://192.168.210.226:8000/upload_map" \
         -F "name=Building A Floor 1" \
         -F "lat_origin=40.7128" \
         -F "lon_origin=-74.0060" \
         -F "min_x=0.0" \
         -F "min_y=0.0" \
         -F "max_x=100.0" \
         -F "max_y=50.0" \
         -F "file=@/path/to/floor1.png"
    ```
    Response:
    ```json
    {
      "message": "Map uploaded successfully",
      "map_id": 123
    }
    ```

    Use Case:
    - A facility manager uploads a new floor plan for a building to the ParcoRTLS system to enable real-time tracking of assets or personnel. For example, uploading a map for "Building A Floor 1" with its geographic coordinates allows the system to associate zones (e.g., rooms) and triggers (e.g., entry/exit alerts) with this map.

    Hint:
    - Ensure the map image is optimized (e.g., <4MB) to avoid performance issues. Large files trigger a warning in the logs but are still processed.
    - Provide `lat_origin` and `lon_origin` for outdoor maps to enable geolocation-based tracking.
    - Use `min_x`, `min_y`, `max_x`, and `max_y` to define the map's coordinate system for accurate zone and region placement.
    """
    try:
        img_binary = await file.read()
        file_format = file.filename.split('.')[-1].upper()

        allowed_formats = {"PNG", "JPG", "JPEG", "GIF"}
        if file_format not in allowed_formats:
            logger.warning(f"Unsupported file format attempted: {file_format}")
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_format}")

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

@router.get("/map_image/{map_id}")
async def get_map_image(map_id: int):
    """
    Retrieve the stored map image for a given map ID.

    This endpoint fetches the binary image data and file format of a map stored in the 'maps' table in the 'maint' schema. It returns the image as a response with the appropriate media type (e.g., image/png). This is used to display maps in the ParcoRTLS React frontend or other client applications.

    Parameters:
    - map_id (int, required): The unique ID of the map to retrieve (path parameter).

    Returns:
    - Binary image data with the appropriate media type (e.g., image/png, image/jpeg).

    Raises:
    - HTTPException (404): If the map ID does not exist in the database.
    - HTTPException (500): If there is an error retrieving the map image (e.g., database connection issues).

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/map_image/123" -o map_image.png
    ```

    Use Case:
    - The ParcoRTLS React frontend calls this endpoint to display a floor plan in the user interface when a user selects a specific map (e.g., "Building A Floor 1") for viewing or configuring zones.

    Hint:
    - Ensure the `map_id` corresponds to a valid map in the database. Use the `/upload_map` endpoint to create maps first.
    - The response media type is set based on the stored `x_format` (e.g., PNG, JPEG), so ensure the client can handle the returned format.
    """
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
    """
    Update the metadata of an existing map in the ParcoRTLS system.

    This endpoint allows users to modify the metadata (e.g., name, coordinates, boundaries) of a map without altering the stored image. The changes are applied to the 'maps' table in the 'maint' schema. This is useful for correcting map details or adjusting coordinates after initial upload.

    Parameters:
    - map_id (int, required): The unique ID of the map to update (path parameter).
    - name (str, required): The updated name of the map.
    - lat_origin (float, optional): Updated latitude of the map's origin point. Defaults to None.
    - lon_origin (float, optional): Updated longitude of the map's origin point. Defaults to None.
    - min_x (float, optional): Updated minimum X-coordinate. Defaults to None.
    - min_y (float, optional): Updated minimum Y-coordinate. Defaults to None.
    - min_z (float, optional): Updated minimum Z-coordinate. Defaults to None.
    - max_x (float, optional): Updated maximum X-coordinate. Defaults to None.
    - max_y (float, optional): Updated maximum Y-coordinate. Defaults to None.
    - max_z (float, optional): Updated maximum Z-coordinate. Defaults to None.

    Returns:
    - JSON object with:
      - message (str): Confirmation message ("Map updated successfully").

    Raises:
    - HTTPException (500): If the map update fails (e.g., database error).
    - HTTPException (404): If the map ID does not exist (handled by database query returning no rows).

    Example:
    ```bash
    curl -X PUT "http://192.168.210.226:8000/edit_map/123" \
         -F "name=Building A Floor 1 Updated" \
         -F "lat_origin=40.7129" \
         -F "lon_origin=-74.0061" \
         -F "min_x=0.0" \
         -F "min_y=0.0" \
         -F "max_x=100.0" \
         -F "max_y=50.0"
    ```
    Response:
    ```json
    {
      "message": "Map updated successfully"
    }
    ```

    Use Case:
    - A facility manager updates the coordinates of a map after discovering an error in the initial latitude/longitude values or adjusts the map name to reflect a new naming convention.

    Hint:
    - Only provide parameters that need updating; unchanged fields can be omitted (they will remain as None in the query).
    - Verify the `map_id` exists before calling this endpoint to avoid unnecessary errors.
    """
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

@router.delete("/delete_map/{map_id}")
async def delete_map(map_id: int):
    """
    Delete a map from the ParcoRTLS system.

    This endpoint removes a map and its associated metadata from the 'maps' table in the 'maint' schema. It is used when a map is no longer needed or was uploaded in error. Note that deleting a map may affect associated zones, regions, or triggers.

    Parameters:
    - map_id (int, required): The unique ID of the map to delete (path parameter).

    Returns:
    - JSON object with:
      - message (str): Confirmation message (e.g., "Map 123 deleted successfully").

    Raises:
    - HTTPException (404): If the map ID does not exist in the database.
    - HTTPException (500): If the deletion fails due to database errors.

    Example:
    ```bash
    curl -X DELETE "http://192.168.210.226:8000/delete_map/123"
    ```
    Response:
    ```json
    {
      "message": "Map 123 deleted successfully"
    }
    ```

    Use Case:
    - A facility manager deletes an outdated map (e.g., for a decommissioned building) to prevent it from being used in tracking operations.

    Hint:
    - Before deleting, check if the map is referenced by zones or regions using the `/get_map_zones/{map_id}` or `/get_map_regions/{map_id}` endpoints to avoid orphaned data.
    - Ensure no active tracking operations depend on this map to prevent disruptions.
    """
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

@router.get("/get_map_zones/{map_id}")
async def get_map_zones(map_id: int):
    """
    Retrieve the number of zones associated with a specific map.

    This endpoint queries the 'zones' table in the 'maint' schema to count the number of zones linked to a given map. It is useful for understanding the scope of a map's usage in the ParcoRTLS system.

    Parameters:
    - map_id (int, required): The unique ID of the map (path parameter).

    Returns:
    - JSON object with:
      - zone_count (int): The number of zones associated with the map (0 if none).

    Raises:
    - None explicitly, but database errors may result in a 500 status code (handled by FastAPI).

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/get_map_zones/123"
    ```
    Response:
    ```json
    {
      "zone_count": 5
    }
    ```

    Use Case:
    - A system administrator checks how many zones (e.g., rooms or areas) are defined for a map before updating or deleting it to assess its impact.

    Hint:
    - Use this endpoint before deleting a map to ensure no zones are orphaned.
    - A `zone_count` of 0 indicates the map is not yet associated with any zones, which may suggest it is safe to modify or delete.
    """
    query = """
        SELECT COUNT(*) AS zone_count 
        FROM zones 
        WHERE i_map = $1;
    """
    result = await execute_raw_query("maint", query, map_id)
    return {"zone_count": result[0]["zone_count"] if result else 0}

@router.get("/get_map_regions/{map_id}")
async def get_map_regions(map_id: int):
    """
    Retrieve the number of regions associated with a specific map.

    This endpoint counts the number of regions linked to a map by joining the 'regions' and 'zones' tables in the 'maint' schema. Regions are sub-areas within zones, and this endpoint helps assess the complexity of a map's configuration.

    Parameters:
    - map_id (int, required): The unique ID of the map (path parameter).

    Returns:
    - JSON object with:
      - region_count (int): The number of regions associated with the map (0 if none).

    Raises:
    - HTTPException (500): If there is an error fetching region data (e.g., database connection issues).

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/get_map_regions/123"
    ```
    Response:
    ```json
    {
      "region_count": 10
    }
    ```

    Use Case:
    - A developer checks the number of regions on a map to determine if additional configuration (e.g., triggers) is needed for fine-grained tracking within zones.

    Hint:
    - Regions are tied to zones, so ensure zones exist for the map (check with `/get_map_zones/{map_id}`) before expecting regions.
    - A high `region_count` may indicate a complex map with detailed sub-areas, requiring careful management.
    """
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

@router.get("/get_map_triggers/{map_id}")
async def get_map_triggers(map_id: int):
    """
    Retrieve the number of triggers associated with a specific map.

    This endpoint counts the number of triggers linked to a map by joining the 'triggers', 'regions', and 'zones' tables in the 'maint' schema. Triggers define actions (e.g., alerts) for specific events in regions, and this endpoint helps evaluate a map's automation setup.

    Parameters:
    - map_id (int, required): The unique ID of the map (path parameter).

    Returns:
    - JSON object with:
      - trigger_count (int): The number of triggers associated with the map (0 if none).

    Raises:
    - HTTPException (500): If there is an error fetching trigger data (e.g., database issues).

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/get_map_triggers/123"
    ```
    Response:
    ```json
    {
      "trigger_count": 3
    }
    ```

    Use Case:
    - A facility manager checks the number of triggers on a map to ensure all necessary alerts (e.g., for unauthorized entry into a restricted area) are configured.

    Hint:
    - Triggers depend on regions, which depend on zones. Verify the map has zones and regions (using `/get_map_zones/{map_id}` and `/get_map_regions/{map_id}`) before expecting triggers.
    - A `trigger_count` of 0 may indicate that automation rules have not yet been set up for the map.
    """
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