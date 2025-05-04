# Name: get_maps.py
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

from flask import Blueprint, jsonify
from db_connection import get_db_connection

get_maps_bp = Blueprint('get_maps', __name__)

@get_maps_bp.route('/get_maps', methods=['GET'])
def get_maps():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fix: Use correct column names `i_map` as `map_id` and `x_nm_map` as `name`
    cur.execute("SELECT i_map AS map_id, x_nm_map AS name FROM maps")
    
    maps = [{"map_id": row[0], "name": row[1]} for row in cur.fetchall()]
    
    cur.close()
    conn.close()

    return jsonify({"maps": maps})
