# Name: zoneviewer_api.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Version: 250227 zoneviewer_api.py Version 0P.6B.33i

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from flask import Flask, jsonify, render_template
from db_connection import get_db_connection, release_db_connection
import logging
import psycopg2

app = Flask(__name__, template_folder="templates")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/zoneviewer_ui', methods=['GET'])
def serve_zoneviewer_ui():
    return render_template("zoneviewer_ui.html")

@app.route('/get_campus_zones', methods=['GET'])
def get_campus_zones():
    logger.info("Fetching Campus Zones (Version 0P.6B.33i)...")
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cur = conn.cursor()
        # Fetch all zones, including i_map, ordered by hierarchy
        cur.execute("""
            SELECT z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn, z.i_map
            FROM zones z
            ORDER BY z.i_pnt_zn NULLS FIRST, z.i_zn;
        """)
        zones = cur.fetchall()

        # Process zones into campus structure (assuming Campus L1 as root)
        campuses = []
        zone_map = {}  # To build hierarchy
        for zone in zones:
            zone_id, zone_name, zone_type, parent_zone_id, map_id = zone
            zone_map[zone_id] = {
                'zone_id': zone_id,
                'map_id': map_id,
                'name': zone_name,
                'zone_type': zone_type,
                'parent_zone_id': parent_zone_id,
                'children': []
            }
            if zone_type == 1:  # Campus L1 (root campus)
                campuses.append(zone_map[zone_id])
            elif parent_zone_id is not None and parent_zone_id in zone_map:
                zone_map[parent_zone_id]['children'].append(zone_map[zone_id])

        # Ensure campuses is always a list, even if empty
        if not campuses:
            campuses = []

        logger.info(f"Returned {len(campuses)} campuses with map IDs and hierarchy.")
        return jsonify(campuses), 200
    except psycopg2.Error as e:
        logger.error(f"Error fetching campus zones: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)