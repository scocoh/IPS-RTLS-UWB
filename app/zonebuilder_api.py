"""
Version: 250227 zonebuilder_api.py Version 0P.6B.1N
/home/parcoadmin/parco_fastapi/app/zonebuilder_api.py
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
from db_connection import get_db_connection, release_db_connection
import logging
import psycopg2

# ✅ **Fix: Define Flask App Before Registering Routes**
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, resources={
    r"/get_*": {"origins": "http://192.168.210.231:5004"},  # Allow CORS for get endpoints from zoneviewer_ui
    r"/update_vertices": {"origins": "http://192.168.210.231:5004"}  # Allow CORS for update_vertices from zoneviewer_ui
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
    cur = conn.cursor()

    cur.execute("SELECT i_typ_zn, x_dsc_zn FROM tlkzonetypes ORDER BY i_typ_zn;")
    zones = cur.fetchall()

    api_mapping = {
        1: "/create_zone",
        2: "/create_zone",
        3: "/create_zone",
        4: "/create_zone",
        5: "/create_zone",
        10: "/create_zone"
    }

    zone_list = []
    for z in zones:
        zone_list.append({
            "zone_level": z[0],
            "zone_name": z[1],
            "api_endpoint": api_mapping.get(z[0], "/create_zone")
        })

    cur.close()
    release_db_connection(conn)

    return jsonify(zone_list)

@app.route('/create_zone', methods=['POST'])
def create_zone():
    data = request.get_json()
    zone_name = data.get('zone_name')
    map_id = data.get('map_id')
    zone_level = data.get('zone_level')
    parent_zone_id = data.get('parent_zone_id')
    vertices = data.get('vertices', [])

    if not all([zone_name, map_id, zone_level]):
        return jsonify({'error': 'Missing required fields (zone_name, map_id, zone_level)'}), 400

    try:
        zone_type = int(zone_level)
    except ValueError:
        return jsonify({'error': 'Invalid zone_level format'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO zones (x_nm_zn, i_typ_zn, i_pnt_zn, i_map)
            VALUES (%s, %s, %s, %s)
            RETURNING i_zn;
        """, (zone_name, zone_type, parent_zone_id, map_id))
        zone_id = cur.fetchone()[0]
        logger.info(f"✅ Inserted Zone ID: {zone_id}")

        # Calculate min/max coordinates from vertices
        if vertices:
            x_coords = [v.get('n_x', 0) for v in vertices]
            y_coords = [v.get('n_y', 0) for v in vertices]
            z_coords = [v.get('n_z', 0) for v in vertices]  # Add Z coordinates
            n_min_x = min(x_coords) if x_coords else 0
            n_max_x = max(x_coords) if x_coords else 0
            n_min_y = min(y_coords) if y_coords else 0
            n_max_y = max(y_coords) if y_coords else 0
            n_min_z = min(z_coords) if z_coords else 0  # Default to 0 if no Z values
            n_max_z = max(z_coords) if z_coords else 0  # Default to 0 if no Z values
        else:
            n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z = 0, 0, 0, 0, 0, 0

        cur.execute("""
            INSERT INTO regions (i_zn, x_nm_rgn, n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING i_rgn;
        """, (zone_id, zone_name, n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z))
        region_id = cur.fetchone()[0]
        logger.info(f"✅ Inserted Region ID: {region_id}")

        if vertices:
            order = 1
            for vertex in vertices:
                cur.execute("""
                    INSERT INTO vertices (i_rgn, n_x, n_y, n_z, n_ord)
                    VALUES (%s, %s, %s, %s, %s);
                """, (region_id, vertex.get('n_x', 0), vertex.get('n_y', 0), vertex.get('n_z', 0), order))
                order += 1
                logger.info(f"✅ Inserted Vertex: {vertex}")
            logger.info(f"🔹 Vertices Data: {vertices}")

        logger.info(f"🔹 Zone ID: {zone_id}")
        logger.info(f"🔹 Region ID: {region_id}")

        conn.commit()
        return jsonify({'i_zn': zone_id, 'message': 'Zone created successfully'}), 201
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error creating zone: {str(e)}")
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
        for vertex in vertices:
            cur.execute("""
                UPDATE vertices
                SET n_x = %s, n_y = %s, n_z = %s
                WHERE i_vtx = %s;
            """, (vertex['x'], vertex['y'], vertex['z'], vertex['vertex_id']))
        conn.commit()
        return jsonify({'message': 'Vertices updated successfully'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error updating vertices: {str(e)}")
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
    app.run(host='0.0.0.0', port=5002, debug=True)