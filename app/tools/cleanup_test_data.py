"""
Version: 250227 cleanup_test_data.py Version 0P.2C.03

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import logging
import psycopg2
from psycopg2 import Error
import os  # Added for os.path.exists and os.makedirs

# ✅ Hardcode database credentials
DB_CONFIG = {
    'dbname': 'ParcoRTLSMaint',
    'user': 'parcoadmin',
    'password': 'parcoMCSE04106!',
    'host': '192.168.210.231',
    'port': '5432'
}

# ✅ Configure Logging
log_dir = "/home/parcoadmin/parco_fastapi/app/tools"
if not os.path.exists(log_dir):
    os.makedirs(log_dir, mode=0o755)
log_file = os.path.join(log_dir, "cleanup_test_data.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(log_file, mode='a')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.info("Cleanup script initialized successfully (Version 0P.2C.03).")

def get_db_connection():
    """Establish a new database connection with hardcoded credentials"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Database connection established successfully.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def release_db_connection(conn):
    """Safely close database connection"""
    try:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")

def fetch_zones_to_delete():
    """Fetch all zones to delete (since all data is test data)."""
    query = """
        SELECT i_zn, x_nm_zn, i_typ_zn, i_pnt_zn
        FROM zones
        ORDER BY i_zn;
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection.")
        return []
    try:
        cur = conn.cursor()
        cur.execute(query)
        zones = cur.fetchall()
        logger.info(f"Found {len(zones)} zones to delete (all test data).")
        return zones
    except Error as e:
        logger.error(f"Error fetching zones to delete: {str(e)}")
        return []
    finally:
        release_db_connection(conn)

def fetch_vertices_to_delete():
    """Fetch all vertices to delete (since all data is test data)."""
    query = """
        SELECT i_vtx as vertex_id, i_rgn as zone_id, n_x as x, n_y as y, n_z as z, n_ord as order
        FROM vertices
        ORDER BY i_vtx;
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection.")
        return []
    try:
        cur = conn.cursor()
        cur.execute(query)
        vertices = cur.fetchall()
        logger.info(f"Found {len(vertices)} vertices to delete (all test data).")
        return vertices
    except Error as e:
        logger.error(f"Error fetching vertices to delete: {str(e)}")
        return []
    finally:
        release_db_connection(conn)

def fetch_regions_to_delete():
    """Fetch all regions to delete (since all data is test data)."""
    query = """
        SELECT i_zn, i_rgn as i_reg, x_nm_rgn as x_nm_reg, i_trg as i_pnt_reg
        FROM regions
        ORDER BY i_zn;
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection.")
        return []
    try:
        cur = conn.cursor()
        cur.execute(query)
        regions = cur.fetchall()
        logger.info(f"Found {len(regions)} regions to delete (all test data).")
        return regions
    except Error as e:
        logger.error(f"Error fetching regions to delete: {str(e)}")
        return []
    finally:
        release_db_connection(conn)

def fetch_maps_to_delete():
    """Fetch all maps to delete (since all data is test data)."""
    query = """
        SELECT i_map, x_nm_map
        FROM maps
        ORDER BY i_map;
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection.")
        return []
    try:
        cur = conn.cursor()
        cur.execute(query)
        maps = cur.fetchall()
        logger.info(f"Found {len(maps)} maps to delete (all test data).")
        return maps
    except Error as e:
        logger.error(f"Error fetching maps to delete: {str(e)}")
        return []
    finally:
        release_db_connection(conn)

def delete_test_vertices():
    """Delete all vertices (since all data is test data)."""
    query = """
        DELETE FROM vertices;
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection.")
        return False
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        logger.info(f"Deleted all {cur.rowcount} vertices (all test data).")
        return True
    except Error as e:
        logger.error(f"Error deleting vertices: {str(e)}")
        conn.rollback()
        return False
    finally:
        release_db_connection(conn)

def delete_test_regions():
    """Delete all regions (since all data is test data)."""
    query = """
        DELETE FROM regions;
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection.")
        return False
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        logger.info(f"Deleted all {cur.rowcount} regions (all test data).")
        return True
    except Error as e:
        logger.error(f"Error deleting regions: {str(e)}")
        conn.rollback()
        return False
    finally:
        release_db_connection(conn)

def delete_test_zones():
    """Delete all zones (since all data is test data)."""
    query = """
        DELETE FROM zones;
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection.")
        return False
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        logger.info(f"Deleted all {cur.rowcount} zones (all test data).")
        return True
    except Error as e:
        logger.error(f"Error deleting zones: {str(e)}")
        conn.rollback()
        return False
    finally:
        release_db_connection(conn)

def delete_test_maps():
    """Delete all maps (since all data is test data)."""
    query = """
        DELETE FROM maps;
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection.")
        return False
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        logger.info(f"Deleted all {cur.rowcount} maps (all test data).")
        return True
    except Error as e:
        logger.error(f"Error deleting maps: {str(e)}")
        conn.rollback()
        return False
    finally:
        release_db_connection(conn)

