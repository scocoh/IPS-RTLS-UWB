"""
Version: 250216 room_l6.py Version 0P.6B.3B

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from flask import Blueprint, request, jsonify
from api_modules.database import get_db_connection

room_l6 = Blueprint('room_l6', __name__)

@room_l6.route('/create_room_l6', methods=['POST'])
def create_room_l6():
    data = request.json
    print("📌 Received Payload:", data)  # Debugging

    zone_name = data.get('zone_name')
    parent_zone_id = data.get('parent_zone_id')  # ✅ Fixed naming
    vertices = data.get('vertices')

    print(f"🛠️ Zone Name: {zone_name}")
    print(f"🛠️ Parent Zone ID: {parent_zone_id}")
    print(f"🛠️ Vertices: {vertices}")

    if not (zone_name and parent_zone_id and vertices):
        print("❌ ERROR: Missing required fields")
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 🔍 **Check if the zone already exists**
        cur.execute("SELECT i_zn FROM zones WHERE x_nm_zn = %s", (zone_name,))
        existing_zone = cur.fetchone()

        if existing_zone:
            print(f"⚠️ Zone '{zone_name}' already exists! Skipping insertion.")
            return jsonify({
                'error': f'Zone "{zone_name}" already exists!',
                'zone_id': existing_zone[0]
            }), 400
        
        # ✅ Insert into `zones` for Room L6
        cur.execute("""
            INSERT INTO zones (i_typ_zn, x_nm_zn, i_pnt_zn)
            VALUES (5, %s, %s) RETURNING i_zn
        """, (zone_name, parent_zone_id))
        new_zone_id = cur.fetchone()[0]
        print(f"✅ Inserted Zone ID: {new_zone_id}")

        # ✅ Insert into `regions`
        cur.execute("""
            INSERT INTO regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z)
            VALUES (%s, %s, %s, %s, 0, %s, %s, 0) RETURNING i_rgn
        """, (
            new_zone_id,
            zone_name,
            max(v['n_x'] for v in vertices),  # n_max_x
            max(v['n_y'] for v in vertices),  # n_max_y
            min(v['n_x'] for v in vertices),  # n_min_x
            min(v['n_y'] for v in vertices)   # n_min_y
        ))
        new_region_id = cur.fetchone()[0]
        print(f"✅ Inserted Region ID: {new_region_id}")

        # ✅ Insert into `vertices`
        for i, v in enumerate(vertices):
            cur.execute("""
                INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn)
                VALUES (%s, %s, 0, %s, %s)
            """, (v['n_x'], v['n_y'], i + 1, new_region_id))
            print(f"✅ Inserted Vertex: {v}")

        conn.commit()
        print(f"🚀 Room L6 '{zone_name}' successfully created!")
        return jsonify({'message': f'Room L6 "{zone_name}" created successfully!', 'region_id': new_region_id, 'zone_id': new_zone_id})

    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        cur.close()
        conn.close()
