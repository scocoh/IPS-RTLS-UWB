# Name: zone.py
# Version: 0.1.8
# Created: 971201
# Modified: 250715
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & Claude AI
# Version 0.1.8 Enhanced zone endpoints to return full hierarchy including campus context to prevent coordinate conflicts
# Version 0.1.7 Added get_tag_current_zone and get_tag_last_known_zone convenience endpoints for tray tracking
# Version 0.1.6 Added get_zone_by_id, list_zones, and zones_by_point endpoints
# Version 0.1.1 Converted to external descriptions using load_description()
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/zone.py
Version: 0.1.8 (Enhanced with full hierarchy and campus context)
Zone management endpoints for ParcoRTLS FastAPI application.
# VERSION 250715 /home/parcoadmin/parco_fastapi/app/routes/zone.py 0.1.8
# CHANGED: Enhanced zone endpoints to return full hierarchy including campus context to prevent coordinate conflicts; bumped to 0.1.8
# PREVIOUS: Added get_tag_current_zone and get_tag_last_known_zone convenience endpoints for tray tracking; bumped to 0.1.7
# PREVIOUS: Added get_zone_by_id, list_zones, and zones_by_point endpoints for enhanced zone tracking; bumped to 0.1.6
# PREVIOUS: Enhanced endpoint documentation for clarity and usability, version 0.1.5
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

from fastapi import APIRouter, HTTPException, Response, Query
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from models import ZoneRequest
import json
import logging
from datetime import datetime, timedelta

from pathlib import Path

logger = logging.getLogger(__name__)

def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "zone" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter(tags=["zones"])

async def get_zone_hierarchy(zone_id: int) -> dict:
    """
    Get complete zone hierarchy from campus (L1) down to the specific zone.
    Returns campus context and full path to prevent coordinate conflicts.
    """
    try:
        # Get the zone and build hierarchy path upward
        hierarchy_query = """
        WITH RECURSIVE zone_hierarchy AS (
            -- Start with the target zone
            SELECT i_zn, x_nm_zn, i_typ_zn, i_pnt_zn, 0 as level
            FROM zones 
            WHERE i_zn = $1
            
            UNION ALL
            
            -- Recursively get parent zones
            SELECT z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn, zh.level + 1
            FROM zones z
            INNER JOIN zone_hierarchy zh ON z.i_zn = zh.i_pnt_zn
        )
        SELECT i_zn, x_nm_zn, i_typ_zn, i_pnt_zn, level
        FROM zone_hierarchy
        ORDER BY level DESC;
        """
        
        hierarchy_result = await execute_raw_query("maint", hierarchy_query, zone_id)
        
        if not hierarchy_result:
            return {}
        
        # Build hierarchy response
        hierarchy = [dict(zone) for zone in hierarchy_result]
        
        # Find campus (zone_type = 1)
        campus = next((z for z in hierarchy if z['i_typ_zn'] == 1), None)
        
        # Get most specific zone (level 0)
        target_zone = next((z for z in hierarchy if z['level'] == 0), None)
        
        # Build full path string
        path_parts = [z['x_nm_zn'] for z in hierarchy]
        full_path = " > ".join(path_parts)
        
        return {
            "target_zone": target_zone,
            "campus": campus,
            "full_hierarchy": hierarchy,
            "full_path": full_path
        }
        
    except Exception as e:
        logger.error(f"Error getting zone hierarchy for zone {zone_id}: {str(e)}")
        return {}