def get_valid_input(prompt):
    """Get valid user input (numbers or 'all') with retry on invalid input."""
    while True:
        selection = input(prompt).strip().lower()
        if selection == 'all':
            return selection
        try:
            selected = [int(x.strip()) for x in selection.split(',') if x.strip()]
            if selected:
                return selected
        except (ValueError, IndexError) as e:
            logger.error(f"Invalid selection: {str(e)}")
            print("Invalid input. Please enter valid numbers (comma-separated) or 'all'.")
        print("Try again:")

def display_and_select_data(zones, vertices, regions, maps):
    """Display all data to delete and allow user selection with retry."""
    print("\n=== Full Data Cleanup (All Test Data) ===")
    print("Found the following data to delete (all test data). Select which to delete (or 'all' for all):")

    # Display zones
    if zones:
        print("\nZones to Delete (All Test Data):")
        for i, (i_zn, x_nm_zn, i_typ_zn, i_pnt_zn) in enumerate(zones, 1):
            print(f"{i}. Zone ID: {i_zn}, Name: {x_nm_zn}, Type: {i_typ_zn}, Parent: {i_pnt_zn or 'None'}")
    
    # Display vertices
    if vertices:
        print("\nVertices to Delete (All Test Data):")
        for i, (vertex_id, zone_id, x, y, z, order) in enumerate(vertices, 1):
            print(f"{len(zones) + i}. Vertex ID: {vertex_id}, Zone ID: {zone_id}, X: {x}, Y: {y}, Z: {z}, Order: {order}")
    
    # Display regions
    if regions:
        print("\nRegions to Delete (All Test Data):")
        for i, (i_zn, i_reg, x_nm_reg, i_pnt_reg) in enumerate(regions, 1):
            print(f"{len(zones) + len(vertices) + i}. Region ID: {i_reg}, Zone ID: {i_zn}, Name: {x_nm_reg}, Parent: {i_pnt_reg or 'None'}")

    # Display maps
    if maps:
        print("\nMaps to Delete (All Test Data):")
        for i, (i_map, x_nm_map) in enumerate(maps, 1):
            print(f"{len(zones) + len(vertices) + len(regions) + i}. Map ID: {i_map}, Name: {x_nm_map}")

    if not (zones or vertices or regions or maps):
        print("No data found to delete (database is already empty).")
        return []

    selection = get_valid_input("\nEnter numbers to delete (comma-separated, or 'all' for all): ")
    if selection == 'all':
        selected_ids = []
        if zones:
            selected_ids.extend([row[0] for row in zones])
        if vertices:
            selected_ids.extend([row[0] for row in vertices])
        if regions:
            selected_ids.extend([row[1] for row in regions])
        if maps:
            selected_ids.extend([row[0] for row in maps])
        return selected_ids

    selected = selection
    selected_ids = []
    offset = 0
    if zones:
        selected_ids.extend([zones[i-1-offset][0] for i in selected if i <= len(zones)])
        offset = len(zones)
    if vertices and offset < max(selected, default=0):
        selected_ids.extend([vertices[i-1-offset][0] for i in selected if i > offset and i <= offset + len(vertices)])
        offset += len(vertices)
    if regions and offset < max(selected, default=0):
        selected_ids.extend([regions[i-1-offset][1] for i in selected if i > offset and i <= offset + len(regions)])
        offset += len(regions)
    if maps and offset < max(selected, default=0):
        selected_ids.extend([maps[i-1-offset][0] for i in selected if i > offset])
    return selected_ids

def cleanup_test_data(selected_ids=None):
    """Clean up all data (since all data is test data)."""
    zones = fetch_zones_to_delete()
    zone_ids = [z[0] for z in zones] if zones else []
    vertices = fetch_vertices_to_delete() if not zone_ids else []
    regions = fetch_regions_to_delete() if not zone_ids else []
    maps = fetch_maps_to_delete() if not zone_ids else []

    if not (zones or vertices or regions or maps):
        logger.info("No data found to delete (database is already empty).")
        print("No data found to delete (database is already empty).")
        return

    if selected_ids is None:
        selected_ids = display_and_select_data(zones, vertices, regions, maps)
        if not selected_ids:
            print("No data selected for deletion. Exiting.")
            return

    # Delete in correct order: vertices, regions, zones, then maps
    success = True

    if zone_ids or maps:
        if not delete_test_vertices():
            success = False
        if not delete_test_regions():
            success = False
        if not delete_test_zones():
            success = False
        if not delete_test_maps():
            success = False

    if success:
        logger.info("Full data cleanup completed successfully (all test data removed).")
        print("Full data cleanup completed successfully (all test data removed).")
    else:
        logger.error("Data cleanup failed. Check logs for details.")
        print("Data cleanup failed. Check logs for details.")

if __name__ == "__main__":
    cleanup_test_data()