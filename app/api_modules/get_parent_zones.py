# Name: get_parent_zones.py
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
/home/parcoadmin/parco_fastapi/app/api_modules/get_parent_zones.py
Version: 250212 get_parent_zone.py Version 0P.6B.1A
ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""
from flask import Blueprint, jsonify
from db_connection import get_db_connection

get_parent_zones_bp = Blueprint("get_parent_zones", __name__)

@get_parent_zones_bp.route('/get_parent_zones', methods=['GET'])
def get_parent_zones():
    """ Fetch all existing zones to be used as parent zones """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT i_zn, x_nm_zn FROM zones ORDER BY i_zn")
    zones = [{"zone_id": row[0], "name": row[1]} for row in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({"zones": zones})
