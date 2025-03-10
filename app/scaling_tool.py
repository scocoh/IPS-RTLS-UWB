from flask import Flask, request, jsonify, render_template
import io
import base64
from PIL import Image
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('scaling_tool.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    
    img = Image.open(file)
    img = img.convert('RGB')
    
    # Get image dimensions
    width, height = img.size
    
    # Convert image to base64 for display in frontend
    buffered = io.BytesIO()
    img.save(buffered, format='PNG')
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'image': img_str, 'width': width, 'height': height})

@app.route('/compute_scaling', methods=['POST'])
def compute_scaling():
    data = request.json
    
    # Extract values from request
    p1_x_px = data['p1_x_px']
    p1_y_px = data['p1_y_px']
    p2_x_px = data['p2_x_px']
    p2_y_px = data['p2_y_px']
    p1_x_ft = data['p1_x_ft']
    p1_y_ft = data['p1_y_ft']
    p2_x_ft = data['p2_x_ft']
    p2_y_ft = data['p2_y_ft']
    image_width = data['image_width']
    image_height = data['image_height']
    
    # Compute pixel deltas
    delta_x_px = p2_x_px - p1_x_px
    delta_y_px = p1_y_px - p2_y_px  # Y-axis inversion
    
    # Compute real-world deltas
    delta_x_ft = p2_x_ft - p1_x_ft
    delta_y_ft = p2_y_ft - p1_y_ft
    
    # Compute pixels per foot
    pixels_per_foot_x = delta_x_px / delta_x_ft
    pixels_per_foot_y = delta_y_px / delta_y_ft
    
    # Compute bottom-left and top-right in feet
    min_x_ft = p1_x_ft - (p1_x_px / pixels_per_foot_x)
    min_y_ft = (p1_y_px / pixels_per_foot_y) - p1_y_ft
    max_x_ft = image_width / pixels_per_foot_x
    max_y_ft = image_height / pixels_per_foot_y
    
    return jsonify({
        'min_x_ft': min_x_ft,
        'min_y_ft': min_y_ft,
        'max_x_ft': max_x_ft,
        'max_y_ft': max_y_ft,
        'pixels_per_foot_x': pixels_per_foot_x,
        'pixels_per_foot_y': pixels_per_foot_y
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
