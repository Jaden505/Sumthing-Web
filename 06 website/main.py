import os

from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
from parse_images import get_img_urls_and_metadata

app = Flask(__name__)

app.config['images_data'] = get_img_urls_and_metadata()
print(app.config['images_data'])

@app.route('/')
def index():
    return render_template('index.html', images=app.config['images_data'])


@app.route('/weather', methods=['GET'])
def weather():
    return render_template('weather.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0', threaded=True, use_reloader=True)
