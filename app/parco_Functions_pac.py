# Name: parco_Functions_pac.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

# Version: 250301 parco_Functions_pac.py Version 0P.7B.09g
# parco_functions.py
from db_connection_pac import get_db_connection, release_db_connection
import psycopg2
import logging
import sys  # For forcing output to stderr
import traceback  # For stack tracing

logging.basicConfig(level=logging.INFO, stream=sys.stderr)  # Force logs to stderr for terminal visibility
logger = logging.getLogger(__name__)

def get_zone_types():
    # Track call depth to prevent infinite recursion
    if not hasattr(get_zone_types, 'call_count'):
        get_zone_types.call_count = 0
    get_zone_types.call_count += 1
    if get_zone_types.call_count > 10:  # Limit to 10 calls to prevent deep recursion
        logger.error(f"Excessive recursion detected (call_count={get_zone_types.call_count}) - check for infinite loops")
        print(f"DEBUG: Excessive recursion detected (call_count={get_zone_types.call_count}) - check for infinite loops", file=sys.stderr)
        raise Exception(f"Excessive recursion detected (call_count={get_zone_types.call_count}) - check for infinite loops")

    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Database connection failed - check db_connection_pac.py")
            print(f"DEBUG: Database connection failed - check db_connection_pac.py", file=sys.stderr)
            raise Exception("Database connection failed - check db_connection_pac.py")
        logger.info("Querying tlkzonetypes for zone types")
        print(f"DEBUG: Querying tlkzonetypes for zone types (call_count={get_zone_types.call_count})", file=sys.stderr)
        cur = conn.cursor()
        cur.execute("SELECT i_typ_zn, x_dsc_zn FROM public.tlkzonetypes ORDER BY i_typ_zn")
        zones = cur.fetchall()
        logger.info(f"Fetched zones (raw) - type: {type(zones)}, value: {zones}")
        print(f"DEBUG: Fetched zones (raw) - type: {type(zones)}, value: {zones}", file=sys.stderr)
        if zones is None or not zones:
            logger.warning("No zone types found in tlkzonetypes")
            print("DEBUG: No zone types found in tlkzonetypes", file=sys.stderr)
            return []  # Return empty list if no data or None
        # Ensure zones is a list of tuples, even if it's a single row or tuple
        if isinstance(zones, tuple):
            zones = [zones]  # Convert single tuple to list of tuples
            logger.info(f"Converted single tuple to list: {zones}")
            print(f"DEBUG: Converted single tuple to list: {zones}", file=sys.stderr)
        elif not isinstance(zones, (list, tuple)):
            logger.error(f"Unexpected type for zones: {type(zones)}")
            print(f"DEBUG: Unexpected type for zones: {type(zones)}", file=sys.stderr)
            raise ValueError(f"Expected list or tuple of tuples from fetchall, got {type(zones)}")
        # Format the result to match the expected structure (i_typ_zn, x_dsc_zn)
        formatted_zones = [{'i_typ_zn': row[0], 'x_dsc_zn': row[1]} for row in zones if len(row) >= 2]
        logger.info(f"Formatted zones - type: {type(formatted_zones)}, value: {formatted_zones}")
        print(f"DEBUG: Formatted zones - type: {type(formatted_zones)}, value: {formatted_zones}", file=sys.stderr)
        return formatted_zones
    except psycopg2.Error as e:
        logger.error(f"Database error fetching zone types: {str(e)} - check db_connection_pac.py and permissions")
        print(f"DEBUG: Database error fetching zone types: {str(e)} - check db_connection_pac.py and permissions\n{traceback.format_exc()}", file=sys.stderr)
        raise Exception(f"Database error fetching zone types: {str(e)} - check db_connection_pac.py and permissions")
    except Exception as e:
        logger.error(f"Unexpected error fetching zone types: {str(e)} - check db_connection_pac.py and code context")
        print(f"DEBUG: Unexpected error fetching zone types: {str(e)} - check db_connection_pac.py and code context\n{traceback.format_exc()}", file=sys.stderr)
        raise Exception(f"Unexpected error fetching zone types: {str(e)} - check db_connection_pac.py and code context")
    finally:
        release_db_connection(conn)
        get_zone_types.call_count = 0  # Reset call count after execution

def create_zone(zone_name, map_id, zone_type, parent_zone_id, vertices):
    # Mock function for testing until the real Parco Function is identified
    logger.info(f"Mock create_zone called with: zone_name={zone_name}, map_id={map_id}, zone_type={zone_type}, parent_zone_id={parent_zone_id}, vertices={vertices}")
    print(f"DEBUG: Mock create_zone called with: zone_name={zone_name}, map_id={map_id}, zone_type={zone_type}, parent_zone_id={parent_zone_id}, vertices={vertices}", file=sys.stderr)
    return 1  # Return a dummy zone ID for testing