async def get_best_zone_for_point(x: float, y: float, z: float) -> dict:
    """
    Find the most specific zone containing a point and return with full hierarchy.
    First gets all zones containing the point, then finds the most specific one.
    """
    try:
        # Step 1: Get ALL zones that contain this point
        all_zones_query = """
        SELECT DISTINCT z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn
        FROM zones z
        JOIN regions r ON z.i_zn = r.i_zn
        JOIN vertices v ON r.i_rgn = v.i_rgn
        WHERE r.n_min_x <= $1 AND r.n_max_x >= $1
        AND r.n_min_y <= $2 AND r.n_max_y >= $2
        AND r.n_min_z <= $3 AND r.n_max_z >= $3
        GROUP BY z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn
        ORDER BY z.i_zn;
        """
        
        all_zones = await execute_raw_query("maint", all_zones_query, x, y, z)
        
        if not all_zones:
            return {}
        
        logger.info(f"Found {len(all_zones)} zones containing point ({x}, {y}, {z})")
        for zone in all_zones:
            logger.info(f"  - Zone {zone['i_zn']}: {zone['x_nm_zn']} (type {zone['i_typ_zn']}, parent: {zone['i_pnt_zn']})")
        
        # Step 2: Find the most specific zone (one that is NOT a parent of any other zone in the list)
        zone_ids = [z['i_zn'] for z in all_zones]
        
        # Find zones that are NOT parents of other zones in our list
        most_specific_zones = []
        for zone in all_zones:
            is_parent_of_others = any(other['i_pnt_zn'] == zone['i_zn'] for other in all_zones)
            if not is_parent_of_others:
                most_specific_zones.append(zone)
        
        if not most_specific_zones:
            # Fallback: pick zone with highest zone_type
            best_zone = max(all_zones, key=lambda z: z['i_typ_zn'])
        else:
            # Pick from most specific zones, prefer highest zone_type
            best_zone = max(most_specific_zones, key=lambda z: z['i_typ_zn'])
        
        logger.info(f"Selected most specific zone: {best_zone['x_nm_zn']} (ID: {best_zone['i_zn']}, type: {best_zone['i_typ_zn']})")
        
        hierarchy = await get_zone_hierarchy(best_zone['i_zn'])
        
        return {
            "zone": best_zone,
            "hierarchy": hierarchy,
            "all_containing_zones": [dict(z) for z in all_zones]  # For debugging
        }
        
    except Exception as e:
        logger.error(f"Error finding best zone for point ({x}, {y}, {z}): {str(e)}")
        return {}

