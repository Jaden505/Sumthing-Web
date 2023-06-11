import json
import os

from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
from AWS_CRUD import conn_AWS, get_image_urls
from PIL import Image

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



app = Flask(__name__)

#  Get Images from AWS S3
s3, bucket_name = conn_AWS()
AWS_FOLDER = 'AllImages/'

app.config['image_files'] = get_image_urls(s3, bucket_name, AWS_FOLDER)
print(app.config['image_files'])


def is_valid_image(image_url):
    try:
        # Open the image using PIL
        with Image.open(image_url) as img:
            # Verify that the image can be loaded without errors
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False


for url in app.config['image_files']:
    if not is_valid_image(url):
        app.config['image_files'].remove(url)


@app.route('/')
def index():
    return render_template('index.html', images=app.config['image_files'])


@app.route('/weather', methods=['GET'])
def weather():
    return render_template('weather.html')


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


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0', threaded=True, use_reloader=True)
