from flask import Flask, render_template
from parse_images import get_img_urls_and_metadata
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=3600)
def get_images_data():
    return get_img_urls_and_metadata()

@app.route('/', methods=['GET'])
def index():
    images_data = get_images_data()
    return render_template('index.html', images=images_data)

@app.route('/weather/<int:image_id>', methods=['GET'])
def image_weather(image_id):
    images_data = get_images_data()
    image = next((data for data in images_data if data['id'] == image_id), None)
    return render_template('image_weather.html', image=image)

@app.route('/weather', methods=['GET'])
def weather():
    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True, port=5010, host='0.0.0.0', threaded=True, use_reloader=True)