"""
Version: 250303 zoneviewer_api_pac.py Version 0P.7B.60g (Modified for ParcoRTLS)

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from flask import Flask, jsonify, render_template, Response, request
from flask_cors import CORS  # Added for CORS support
from db_connection import get_db_connection, release_db_connection
import logging
import psycopg2
import sys  # Added for sys.stderr in prints
import json  # Added for JSON parsing (if needed for future ParcoRTLS functions)

app = Flask(__name__, template_folder="templates")
CORS(app, resources={  # Allow same-origin requests
    r"/get_*": {"origins": ["http://192.168.210.226:5014"]},
    r"/update_*": {"origins": ["http://192.168.210.226:5014"]},  # Allow POST for update endpoints
})
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/zoneviewer_ui_pac', methods=['GET'])
def serve_zoneviewer_ui():
    return render_template("zoneviewer_ui_pac.html")  # Changed to zoneviewer_ui_pac.html

@app.route('/get_campus_zones', methods=['GET'])
def get_campus_zones():
    # Get campus_id from query parameter, handle 'all' or specific ID
    campus_id = request.args.get('campus_id', type=str)  # Changed to str to handle 'all'
    logger.info(f"Fetching Campus Zones for campus_id {campus_id} (Version 0P.7B.60g)...")
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cur = conn.cursor()
        if campus_id == 'all':
            # Fetch all Campus L1 zones (zone_type = 1) and their hierarchies
            cur.execute("""
                SELECT i_zn FROM zones
                WHERE i_typ_zn = 1
                AND i_zn IS NOT NULL;
            """)
            campus_ids = [row[0] for row in cur.fetchall()]
            if not campus_ids:
                return jsonify({'zones': []}), 200

            all_zones = []
            for cid in campus_ids:
                cur.execute("""
                    SELECT public.usp_getallzonesforcampus(%s);
                """, (cid,))
                zones = cur.fetchone()[0]
                if zones:
                    # Handle JSONB or string response
                    if isinstance(zones, (str, bytes)):
                        try:
                            parsed = json.loads(zones) if isinstance(zones, str) else json.loads(zones.decode('utf-8'))
                            if 'zones' in parsed and parsed['zones']:
                                all_zones.extend(parsed['zones'])
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decoding error for campus_id {cid}: {str(e)}")
                    elif isinstance(zones, dict) and 'zones' in zones and zones['zones']:
                        all_zones.extend(zones['zones'])

            if not all_zones:
                return jsonify({'zones': []}), 200
            return jsonify({'zones': all_zones}), 200
        else:
            # Try to convert campus_id to integer for specific campus
            try:
                campus_id_int = int(campus_id)
                cur.execute("""
                    SELECT public.usp_getallzonesforcampus(%s);
                """, (campus_id_int,))
            except ValueError:
                logger.warning("Invalid campus_id format; returning empty zones as fallback (Version 0P.7B.60g)")
                return jsonify({'zones': []}), 200

        zones = cur.fetchone()[0]  # Assuming usp_getallzonesforcampus returns a JSONB object

        if not zones:
            return jsonify({'zones': []}), 200  # Return empty list if no zones found

        # Parse the result (assuming JSONB object with 'zones' key or array format)
        if isinstance(zones, (str, bytes)):
            zones = json.loads(zones) if isinstance(zones, str) else json.loads(zones.decode('utf-8'))
        
        # Ensure zones is structured as expected (object with 'zones' key or array)
        if isinstance(zones, dict) and 'zones' in zones:
            normalized_zones = zones['zones']
        elif isinstance(zones, list):
            normalized_zones = zones
        else:
            logger.error(f"Unexpected type for zones from usp_getallzonesforcampus: {type(zones)}")
            return jsonify({'error': 'Invalid data format from ParcoRTLS function'}), 500

        # Normalize the data structure to match expected fields (zone_id, name, etc.)
        def normalize_zone(zone):
            normalized = {
                'zone_id': zone.get('zone_id', zone.get('i_zn')),
                'name': zone.get('name', zone.get('zone_name', '')),
                'zone_type': zone.get('zone_type', 0),
                'parent_zone_id': zone.get('parent_zone_id', zone.get('i_pnt_zn')),
                'map_id': zone.get('map_id', zone.get('i_map')),
                'children': []
            }
            if 'children' in zone and zone['children']:
                normalized['children'] = [normalize_zone(child) for child in zone['children']]
            return normalized

        normalized_zones = [normalize_zone(zone) for zone in normalized_zones]

        # Build hierarchy (already handled by usp_getallzonesforcampus, but ensure consistency)
        logger.info(f"Returned {len(normalized_zones)} zones with map IDs and hierarchy from usp_getallzonesforcampus for campus_id {campus_id}.")
        print(f"DEBUG: Returned {len(normalized_zones)} zones with map IDs and hierarchy from usp_getallzonesforcampus for campus_id {campus_id} - type: {type(normalized_zones)}, value: {normalized_zones}", file=sys.stderr)
        return jsonify({'zones': normalized_zones}), 200  # Return structure matching non-pac version
    except psycopg2.Error as e:
        logger.error(f"Error fetching campus zones: {str(e)}")
        print(f"DEBUG: Error fetching campus zones: {str(e)}", file=sys.stderr)
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
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cur = conn.cursor()
        data = request.get_json()
        if not data or 'vertices' not in data:
            return jsonify({'error': 'No vertex data provided'}), 400

        vertices = data['vertices']
        for vertex in vertices:
            vertex_id = vertex.get('vertex_id')
            x = vertex.get('x')
            y = vertex.get('y')
            z = vertex.get('z')

            if not all([vertex_id, x, y]):
                return jsonify({'error': f'Missing required fields for vertex_id {vertex_id}'}), 400

            cur.execute("""
                UPDATE vertices
                SET n_x = %s, n_y = %s, n_z = %s
                WHERE i_vtx = %s;
            """, (x, y, z, vertex_id))

        conn.commit()
        logger.info(f"Updated {len(vertices)} vertices successfully.")
        return jsonify({'message': 'Vertices updated successfully'}), 200

    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error updating vertices: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5014, debug=True)