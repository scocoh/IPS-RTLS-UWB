"""
Version: 250220 campus_l1.py Version 0P.6B.3E

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

# Create Blueprint for this module
campus_l1 = Blueprint('campus_l1', __name__)

@campus_l1.route('/create_campus_l1', methods=['POST'])
def create_campus_l1():
    data = request.json
    print("📌 Received Payload:", data)

    zone_name = data.get('zone_name')
    map_id = data.get('map_id')
    vertices = data.get('vertices')

    if not (zone_name and map_id and vertices):
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

        # ✅ **Insert Zone**
        cur.execute("""
            INSERT INTO zones (i_typ_zn, x_nm_zn)
            VALUES (1, %s) RETURNING i_zn
        """, (zone_name,))
        new_zone_id = cur.fetchone()[0]
        print(f"✅ Inserted Zone ID: {new_zone_id}")

        # ✅ **Insert Region**
        cur.execute("""
            INSERT INTO regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING i_rgn
        """, (
            new_zone_id,
            zone_name,
            max(v['n_x'] for v in vertices),  # n_max_x
            max(v['n_y'] for v in vertices),  # n_max_y
            max(v.get('n_z', 0) for v in vertices),  # n_max_z
            min(v['n_x'] for v in vertices),  # n_min_x
            min(v['n_y'] for v in vertices),  # n_min_y
            min(v.get('n_z', 0) for v in vertices)  # n_min_z
        ))
        new_region_id = cur.fetchone()[0]
        print(f"✅ Inserted Region ID: {new_region_id}")

        # ✅ **Insert Vertices**
        for i, v in enumerate(vertices):
            cur.execute("""
                INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn)
                VALUES (%s, %s, %s, %s, %s)
            """, (v['n_x'], v['n_y'], v.get('n_z', 0), i + 1, new_region_id))

        print(f"✅ Inserted {len(vertices)} vertices")

        conn.commit()

        # ✅ **Move Debugging Print Statements Here**
        print(f"🔹 Zone ID: {new_zone_id}")
        print(f"🔹 Region ID: {new_region_id}")
        print(f"🔹 Vertices Data: {vertices}")

        return jsonify({
            'message': f'Campus L1 "{zone_name}" created successfully!',
            'region_id': new_region_id,
            'zone_id': new_zone_id
        })

    except Exception as e:
        conn.rollback()
        print(f"❌ Database Error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
