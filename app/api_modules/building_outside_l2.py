# Name: building_outside_l2.py
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
Version: 250216 building_outside_l2.py Version 0P.6B.3B

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
building_outside_l2 = Blueprint('building_outside_l2', __name__)

# ✅ Create a Building Outside (L2)
@building_outside_l2.route('/create_building_outside_l2', methods=['POST'])
def create_building_outside_l2():
    data = request.json
    print("📌 Received Payload:", data)  # <-- Debugging
    zone_name = data.get('zone_name')
    parent_zone_id = data.get('parent_zone_id')
    vertices = data.get('vertices')

    # Debugging print
    print(f"🛠️ zone_name: {zone_name}")
    print(f"🛠️ parent_zone_id: {parent_zone_id}")
    print(f"🛠️ vertices: {vertices}")

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
        
        # 🔍 **Check if the zone already exists**
        cur.execute("SELECT i_zn FROM zones WHERE x_nm_zn = %s", (zone_name,))
        existing_zone = cur.fetchone()

        if existing_zone:
            print(f"⚠️ Zone '{zone_name}' already exists! Skipping insertion.")
            return jsonify({
                'error': f'Zone "{zone_name}" already exists!',
                'zone_id': existing_zone[0]
            }), 400
        
        # ✅ Insert Zone (Corrected i_typ_zn to 2 for L2 zones)
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
            max(v.get('n_z', 0) for v in vertices),  # n_max_z
            min(v.get('n_x', 0) for v in vertices),  # n_min_x
            min(v.get('n_y', 0) for v in vertices),  # n_min_y
            min(v.get('n_z', 0) for v in vertices)   # n_min_z
        ))
        new_region_id = cur.fetchone()[0]

        # ✅ Insert Vertices (Ensure correct key names and log insertions)
        for i, v in enumerate(vertices):
            cur.execute("""
                INSERT INTO vertices (n_x, n_y, n_z, n_ord, i_rgn)
                VALUES (%s, %s, %s, %s, %s)
            """, (v.get('n_x', 0), v.get('n_y', 0), v.get('n_z', 0), i + 1, new_region_id))
            print(f"✅ Inserted Vertex: {v}")

        conn.commit()
        return jsonify({'message': f'Building Outside L2 "{zone_name}" created successfully!', 'region_id': new_region_id, 'zone_id': new_zone_id})

    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
