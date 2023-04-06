from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    image_files = os.listdir('static/images')
    return render_template('index.html', images=image_files)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True, use_reloader=True)
