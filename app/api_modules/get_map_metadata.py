# Name: get_map_metadata.py
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

# Version: 250218 get_map_metadata.py Version 0P.6B.3J
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
#
# 🔥 FIXED: Corrected field order to align with DB schema
# 🔥 FIXED: Changed incorrect JSON response keys to match frontend expectations
# 🔥 FIXED: Min/max values were misaligned (fixed indexing)

from flask import Blueprint, jsonify
from db_connection import get_db_connection

# ✅ Blueprint for handling map metadata requests
get_map_metadata_bp = Blueprint("get_map_metadata", __name__)

@get_map_metadata_bp.route('/get_map_metadata/<int:map_id>', methods=['GET'])
def get_map_metadata(map_id):
    """
    Retrieves map metadata (min_x, min_y, max_x, max_y) for a given map_id.
    Fixes incorrect field mappings that caused pixel-to-feet conversion errors.
    """
    print(f"[INFO] get_map_metadata.py Version 0P.6B.3J called for map_id: {map_id}")
    
    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ Corrected SQL Query and Field Order
    cur.execute("""
        SELECT min_x, min_y, max_x, max_y, x_nm_map 
        FROM maps 
        WHERE i_map = %s
    """, (map_id,))
    
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        metadata = {
            "min_x": row[0],  # ✅ Correct order
            "min_y": row[1],
            "max_x": row[2],
            "max_y": row[3],
            "map_id": map_id,
            "name": row[4]
        }
        print(f"[INFO] Map metadata retrieved: {metadata}")
        return jsonify(metadata)
    
    print(f"[ERROR] Map ID {map_id} not found in database.")
    return jsonify({"error": "Map not found"}), 404
