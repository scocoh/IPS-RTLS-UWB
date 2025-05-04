# Name: elevator_l4.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/api_modules
# Role: Backend
# Status: Active
# Dependent: TRUE

from flask import Blueprint, request, jsonify
from api_modules.database import get_db_connection

elevator_l4 = Blueprint('elevator_l4', __name__)

@elevator_l4.route('/create_elevator_l4', methods=['POST'])
def create_elevator_l4():
    data = request.json
    zone_name = data.get('zone_name')
    parent_building_id = data.get('parent_building_id')
    position = data.get('position')
    min_z = data.get('min_z')
    max_z = data.get('max_z')

    if not (zone_name and parent_building_id and position and min_z is not None and max_z is not None):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insert zone
        cur.execute("INSERT INTO zones (i_typ_zn, x_nm_zn, i_pnt_zn) VALUES (4, %s, %s) RETURNING i_zn", 
                    (zone_name, parent_building_id))
        new_zone_id = cur.fetchone()[0]

        # Insert region
        cur.execute("INSERT INTO regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING i_rgn",
                    (new_zone_id, zone_name, position['x'], position['y'], max_z, position['x'], position['y'], min_z))
        new_region_id = cur.fetchone()[0]

        # Insert single vertex (location of elevator shaft)
        cur.execute("INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn) VALUES (%s, %s, %s, %s, %s)",
                    (position['x'], position['y'], min_z, 1, new_region_id))

        cur.execute("INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn) VALUES (%s, %s, %s, %s, %s)",
                    (position['x'], position['y'], max_z, 2, new_region_id))

        conn.commit()
        return jsonify({'message': f'Elevator L4 "{zone_name}" created successfully!', 'region_id': new_region_id, 'zone_id': new_zone_id})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
