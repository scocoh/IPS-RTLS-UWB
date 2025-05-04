# Name: upload_map_coordinates.py
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

from flask import Flask, request, jsonify
from db_connection import get_db_connection

app = Flask(__name__)

def compute_map_coordinates(p1_pixel_x, p1_pixel_y, p2_pixel_x, p2_pixel_y, p1_real_x, p1_real_y, p2_real_x, p2_real_y, canvas_width, canvas_height):
    """ Computes the min_x, min_y, max_x, and max_y for storing into the database """
    dx_pixels = p2_pixel_x - p1_pixel_x
    dy_pixels = p1_pixel_y - p2_pixel_y  # Image coordinates (top-left origin)
    
    dx_real = p2_real_x - p1_real_x
    dy_real = p2_real_y - p1_real_y
    
    s_x = dx_pixels / dx_real
    s_y = dy_pixels / dy_real
    
    Q1 = p1_pixel_x / s_x
    min_x = p1_real_x - Q1
    
    Q2 = -abs(p1_pixel_y / s_y)
    min_y = Q2 - p1_real_y
    
    max_x = canvas_width / s_x
    max_y = canvas_height / s_y
    
    return min_x, min_y, max_x, max_y

def store_map_coordinates(map_name, min_x, min_y, max_x, max_y):
    """ Stores the computed map coordinates into the database """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO maps (map_name, min_x, min_y, max_x, max_y)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (map_name) DO UPDATE
            SET min_x = EXCLUDED.min_x, min_y = EXCLUDED.min_y, max_x = EXCLUDED.max_x, max_y = EXCLUDED.max_y;
        """, (map_name, min_x, min_y, max_x, max_y))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False

@app.route('/scaling_upload', methods=['POST'])
def scaling_upload():
    data = request.json
    
    map_name = data['map_name']
    p1_pixel_x = data['p1_pixel_x']
    p1_pixel_y = data['p1_pixel_y']
    p2_pixel_x = data['p2_pixel_x']
    p2_pixel_y = data['p2_pixel_y']
    p1_real_x = data['p1_real_x']
    p1_real_y = data['p1_real_y']
    p2_real_x = data['p2_real_x']
    p2_real_y = data['p2_real_y']
    canvas_width = data['canvas_width']
    canvas_height = data['canvas_height']
    
    min_x, min_y, max_x, max_y = compute_map_coordinates(
        p1_pixel_x, p1_pixel_y, p2_pixel_x, p2_pixel_y,
        p1_real_x, p1_real_y, p2_real_x, p2_real_y,
        canvas_width, canvas_height
    )
    
    success = store_map_coordinates(map_name, min_x, min_y, max_x, max_y)
    
    if success:
        return jsonify({"message": "Map coordinates uploaded successfully", "min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}), 200
    else:
        return jsonify({"message": "Error storing map coordinates"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
