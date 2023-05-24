import json
import os

from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename

from models.proof import Proof, db


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config["PG_user"]}:{config["PG_password"]}@{config["PG_host"]}:{config["PG_port"]}/{config["PG_database"]}'
app.config['UPLOAD_FOLDER'] = '06 website/static/images'  # Update this with desired upload directory

db.init_app(app)


@app.route('/')
def index():
    image_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', images=image_files)


@app.route("/anomaly_check")
def anomaly_check():
    return render_template("anomaly_check.html")


@app.route('/upload_images', methods=['POST'])
def upload_images():
    if 'images' not in request.files:
        return jsonify({"error": "No file part in received request"}), 400

    files = request.files.getlist('images')
    filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filenames.append(filename)

    if filenames:
        return jsonify({"message": "Files uploaded successfully", "filenames": filenames}), 200
    else:
        return jsonify({"error": "No valid image files received"}), 400


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
    app.run(debug=True, port=5001, host='0.0.0.0', threaded=True, use_reloader=True)