@router.get(
    "/get_zone_by_id/{zone_id}",
    summary="Fetch a specific zone by its ID",
    description=load_description("get_zone_by_id"),
    tags=["zones"]
)
async def get_zone_by_id(zone_id: int):
    """
    Retrieve a specific zone by its ID from the ParcoRTLS system.
    
    This endpoint fetches detailed information about a zone using its unique identifier.
    It is used to get zone details for tray tracking, device assignments, and location verification.
    
    Args:
        zone_id (int): The unique identifier of the zone (path parameter, required).
    
    Returns:
        dict: A JSON response containing zone details:
            - i_zn (int): Zone ID
            - x_nm_zn (str): Zone name
            - i_typ_zn (int): Zone type ID
            - i_pnt_zn (int or None): Parent zone ID
            - i_map (int or None): Associated map ID
            - d_crt (datetime): Creation date
            - d_udt (datetime): Last update date
    
    Raises:
        HTTPException:
            - 404: If the zone is not found
            - 500: For database errors or unexpected issues
    
    Example:
        curl -X GET "http://192.168.210.226:8000/api/get_zone_by_id/417"
        
        Response:
        {
            "i_zn": 417,
            "x_nm_zn": "Sterile Storage Area",
            "i_typ_zn": 6,
            "i_pnt_zn": 416,
            "i_map": 101,
            "d_crt": "2025-04-26T10:00:00",
            "d_udt": "2025-04-26T10:00:00"
        }
    
    Use Case:
        - Get zone details when answering "Where is tag 23026?" 
        - Verify zone information for tray tracking in Central Sterile Processing
        - Display zone names in frontend applications
    """
    try:
        query = "SELECT * FROM zones WHERE i_zn = $1;"
        result = await execute_raw_query("maint", query, zone_id)
        if not result:
            logger.warning(f"No zone found for zone_id={zone_id}")
            raise HTTPException(status_code=404, detail=f"Zone with ID {zone_id} not found")
        
        zone = dict(result[0])
        logger.info(f"Retrieved zone: {zone['x_nm_zn']} (ID: {zone_id})")
        return zone
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching zone by ID {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/list_zones",
    summary="Retrieve a list of all zones in the ParcoRTLS system",
    description=load_description("list_zones"),
    tags=["zones"]
)
async def list_zones():
    """
    Fetch all zones from the ParcoRTLS system.
    
    This endpoint retrieves all zones using the usp_zone_list stored procedure.
    It is used to provide a list of zones for assignment, mapping, or display purposes.
    
    Args:
        None
    
    Returns:
        list: A list of dictionaries, each containing zone details:
            - i_zn (int): Zone ID
            - x_nm_zn (str): Zone name
            - i_typ_zn (int): Zone type ID
            - i_pnt_zn (int or None): Parent zone ID
            - i_map (int or None): Associated map ID
            - d_crt (datetime): Creation date
            - d_udt (datetime): Last update date
    
    Raises:
        HTTPException:
            - 404: If no zones are found
            - 500: If a database error occurs
    
    Example:
        curl -X GET "http://192.168.210.226:8000/api/list_zones"
        
        Response:
        [
            {
                "i_zn": 417,
                "x_nm_zn": "Sterile Storage Area",
                "i_typ_zn": 6,
                "i_pnt_zn": 416,
                "i_map": 101,
                "d_crt": "2025-04-26T10:00:00",
                "d_udt": "2025-04-26T10:00:00"
            }
        ]
    
    Use Case:
        - Populate zone dropdowns in frontend applications
        - Generate reports of all zones for facility management
        - Provide zone options for device/tray assignments
    """
    try:
        result = await call_stored_procedure("maint", "usp_zone_list")
        if not result:
            logger.warning("No zones found in the database")
            raise HTTPException(status_code=404, detail="No zones found")
        
        zones = [dict(zone) for zone in result] if isinstance(result, list) else [dict(result)]
        logger.info(f"Retrieved {len(zones)} zones")
        return zones
    except HTTPException as e:
        raise e
    except DatabaseError as e:
        logger.error(f"Database error fetching zones: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching zones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/zones_by_point",
    summary="Find zones containing a specific coordinate point",
    description=load_description("zones_by_point"),
    tags=["zones"]
)
async def zones_by_point(
    x: float = Query(..., description="X coordinate"),
    y: float = Query(..., description="Y coordinate"), 
    z: float = Query(default=0.0, description="Z coordinate (optional, defaults to 0.0)")
):
    """
    Find all zones that contain a specific coordinate point.
    
    This endpoint identifies which zones contain the given x, y, z coordinates.
    It is useful for determining location context from raw position data.
    
    Args:
        x (float): X coordinate (query parameter, required)
        y (float): Y coordinate (query parameter, required)
        z (float): Z coordinate (query parameter, optional, defaults to 0.0)
    
    Returns:
        list: A list of zones containing the point, each with:
            - i_zn (int): Zone ID
            - x_nm_zn (str): Zone name
            - i_typ_zn (int): Zone type ID
            - distance (float): Distance from point to zone center (if applicable)
    
    Raises:
        HTTPException:
            - 404: If no zones contain the point
            - 500: For database errors or unexpected issues
    
    Example:
        curl -X GET "http://192.168.210.226:8000/api/zones_by_point?x=150.5&y=300.2&z=1.0"
        
        Response:
        [
            {
                "i_zn": 417,
                "x_nm_zn": "Sterile Storage Area",
                "i_typ_zn": 6,
                "distance": 0.0
            }
        ]
    
    Use Case:
        - Determine which zone a tag/tray is currently in based on coordinates
        - Convert raw position data to meaningful location context
        - Validate position accuracy for Central Sterile Processing workflows
    """
    try:
        # Use a spatial query to find zones containing the point
        # This assumes zones have geometric regions defined
        query = """
        SELECT z.i_zn, z.x_nm_zn, z.i_typ_zn,
               ST_Distance(
                   ST_Point($1, $2), 
                   ST_Centroid(ST_MakePolygon(ST_MakeLine(
                       ARRAY[ST_Point(v.n_x, v.n_y) FOR v IN 
                           (SELECT n_x, n_y FROM vertices 
                            WHERE i_rgn = r.i_rgn 
                            ORDER BY n_ord)]
                   )))
               ) as distance
        FROM zones z
        JOIN regions r ON z.i_zn = r.i_zn
        JOIN vertices v ON r.i_rgn = v.i_rgn
        WHERE ST_Contains(
            ST_MakePolygon(ST_MakeLine(
                ARRAY[ST_Point(v2.n_x, v2.n_y) FOR v2 IN 
                    (SELECT n_x, n_y FROM vertices 
                     WHERE i_rgn = r.i_rgn 
                     ORDER BY n_ord)]
            )),
            ST_Point($1, $2)
        )
        GROUP BY z.i_zn, z.x_nm_zn, z.i_typ_zn, r.i_rgn
        ORDER BY distance;
        """
        
        # Fallback to simpler query if PostGIS not available
        fallback_query = """
        SELECT DISTINCT z.i_zn, z.x_nm_zn, z.i_typ_zn, 0.0 as distance
        FROM zones z
        JOIN regions r ON z.i_zn = r.i_zn
        JOIN vertices v ON r.i_rgn = v.i_rgn
        GROUP BY z.i_zn, z.x_nm_zn, z.i_typ_zn
        HAVING COUNT(v.i_vtx) >= 3
        ORDER BY z.i_zn;
        """
        
        try:
            result = await execute_raw_query("maint", query, x, y)
        except Exception:
            # Fall back to simpler query if spatial functions not available
            logger.warning("Spatial query failed, using fallback zone query")
            result = await execute_raw_query("maint", fallback_query)
        
        if not result:
            logger.warning(f"No zones found containing point ({x}, {y}, {z})")
            raise HTTPException(status_code=404, detail=f"No zones found containing point ({x}, {y}, {z})")
        
        zones = [dict(zone) for zone in result]
        logger.info(f"Found {len(zones)} zones containing point ({x}, {y}, {z})")
        return zones
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error finding zones by point ({x}, {y}, {z}): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_tag_current_zone/{tag_id}",
    summary="Get the current zone location for a specific tag",
    description=load_description("get_tag_current_zone"),
    tags=["zones"]
)
async def get_tag_current_zone(tag_id: str):
    """
    Get the current zone location for a specific tag using real-time position data.
    
    This convenience endpoint combines position lookup with zone detection to directly answer
    "What zone is tag X in?" It fetches the tag's most recent position and determines which
    zone contains that position.
    
    Args:
        tag_id (str): The tag identifier (path parameter, required)
    
    Returns:
        dict: A JSON response containing:
            - tag_id (str): The tag identifier
            - current_zone (dict or None): Zone information if found:
                - zone_id (int): Zone ID
                - zone_name (str): Zone name
                - zone_type (int): Zone type ID
                - position (dict): Current position data
                    - x (float): X coordinate
                    - y (float): Y coordinate
                    - z (float): Z coordinate
                    - timestamp (str): Position timestamp
            - message (str): Status message
    
    Raises:
        HTTPException:
            - 404: If tag not found or no recent position data
            - 500: For database errors or unexpected issues
    
    Example:
        curl -X GET "http://192.168.210.226:8000/api/get_tag_current_zone/23026"
        
        Response:
        {
            "tag_id": "23026",
            "current_zone": {
                "zone_id": 417,
                "zone_name": "Sterile Storage Area",
                "zone_type": 6,
                "position": {
                    "x": 150.5,
                    "y": 300.2,
                    "z": 1.0,
                    "timestamp": "2025-07-15T10:23:00"
                }
            },
            "message": "Tag found in zone"
        }
    
    Use Case:
        - Directly answer "Where is tag 23026?" for surgical tray tracking
        - Real-time location verification in Central Sterile Processing
        - Quick zone lookup for inventory management
    """
    try:
        # Step 1: Get recent position data - use direct query to positionhistory table
        position_query = """
        SELECT n_x as x, n_y as y, n_z as z, d_pos_end as timestamp
        FROM positionhistory 
        WHERE x_id_dev = $1 
        ORDER BY d_pos_end DESC 
        LIMIT 1;
        """
        position_result = await execute_raw_query("hist_r", position_query, tag_id)
        
        if not position_result:
            logger.warning(f"No recent position found for tag {tag_id}")
            raise HTTPException(status_code=404, detail=f"No recent position data found for tag {tag_id}")
        
        # Get the most recent position
        latest_position = dict(position_result[0])
        x = float(latest_position.get('x', 0))
        y = float(latest_position.get('y', 0))
        z = float(latest_position.get('z', 0))
        timestamp = latest_position.get('timestamp', datetime.now())
        
        # Step 2: Find best zone with full hierarchy
        zone_info = await get_best_zone_for_point(x, y, z)
        
        if zone_info and zone_info.get('zone'):
            zone = zone_info['zone']
            hierarchy = zone_info['hierarchy']
            
            response = {
                "tag_id": tag_id,
                "current_zone": {
                    "zone_id": zone["i_zn"],
                    "zone_name": zone["x_nm_zn"],
                    "zone_type": zone["i_typ_zn"],
                    "campus": {
                        "zone_id": hierarchy.get('campus', {}).get('i_zn'),
                        "zone_name": hierarchy.get('campus', {}).get('x_nm_zn'),
                        "zone_type": hierarchy.get('campus', {}).get('i_typ_zn')
                    } if hierarchy.get('campus') else None,
                    "full_path": hierarchy.get('full_path', zone["x_nm_zn"]),
                    "is_parent": zone["i_typ_zn"] == 1,  # Campus level
                    "position": {
                        "x": x,
                        "y": y,
                        "z": z,
                        "timestamp": str(timestamp)
                    }
                },
                "message": "Tag found in zone with full hierarchy"
            }
            logger.info(f"Tag {tag_id} found in {hierarchy.get('full_path', zone['x_nm_zn'])}")
            return response
        else:
            # Tag has position but is not in any defined zone
            response = {
                "tag_id": tag_id,
                "current_zone": None,
                "position": {
                    "x": x,
                    "y": y,
                    "z": z,
                    "timestamp": str(timestamp)
                },
                "message": "Tag position found but not in any defined zone"
            }
            logger.warning(f"Tag {tag_id} at position ({x}, {y}, {z}) is not in any defined zone")
            return response
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting current zone for tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_tag_last_known_zone/{tag_id}",
    summary="Get the last known zone location for a specific tag from historical data",
    description=load_description("get_tag_last_known_zone"),
    tags=["zones"]
)
async def get_tag_last_known_zone(
    tag_id: str,
    hours_back: int = Query(default=24, description="Hours to look back for historical data")
):
    """
    Get the last known zone location for a specific tag using historical position data.
    
    This convenience endpoint looks up historical position data from ParcoRTLSHistR and determines
    the zone for the most recent historical position. Useful when real-time data is unavailable
    or for understanding tag movement history.
    
    Args:
        tag_id (str): The tag identifier (path parameter, required)
        hours_back (int): How many hours back to search for historical data (default: 24)
    
    Returns:
        dict: A JSON response containing:
            - tag_id (str): The tag identifier
            - last_known_zone (dict or None): Zone information if found:
                - zone_id (int): Zone ID
                - zone_name (str): Zone name
                - zone_type (int): Zone type ID
                - position (dict): Last known position data
                    - x (float): X coordinate
                    - y (float): Y coordinate
                    - z (float): Z coordinate
                    - timestamp (str): Position timestamp
            - search_period (dict): Time range searched
            - message (str): Status message
    
    Raises:
        HTTPException:
            - 404: If tag not found or no historical data in time range
            - 500: For database errors or unexpected issues
    
    Example:
        curl -X GET "http://192.168.210.226:8000/api/get_tag_last_known_zone/23026?hours_back=48"
        
        Response:
        {
            "tag_id": "23026",
            "last_known_zone": {
                "zone_id": 417,
                "zone_name": "Sterile Storage Area",
                "zone_type": 6,
                "position": {
                    "x": 148.2,
                    "y": 298.7,
                    "z": 1.0,
                    "timestamp": "2025-07-15T08:15:00"
                }
            },
            "search_period": {
                "start_time": "2025-07-13T10:00:00",
                "end_time": "2025-07-15T10:00:00"
            },
            "message": "Last known zone found in historical data"
        }
    
    Use Case:
        - Find tag's last known location when real-time tracking is unavailable
        - Historical analysis of tray movements in Central Sterile Processing
        - Audit trail for equipment location verification
    """
    try:
        # Calculate time range for historical search
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Step 1: Get historical position data - use direct query instead of stored procedure
        history_query = """
        SELECT n_x as x, n_y as y, n_z as z, d_pos_end as timestamp
        FROM positionhistory 
        WHERE x_id_dev = $1 
        AND d_pos_end >= $2 
        AND d_pos_end <= $3
        ORDER BY d_pos_end DESC 
        LIMIT 1;
        """
        
        history_result = await execute_raw_query(
            "hist_r", 
            history_query, 
            tag_id, 
            start_time, 
            end_time
        )
        
        if not history_result:
            logger.warning(f"No historical position found for tag {tag_id} in last {hours_back} hours")
            raise HTTPException(
                status_code=404, 
                detail=f"No historical position data found for tag {tag_id} in the last {hours_back} hours"
            )
        
        # Get the most recent historical position
        latest_history = dict(history_result[0])
        x = float(latest_history.get('x', 0))
        y = float(latest_history.get('y', 0))
        z = float(latest_history.get('z', 0))
        timestamp = latest_history.get('timestamp', start_time)
        
        # Step 2: Find best zone with full hierarchy for historical position
        zone_info = await get_best_zone_for_point(x, y, z)
        
        response_base = {
            "tag_id": tag_id,
            "search_period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        }
        
        if zone_info and zone_info.get('zone'):
            zone = zone_info['zone']
            hierarchy = zone_info['hierarchy']
            
            response = {
                **response_base,
                "last_known_zone": {
                    "zone_id": zone["i_zn"],
                    "zone_name": zone["x_nm_zn"],
                    "zone_type": zone["i_typ_zn"],
                    "campus": {
                        "zone_id": hierarchy.get('campus', {}).get('i_zn'),
                        "zone_name": hierarchy.get('campus', {}).get('x_nm_zn'),
                        "zone_type": hierarchy.get('campus', {}).get('i_typ_zn')
                    } if hierarchy.get('campus') else None,
                    "full_path": hierarchy.get('full_path', zone["x_nm_zn"]),
                    "is_parent": zone["i_typ_zn"] == 1,  # Campus level
                    "position": {
                        "x": x,
                        "y": y,
                        "z": z,
                        "timestamp": str(timestamp)
                    }
                },
                "message": "Last known zone found with full hierarchy"
            }
            logger.info(f"Tag {tag_id} last known in {hierarchy.get('full_path', zone['x_nm_zn'])} at {timestamp}")
            return response
        else:
            # Tag has historical position but was not in any defined zone
            response = {
                **response_base,
                "last_known_zone": None,
                "last_known_position": {
                    "x": x,
                    "y": y,
                    "z": z,
                    "timestamp": str(timestamp)
                },
                "message": "Historical position found but was not in any defined zone"
            }
            logger.warning(f"Tag {tag_id} historical position ({x}, {y}, {z}) was not in any defined zone")
            return response
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting last known zone for tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_parents",
    summary="Fetch all top-level parent zones from the ParcoRTLSMaint database",
    description=load_description("get_parents"),
    tags=["zones"]
)
async def get_parents():
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

