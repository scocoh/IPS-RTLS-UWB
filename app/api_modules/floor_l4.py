# Name: floor_l4.py
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
Version: 250216 floor_l4.py Version 0P.6B.3B

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from flask import Blueprint, request, jsonify
import psycopg2
from api_modules.database import get_db_connection

# Create Blueprint for Floor L4
floor_l4 = Blueprint('floor_l4', __name__)

@floor_l4.route('/create_floor_l4', methods=['POST'])
def create_floor_l4():
    data = request.json
    print("📌 Received Payload:", data)

    zone_name = data.get('zone_name')
    parent_zone_id = data.get('parent_zone_id')
    min_z = data.get('min_z', 0)  # Default Z-level to 0 if not provided
    max_z = data.get('max_z', 0)  # Default Z-level to 0 if not provided
    vertices = data.get('vertices')

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
        
        # ✅ Insert Zone (i_typ_zn = 3 for Floor L4)
        cur.execute("""
            INSERT INTO zones (i_typ_zn, x_nm_zn, i_pnt_zn)
            VALUES (3, %s, %s) RETURNING i_zn
        """, (zone_name, parent_zone_id))
        new_zone_id = cur.fetchone()[0]
        print(f"✅ Inserted Zone ID: {new_zone_id}")

        # ✅ Insert Region
        cur.execute("""
            INSERT INTO regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING i_rgn
        """, (
            new_zone_id,
            zone_name,
            max(v.get('n_x', 0) for v in vertices),  # n_max_x
            max(v.get('n_y', 0) for v in vertices),  # n_max_y
            max_z,  # n_max_z
            min(v.get('n_x', 0) for v in vertices),  # n_min_x
            min(v.get('n_y', 0) for v in vertices),  # n_min_y
            min_z   # n_min_z
        ))
        new_region_id = cur.fetchone()[0]
        print(f"✅ Inserted Region ID: {new_region_id}")

        # ✅ Insert Vertices
        for i, v in enumerate(vertices):
            cur.execute("""
                INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn)
                VALUES (%s, %s, %s, %s, %s)
            """, (v.get('n_x', 0), v.get('n_y', 0), min_z, i + 1, new_region_id))

        print(f"✅ Inserted {len(vertices)} vertices")

        conn.commit()

        print(f"🔹 Zone ID: {new_zone_id}")
        print(f"🔹 Region ID: {new_region_id}")
        print(f"🔹 Vertices Data: {vertices}")

        return jsonify({'message': f'Floor L4 "{zone_name}" created successfully!', 'region_id': new_region_id, 'zone_id': new_zone_id})

    except Exception as e:
        conn.rollback()
        print(f"❌ Database Error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
