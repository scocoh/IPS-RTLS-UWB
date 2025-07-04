# Name: fetch_vertices_to_svg.py
# Version: 0.1.1
# Created: 971201
# Modified: 250704
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Version: 250304 fetch_vertices_to_svg.py Version 0P.1B.03 (Fetch, Normalize, and Convert to SVG)

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24, Michael Farnsworth, and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import json
import sys
import os
from sqlalchemy import create_engine, text

# Import centralized configuration
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_db_configs_sync

# Database connection
db_configs = get_db_configs_sync()
maint_config = db_configs['maint']
DATABASE_URL = f"postgresql://{maint_config['user']}:{maint_config['password']}@{maint_config['host']}:{maint_config['port']}/{maint_config['database']}"
engine = create_engine(DATABASE_URL)

def prompt_step(message):
    """
    Prompt user to Proceed (P) or Stop (S)
    """
    while True:
        choice = input(f"{message} (P to proceed, S to stop): ").strip().upper()
        if choice == "P":
            return True
        elif choice == "S":
            print("Process stopped by user.")
            exit()
        else:
            print("Invalid input. Please enter P to proceed or S to stop.")

def get_vertices():
    """
    Fetch vertex data from the database.
    """
    print("\nFetching vertices from the database...")
    query = text("SELECT i_vtx, n_x, n_y, n_z, i_rgn FROM vertices")  
    with engine.connect() as conn:
        result = conn.execute(query)
        vertices = [{"id": row[0], "x": row[1], "y": row[2], "z": row[3], "region": row[4]} for row in result]
    print(f"Fetched {len(vertices)} vertices.")
    return vertices

def normalize_coordinates(vertices, width=1000, height=800):
    """
    Normalize real-world coordinates to fit an SVG coordinate system.
    - X-axis is scaled within `width`
    - Y-axis is flipped and scaled within `height`
    """
    print("\nNormalizing coordinates...")
    min_x = min(v["x"] for v in vertices)
    min_y = min(v["y"] for v in vertices)
    max_x = max(v["x"] for v in vertices)
    max_y = max(v["y"] for v in vertices)

    scale_x = width / (max_x - min_x) if max_x - min_x else 1
    scale_y = height / (max_y - min_y) if max_y - min_y else 1

    for v in vertices:
        v["x"] = (v["x"] - min_x) * scale_x
        v["y"] = height - (v["y"] - min_y) * scale_y  # Flip Y-axis

    print("Coordinates normalized.")
    return vertices

def group_by_region(vertices):
    """
    Group vertices by region to create polygons.
    """
    print("\nGrouping vertices into regions...")
    regions = {}
    for v in vertices:
        if v["region"] not in regions:
            regions[v["region"]] = []
        regions[v["region"]].append((v["x"], v["y"]))
    
    print(f"Grouped into {len(regions)} regions.")
    return regions

def create_svg(regions, output_file="map.svg"):
    """
    Generate an SVG file from grouped regions.
    """
    print("\nGenerating SVG file...")

    svg_header = '<svg width="1000" height="800" xmlns="http://www.w3.org/2000/svg">\n'
    svg_footer = '</svg>'
    svg_content = ""

    for region, points in regions.items():
        points_str = " ".join([f"{x},{y}" for x, y in points])

        # Draw the polygon
        svg_content += f'<polygon points="{points_str}" fill="rgba(173, 216, 230, 0.6)" stroke="black" stroke-width="2"/>\n'

        # Compute centroid for labeling
        centroid_x = sum(x for x, y in points) / len(points)
        centroid_y = sum(y for x, y in points) / len(points)

        # Add text label
        svg_content += f'<text x="{centroid_x}" y="{centroid_y}" font-size="14" fill="black">Region {region}</text>\n'

    # Save to file
    svg_map = svg_header + svg_content + svg_footer
    with open(output_file, "w") as f:
        f.write(svg_map)

    print(f"SVG map saved as {output_file}")

# ---------------------------------
#           MAIN PROCESS
# ---------------------------------
if __name__ == "__main__":
    print("Starting fetch_vertices_to_svg.py")

    # Step 1: Fetch Vertices
    if prompt_step("Step 1: Fetch vertices from database?"):
        vertices = get_vertices()
    
    # Step 2: Normalize Coordinates
    if prompt_step("Step 2: Normalize coordinates for SVG?"):
        vertices = normalize_coordinates(vertices)

    # Step 3: Group by Regions
    if prompt_step("Step 3: Group vertices into regions?"):
        regions = group_by_region(vertices)

    # Step 4: Generate SVG
    if prompt_step("Step 4: Generate SVG file?"):
        create_svg(regions)

    print("\n✅ Process completed successfully!")