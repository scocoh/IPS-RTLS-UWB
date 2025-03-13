"""/home/parcoadmin/parco_fastapi/app/api_modules/get_zone_data_l3.py
"""
import psycopg2
import json
from flask import Blueprint, request, jsonify
from api_modules.database import get_db_connection

get_zone_data_l3 = Blueprint('get_zone_data_l3', __name__)

@get_zone_data_l3.route('/get_zone_data_l3', methods=['GET'])
def get_zone_data():
    """ Fetch Campus L1 Map and L2 Zone Vertices from ParcoRTLSMaint """
    
    zone_id = request.args.get('zone_id')
    
    if not zone_id:
        return jsonify({"error": "Missing zone_id parameter"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ Explicitly set schema to public
        cur.execute("SET search_path TO public;")

        # ✅ Fetch Campus L1 Map and L2 Zone Vertices
        cur.execute("""
            SELECT m.map_file, z.vertices 
            FROM public.maps m
            JOIN public.zones z ON m.i_pnt_zn = z.i_zn  -- ✅ Use i_zn (zone ID)
            WHERE z.i_zn = %s
        """, (zone_id,))

        row = cur.fetchone()

        if not row:
            return jsonify({"error": "Zone ID not found"}), 404

        map_file, vertices = row

        # 🔹 Close connection
        cur.close()
        conn.close()

        return jsonify({
            "map_file": map_file,
            "vertices": json.loads(vertices)  # Ensure JSON format
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
