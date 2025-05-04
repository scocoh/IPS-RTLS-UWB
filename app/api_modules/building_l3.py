# Name: building_l3.py
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

"""
Version: 250216 building_l3.py Version 0P.6B.3B

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from flask import Blueprint, request, jsonify
from api_modules.database import get_db_connection

building_l3 = Blueprint('building_l3', __name__)

@building_l3.route('/create_building_l3', methods=['POST'])
def create_building_l3():
    data = request.json
    print("📌 Received Payload:", data)

    zone_name = data.get('zone_name')
    map_id = data.get('map_id')
    parent_zone_id = data.get('parent_zone_id')
    vertices = data.get('vertices')

    # Ensure min_z and max_z have default values if not provided
    min_z = data.get('min_z', 0)
    max_z = data.get('max_z', 0)

    if not (zone_name and map_id and parent_zone_id and vertices):
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
        
        # ✅ Insert Zone (i_typ_zn = 2 for Building L3)
        cur.execute("""
            INSERT INTO zones (i_typ_zn, x_nm_zn, i_pnt_zn)
            VALUES (2, %s, %s) RETURNING i_zn
        """, (zone_name, parent_zone_id))
        new_zone_id = cur.fetchone()[0]

        # ✅ Insert Region
        cur.execute("""
            INSERT INTO regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING i_rgn
        """, (
            new_zone_id,
            zone_name,
            max(v.get('n_x', 0) for v in vertices),  # n_max_x
            max(v.get('n_y', 0) for v in vertices),  # n_max_y
            max(v.get('n_z', min_z) for v in vertices),  # n_max_z
            min(v.get('n_x', 0) for v in vertices),  # n_min_x
            min(v.get('n_y', 0) for v in vertices),  # n_min_y
            min(v.get('n_z', min_z) for v in vertices)  # n_min_z
        ))
        new_region_id = cur.fetchone()[0]

        # ✅ Insert Vertices (Ensuring correct key names)
        for i, v in enumerate(vertices):
            cur.execute("""
                INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn)
                VALUES (%s, %s, %s, %s, %s)
            """, (v.get('n_x', 0), v.get('n_y', 0), v.get('n_z', min_z), i + 1, new_region_id))
            print(f"✅ Inserted Vertex: {v}")

        conn.commit()
        return jsonify({'message': f'Building L3 "{zone_name}" created successfully!', 'region_id': new_region_id, 'zone_id': new_zone_id})

    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
