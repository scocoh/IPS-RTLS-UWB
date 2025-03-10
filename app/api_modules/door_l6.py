from flask import Blueprint, request, jsonify
from api_modules.database import get_db_connection

door_l6 = Blueprint('door_l6', __name__)

@door_l6.route('/create_door_l6', methods=['POST'])
def create_door_l6():
    data = request.json
    zone_name = data.get('zone_name')
    parent_wing_id = data.get('parent_wing_id')
    position = data.get('position')

    if not (zone_name and parent_wing_id and position):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insert zone
        cur.execute("INSERT INTO zones (i_typ_zn, x_nm_zn, i_pnt_zn) VALUES (6, %s, %s) RETURNING i_zn", 
                    (zone_name, parent_wing_id))
        new_zone_id = cur.fetchone()[0]

        # Insert region
        cur.execute("INSERT INTO regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING i_rgn",
                    (new_zone_id, zone_name, position['x'], position['y'], position['z'], position['x'], position['y'], position['z']))
        new_region_id = cur.fetchone()[0]

        # Insert single vertex (location of door)
        cur.execute("INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn) VALUES (%s, %s, %s, %s, %s)",
                    (position['x'], position['y'], position['z'], 1, new_region_id))

        conn.commit()
        return jsonify({'message': f'Door L6 "{zone_name}" created successfully!', 'region_id': new_region_id, 'zone_id': new_zone_id})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
