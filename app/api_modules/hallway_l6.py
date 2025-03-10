from flask import Blueprint, request, jsonify
from api_modules.database import get_db_connection

hallway_l6 = Blueprint('hallway_l6', __name__)

@hallway_l6.route('/create_hallway_l6', methods=['POST'])
def create_hallway_l6():
    data = request.json
    zone_name = data.get('zone_name')
    parent_wing_id = data.get('parent_wing_id')
    min_z = data.get('min_z')
    max_z = data.get('max_z')
    vertices = data.get('vertices')

    if not (zone_name and parent_wing_id and min_z is not None and max_z is not None and vertices):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO zones (i_typ_zn, x_nm_zn, i_pnt_zn) VALUES (6, %s, %s) RETURNING i_zn", (zone_name, parent_wing_id))
        new_zone_id = cur.fetchone()[0]

        cur.execute("INSERT INTO regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING i_rgn",
                    (new_zone_id, zone_name, 
                     max(vertices, key=lambda v: v['x'])['x'], 
                     max(vertices, key=lambda v: v['y'])['y'], 
                     max_z, 
                     min(vertices, key=lambda v: v['x'])['x'], 
                     min(vertices, key=lambda v: v['y'])['y'], 
                     min_z))
        new_region_id = cur.fetchone()[0]

        for i, v in enumerate(vertices):
            cur.execute("INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn) VALUES (%s, %s, %s, %s, %s)", 
                        (v['x'], v['y'], min_z, i+1, new_region_id))
            cur.execute("INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn) VALUES (%s, %s, %s, %s, %s)", 
                        (v['x'], v['y'], max_z, i+5, new_region_id))

        conn.commit()
        return jsonify({'message': f'Hallway L6 "{zone_name}" created successfully!', 'region_id': new_region_id, 'zone_id': new_zone_id})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
