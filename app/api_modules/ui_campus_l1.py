from flask import Blueprint, request, jsonify
from db_connection import get_db_connection

campus_l1 = Blueprint('campus_l1', __name__)

@campus_l1.route('/create_campus_l1', methods=['POST'])
def create_campus_l1():
    data = request.json
    map_id = data.get('map_id')
    zone_name = data.get('zone_name')

    if not (map_id and zone_name):
        return jsonify({'error': 'Map ID and Zone Name are required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insert into zones table and get the new zone ID
        cur.execute("INSERT INTO zones (i_typ_zn, x_nm_zn) VALUES (1, %s) RETURNING i_zn", (zone_name,))
        new_zone_id = cur.fetchone()[0]

        # Fetch the min/max values from the maps table
        cur.execute("SELECT min_x, min_y, min_z, max_x, max_y, max_z FROM maps WHERE i_map = %s", (map_id,))
        map_data = cur.fetchone()

        if not map_data:
            conn.rollback()
            return jsonify({'error': 'Map not found'}), 400

        min_x, min_y, min_z, max_x, max_y, max_z = map_data

        # Insert into regions table using the min/max values from the map
        cur.execute("""
            INSERT INTO regions (i_zn, x_nm_rgn, n_min_x, n_min_y, n_min_z, n_max_x, n_max_y, n_max_z)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING i_rgn
        """, (new_zone_id, zone_name, min_x, min_y, min_z, max_x, max_y, max_z))

        new_region_id = cur.fetchone()[0]

        conn.commit()
        return jsonify({
            'message': f'Campus L1 "{zone_name}" created successfully!',
            'region_id': new_region_id,
            'zone_id': new_zone_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
