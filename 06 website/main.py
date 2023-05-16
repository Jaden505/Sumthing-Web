import json
import os

from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename

from models.proof import Proof, db


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


with open('../config.json') as f:
    config = json.load(f)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config["user"]}:{config["password"]}@{config["host"]}:{config["port"]}/{config["database"]}'
app.config['UPLOAD_FOLDER'] = 'static/images'  # Update this with desired upload directory

db.init_app(app)


@app.route('/')
def index():
    image_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', images=image_files)


@app.route("/anomaly_check")
def anomaly_check():
    return render_template("anomaly_check.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return 'No file part'
    file = request.files['image']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded successfully'


@app.route('/get_image_data', methods=['GET'])
def get_image_data():
    query_param = request.args.get('query')
    data = Proof.query.filter_by(img_name=query_param).all()
    if data:
        data_list = [
            {'proof_key': item.proof_key,
             'img_name': item.img_name,
             'img_creation_date': item.img_creation_date,
             'latitude': round(float(item.img_latitude), 2),
             'longitude': round(float(item.img_longitude), 2),
             'altitude': item.img_altitude}
            for item in data]
        return jsonify(data_list)
    else:
        return jsonify({'message': 'Data not found'})


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True, use_reloader=True)