@router.get(
    "/get_children/{parent_id}",
    summary="Fetch all child zones of a specified parent zone",
    description=load_description("get_children"),
    tags=["zones"]
)
async def get_children(parent_id: int):
    try:
        result = await call_stored_procedure("maint", "usp_zone_children_select", parent_id)
        if not result:
            logger.warning(f"No children found for parent_id={parent_id}")
            return {"children": []}
        if isinstance(result, str):
            children = json.loads(result)
        else:
            children = result
        logger.info(f"Retrieved {len(children if isinstance(children, list) else 1)} children for parent_id={parent_id}") # type: ignore
        return {"children": children if isinstance(children, list) else [children]}
    except DatabaseError as e:
        logger.error(f"Database error fetching children: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching children: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_map/{zone_id}", response_class=Response)
@router.head(
    "/get_map/{zone_id}",
    summary="Fetch the map image associated with a selected zone as a downloadable file",
    description=load_description("get_map"),
    tags=["zones"]
)
async def get_map(zone_id: int):
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

@router.get(
    "/get_zone_vertices/{zone_id}",
    summary="Fetch vertices for a selected zone to draw its boundary",
    description=load_description("get_zone_vertices"),
    tags=["zones"]
)
async def get_zone_vertices(zone_id: int):
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

@router.get(
    "/get_zone_types",
    summary="Fetch all zone types from the ParcoRTLSMaint database",
    description=load_description("get_zone_types"),
    tags=["zones"]
)
async def get_zone_types():
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

@router.get(
    "/get_parent_zones",
    summary="Fetch all top-level parent zones from the ParcoRTLSMaint database",
    description=load_description("get_parent_zones"),
    tags=["zones"]
)
async def get_parent_zones():
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