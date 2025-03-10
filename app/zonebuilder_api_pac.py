"""
Version: 250301 zonebuilder_api_pac.py Version 0P.6B.16g (Modified for ParcoRTLS)

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from flask import Flask, jsonify, request, Response, render_template  # Added render_template
from flask_cors import CORS
from api_modules.campus_l1 import campus_l1
from api_modules.building_outside_l2 import building_outside_l2
from api_modules.building_l3 import building_l3
from api_modules.floor_l4 import floor_l4
from api_modules.elevator_l4 import elevator_l4
from api_modules.wing_l5 import wing_l5
from api_modules.room_l6 import room_l6
from api_modules.hallway_l6 import hallway_l6
from api_modules.door_l6 import door_l6
from api_modules.get_maps import get_maps_bp
from api_modules.get_map import get_map_bp
from api_modules.get_map_metadata import get_map_metadata_bp
from api_modules.get_parent_zones import get_parent_zones_bp
from db_connection import get_db_connection, release_db_connection  # Using db_connection for now
import logging
import psycopg2
import sys  # Added for sys.stderr in prints
import traceback  # For stack tracing

# ✅ **Fix: Define Flask App Before Registering Routes**
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, resources={
    r"/get_*": {"origins": ["http://192.168.210.231:5004", "http://192.168.210.231:5012"]},  # Allow CORS for get endpoints from zonebuilder_ui and zoneviewer_ui
    r"/update_vertices": {"origins": ["http://192.168.210.231:5004", "http://192.168.210.231:5012"]}  # Allow CORS for update_vertices
})
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/zonebuilder_ui', methods=['GET'])
def serve_zonebuilder_ui():
    return render_template("zonebuilder_ui.html")

@app.route('/get_zone_types', methods=['GET'])
def get_zone_types():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cur = conn.cursor()
        # Use usp_zone_select_all() with filtering to get zone types
        cur.execute("""
            SELECT DISTINCT z.i_typ_zn, t.x_dsc_zn 
            FROM public.usp_zone_select_all() z 
            JOIN public.tlkzonetypes t ON z.i_typ_zn = t.i_typ_zn 
            ORDER BY z.i_typ_zn;
        """)
        zones = cur.fetchall()
        logger.info(f"Fetched zone types from usp_zone_select_all - type: {type(zones)}, value: {zones}")
        print(f"DEBUG: Fetched zone types from usp_zone_select_all - type: {type(zones)}, value: {zones}", file=sys.stderr)

        # Ensure zones is a list of tuples, even if it's a single tuple
        if isinstance(zones, tuple):
            zones = [zones]
            logger.info(f"Converted single tuple to list: {zones}")
            print(f"DEBUG: Converted single tuple to list: {zones}", file=sys.stderr)
        elif not isinstance(zones, (list, tuple)):
            logger.error(f"Unexpected type for zones: {type(zones)}")
            print(f"DEBUG: Unexpected type for zones: {type(zones)}", file=sys.stderr)
            return jsonify({'error': f"Unexpected type for zones: {type(zones)}"}), 500

        # Format to match the expected structure (zone_level, zone_name, api_endpoint)
        zone_list = []
        for z in zones:
            if len(z) >= 2:  # Ensure we have i_typ_zn and x_dsc_zn
                zone_list.append({
                    "zone_level": z[0],  # i_typ_zn
                    "zone_name": z[1],   # x_dsc_zn
                    "api_endpoint": "/create_zone"
                })

        logger.info(f"Formatted zone list - type: {type(zone_list)}, value: {zone_list}")
        print(f"DEBUG: Formatted zone list - type: {type(zone_list)}, value: {zone_list}", file=sys.stderr)
        return jsonify(zone_list), 200
    except psycopg2.Error as e:
        logger.error(f"Error fetching zone types: {str(e)}")
        print(f"DEBUG: Error fetching zone types: {str(e)}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/create_zone', methods=['POST'])
def create_zone():
    data = request.get_json()
    zone_name = data.get('zone_name')
    map_id = data.get('map_id')  # Optional, can be None or an integer
    zone_level = data.get('zone_level')
    parent_zone_id = data.get('parent_zone_id')
    vertices = data.get('vertices', [])

    if not all([zone_name, zone_level]):
        return jsonify({'error': 'Missing required fields (zone_name, zone_level)'}), 400

    try:
        zone_type = int(zone_level)
    except ValueError:
        return jsonify({'error': 'Invalid zone_level format'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cur = conn.cursor()
        # Use usp_zone_add to create the zone (returns i_zn, without map_id)
        cur.execute("""
            SELECT public.usp_zone_add(%s, %s, %s);
        """, (zone_type, zone_name, parent_zone_id))
        zone_id = cur.fetchone()[0]  # usp_zone_add returns the zone ID
        logger.info(f"✅ Created Zone ID: {zone_id} using usp_zone_add")

        # Handle map_id: validate it exists in maps or allow NULL
        if map_id is not None:
            try:
                map_id = int(map_id)  # Ensure map_id is an integer
                cur.execute("SELECT i_map FROM public.maps WHERE i_map = %s", (map_id,))
                if not cur.fetchone():
                    return jsonify({'error': f"Map ID {map_id} not found in maps table"}), 400
                # Update zones.i_map if map_id exists
                cur.execute("""
                    UPDATE public.zones SET i_map = %s WHERE i_zn = %s;
                """, (map_id, zone_id))
                logger.info(f"✅ Updated Zone ID {zone_id} with map_id {map_id}")
            except ValueError:
                return jsonify({'error': 'Invalid map_id format, must be an integer'}), 400
        else:
            logger.info("No map_id provided, i_map will be NULL in zones table")

        # Calculate min/max coordinates from vertices
        if vertices:
            x_coords = [float(v.get('n_x', 0)) for v in vertices]  # Ensure float for real type
            y_coords = [float(v.get('n_y', 0)) for v in vertices]
            z_coords = [float(v.get('n_z', 0)) for v in vertices]
            n_min_x = min(x_coords) if x_coords else 0.0
            n_max_x = max(x_coords) if x_coords else 0.0
            n_min_y = min(y_coords) if y_coords else 0.0
            n_max_y = max(y_coords) if y_coords else 0.0
            n_min_z = min(z_coords) if z_coords else 0.0
            n_max_z = max(z_coords) if z_coords else 0.0
        else:
            n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        # Use usp_region_add to create the region (returns i_rgn), with p_i_trg as NULL
        # Corrected parameter order: p_i_rgn, p_i_zn, p_x_nm_rgn, p_n_max_x, p_n_max_y, p_n_max_z, p_n_min_x, p_n_min_y, p_n_min_z, p_i_trg
        cur.execute("""
            SELECT public.usp_region_add(NULL, %s, %s, %s::real, %s::real, %s::real, %s::real, %s::real, %s::real, NULL);
        """, (zone_id, zone_name, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z))
        region_id = cur.fetchone()[0]  # usp_region_add returns the region ID
        logger.info(f"DEBUG: usp_region_add returned region_id: {region_id}")
        if region_id <= 0:
            raise psycopg2.Error(f"Invalid region_id {region_id} returned from usp_region_add")
        logger.info(f"✅ Created Region ID: {region_id} using usp_region_add")

        # Use usp_zone_vertices_add to add vertices (no return value, void), pass NULL for vertex_id
        if vertices:
            order = 1
            for vertex in vertices:
                cur.execute("""
                    SELECT public.usp_zone_vertices_add(NULL, %s::real, %s::real, %s::real, %s, %s);
                """, (vertex.get('n_x', 0.0), vertex.get('n_y', 0.0), vertex.get('n_z', 0.0), order, region_id))
                order += 1
                logger.info(f"✅ Added Vertex: {vertex} using usp_zone_vertices_add")
            logger.info(f"🔹 Vertices Data: {vertices}")

        conn.commit()
        return jsonify({'i_zn': zone_id, 'message': 'Zone created successfully'}), 201
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error creating zone: {str(e)}")
        print(f"DEBUG: Error creating zone: {str(e)}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_map/<int:map_id>', methods=['GET'])
def get_map(map_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cur = conn.cursor()
        cur.execute("SELECT img_data, x_format FROM maps WHERE i_map = %s", (map_id,))
        map_data = cur.fetchone()
        if not map_data:
            return jsonify({'error': 'Map not found'}), 404
        img_data, format = map_data
        return Response(img_data, mimetype=f'image/{format.lower()}')
    except psycopg2.Error as e:
        logger.error(f"Error fetching map: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_map_metadata/<int:map_id>', methods=['GET'])
def get_map_metadata(map_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT i_map, x_nm_map, min_x, min_y, max_x, max_y
            FROM maps WHERE i_map = %s
        """, (map_id,))
        map_data = cur.fetchone()
        if not map_data:
            return jsonify({'error': 'Map metadata not found'}), 404
        map_id, name, min_x, min_y, max_x, max_y = map_data
        return jsonify({
            'map_id': map_id,
            'name': name,
            'min_x': min_x,
            'min_y': min_y,
            'max_x': max_x,
            'max_y': max_y
        }), 200
    except psycopg2.Error as e:
        logger.error(f"Error fetching map metadata: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_all_zones_for_campus/<int:campus_id>', methods=['GET'])
def get_all_zones_for_campus(campus_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cur = conn.cursor()
        cur.execute("""
            WITH RECURSIVE zone_hierarchy AS (
                SELECT i_zn, x_nm_zn, i_typ_zn, i_pnt_zn, i_map
                FROM zones
                WHERE i_zn = %s
                UNION ALL
                SELECT z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn, z.i_map
                FROM zones z
                JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn
            )
            SELECT i_zn, x_nm_zn, i_typ_zn, i_pnt_zn, i_map
            FROM zone_hierarchy
            ORDER BY i_pnt_zn NULLS FIRST, i_zn;
        """, (campus_id,))
        zones = cur.fetchall()
        zone_map = {}
        for zone in zones:
            zone_id, zone_name, zone_type, parent_zone_id, map_id = zone
            zone_map[zone_id] = {
                'zone_id': zone_id,
                'zone_name': zone_name,
                'zone_type': zone_type,
                'parent_zone_id': parent_zone_id,
                'map_id': map_id,
                'children': []
            }
        result = []
        for zone_id, zone_data in zone_map.items():
            if zone_data['parent_zone_id'] is None:
                result.append(zone_data)
            else:
                parent = zone_map.get(zone_data['parent_zone_id'])
                if parent:
                    parent['children'].append(zone_data)
        return jsonify({'zones': result}), 200
    except psycopg2.Error as e:
        logger.error(f"Error fetching zones for campus: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_vertices_for_campus/<int:campus_id>', methods=['GET'])
def get_vertices_for_campus(campus_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cur = conn.cursor()
        cur.execute("""
            WITH RECURSIVE zone_hierarchy AS (
                SELECT i_zn FROM zones WHERE i_zn = %s
                UNION ALL
                SELECT z.i_zn FROM zones z
                JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn
            )
            SELECT v.i_vtx, v.n_x, v.n_y, v.n_z, v.n_ord, v.i_rgn, z.i_zn AS zone_id
            FROM vertices v
            JOIN regions r ON v.i_rgn = r.i_rgn
            JOIN zones z ON r.i_zn = z.i_zn
            JOIN zone_hierarchy zh ON z.i_zn = zh.i_zn
            ORDER BY v.i_rgn, v.n_ord;
        """, (campus_id,))
        vertices = cur.fetchall()
        result = {
            'vertices': [{
                'vertex_id': v[0],
                'x': v[1],
                'y': v[2],
                'z': v[3],
                'order': v[4],
                'region_id': v[5],
                'zone_id': v[6]
            } for v in vertices]
        }
        return jsonify(result), 200
    except psycopg2.Error as e:
        logger.error(f"Error fetching vertices for campus: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/update_vertices', methods=['POST'])
def update_vertices():
    data = request.get_json()
    vertices = data.get('vertices', [])
    if not vertices:
        return jsonify({'error': 'No vertices provided'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cur = conn.cursor()
        rows_affected = 0
        for vertex in vertices:
            try:
                cur.execute("""
                    UPDATE vertices
                    SET n_x = %s, n_y = %s, n_z = %s
                    WHERE i_vtx = %s;
                """, (vertex['x'], vertex['y'], vertex['z'], vertex['vertex_id']))
                rows_affected += cur.rowcount  # Track number of rows affected
            except KeyError as e:
                return jsonify({'error': f'Missing required field: {str(e)}'}), 400
            except (ValueError, TypeError) as e:
                return jsonify({'error': f'Invalid data format for vertex: {str(e)}'}), 400

        if rows_affected == 0:
            return jsonify({'error': 'No vertices found or updated'}), 404

        conn.commit()
        return jsonify({'message': 'Vertices updated successfully'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error updating vertices: {str(e)}")
        print(f"DEBUG: Error updating vertices: {str(e)}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

# Register Blueprints
app.register_blueprint(campus_l1)
app.register_blueprint(building_outside_l2)
app.register_blueprint(building_l3)
app.register_blueprint(floor_l4)
app.register_blueprint(elevator_l4)
app.register_blueprint(wing_l5)
app.register_blueprint(room_l6)
app.register_blueprint(hallway_l6)
app.register_blueprint(door_l6)
app.register_blueprint(get_maps_bp)
app.register_blueprint(get_map_bp)
app.register_blueprint(get_map_metadata_bp)
app.register_blueprint(get_parent_zones_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5012, debug=True)
    