"""
Version: 250304 fetch_vertices.py Version 0P.1B.02 (Get the Vertices in JSON)

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24, Michael Farnsworth, and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""
from sqlalchemy import create_engine, text
import json

# Database connection
DATABASE_URL = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint"
engine = create_engine(DATABASE_URL)

def get_vertices():
    # Correcting the table name from "vertices_table" to "vertices"
    query = text("SELECT i_vtx, n_x, n_y, n_z, i_rgn FROM vertices")  

    with engine.connect() as conn:
        result = conn.execute(query)
        vertices = [{"id": row[0], "x": row[1], "y": row[2], "z": row[3], "region": row[4]} for row in result]

    return vertices

if __name__ == "__main__":
    vertices = get_vertices()
    print(json.dumps(vertices, indent=4))  # Outputs vertices in JSON format
