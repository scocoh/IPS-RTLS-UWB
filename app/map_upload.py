import os
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded_maps'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://parcoadmin:parcoMCSE04106!@192.168.210.231:5432/ParcoRTLSMaint'
db = SQLAlchemy(app)

class Map(db.Model):
    __tablename__ = 'maps'
    i_map = db.Column(db.Integer, primary_key=True)
    x_nm_map = db.Column(db.String(255), nullable=False)
    x_path = db.Column(db.String(500))
    x_format = db.Column(db.String(10), nullable=False, default="PNG")
    d_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
    min_x = db.Column(db.Float)
    min_y = db.Column(db.Float)
    min_z = db.Column(db.Float)
    max_x = db.Column(db.Float)
    max_y = db.Column(db.Float)
    max_z = db.Column(db.Float)
    lat_origin = db.Column(db.Float)
    lon_origin = db.Column(db.Float)
    img_data = db.Column(db.LargeBinary)  # Store image in database

# ✅ Ensure App Context is Used Correctly
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        name = request.form['name']
        lat_origin = request.form['lat_origin']
        lon_origin = request.form['lon_origin']
        min_x = request.form['min_x']
        min_y = request.form['min_y']
        min_z = request.form['min_z']
        max_x = request.form['max_x']
        max_y = request.form['max_y']
        max_z = request.form['max_z']

        print(f"Uploading: {name} → min_x={min_x}, min_y={min_y}, max_x={max_x}, max_y={max_y}")

        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            img_binary = file.read()  # Read image as binary data

            new_map = Map(
                x_nm_map=name,
                x_format=filename.split('.')[-1].upper(),
                d_uploaded=datetime.utcnow(),
                min_x=min_x, min_y=min_y, min_z=min_z,
                max_x=max_x, max_y=max_y, max_z=max_z,
                lat_origin=lat_origin, lon_origin=lon_origin,
                img_data=img_binary  # Store image binary data
            )

            db.session.add(new_map)
            db.session.commit()
            return redirect(url_for('upload_file'))

    maps = Map.query.all()
    return render_template('upload.html', maps=maps)

# ✅ Updated delete_maps to return JSON instead of redirecting
@app.route('/delete_maps', methods=['POST'])
def delete_maps():
    selected_maps = request.form.getlist('selected_maps')  # Ensure form field matches
    
    if not selected_maps:
        return {"message": "No maps selected for deletion"}, 400

    for map_id in selected_maps:
        map_to_delete = Map.query.get(map_id)
        if map_to_delete:
            db.session.delete(map_to_delete)
    
    db.session.commit()
    return redirect(url_for('upload_file'))

# ✅ Add a route to display images stored in the database
@app.route('/map_image/<int:map_id>')
def map_image(map_id):
    map_entry = Map.query.get(map_id)
    if map_entry and map_entry.img_data:
        return send_file(io.BytesIO(map_entry.img_data), mimetype=f'image/{map_entry.x_format.lower()}')
    return "Image Not Found", 404

# ✅ Add the missing edit_map route
@app.route('/edit_map/<int:map_id>', methods=['GET', 'POST'])
def edit_map(map_id):
    map_entry = Map.query.get(map_id)
    if request.method == 'POST':
        map_entry.x_nm_map = request.form['name']
        map_entry.lat_origin = request.form['lat_origin']
        map_entry.lon_origin = request.form['lon_origin']
        map_entry.min_x = request.form['min_x']
        map_entry.min_y = request.form['min_y']
        map_entry.min_z = request.form['min_z']
        map_entry.max_x = request.form['max_x']
        map_entry.max_y = request.form['max_y']
        map_entry.max_z = request.form['max_z']

        db.session.commit()
        return redirect(url_for('upload_file'))

    return render_template('edit.html', map=map_entry)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
