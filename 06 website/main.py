import os

from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
from parse_images import get_img_urls_and_metadata

app = Flask(__name__)

app.config['images_data'] = get_img_urls_and_metadata()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', images=app.config['images_data'])


@app.route('/weather/<int:image_id>', methods=['GET'])
def image_weather(image_id):
    image = None
    for data in app.config['images_data']:
        if data['id'] == image_id:
            image = data
            break

    return render_template('image_weather.html', image=image)


@app.route('/weather', methods=['GET'])
def weather():
    return render_template('weather.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0', threaded=True, use_reloader=True)
