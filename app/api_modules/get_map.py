from flask import Blueprint, jsonify, Response
from db_connection import get_db_connection
import io

get_map_bp = Blueprint("get_map", __name__)

@get_map_bp.route('/get_map/<int:map_id>', methods=['GET'])
def get_map(map_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch image data from the maps table in the database
    cur.execute("SELECT img_data FROM maps WHERE i_map = %s", (map_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row and row[0]:  # Ensure image data exists
        return Response(io.BytesIO(row[0]), mimetype='image/png')  # Return as an image

    return jsonify({"error": "Map not found in database"}), 404
