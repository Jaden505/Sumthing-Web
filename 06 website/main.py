import json
import os

from flask import Flask, render_template, jsonify, request

from website.models.proof import Proof, db

with open('../config.json') as f:
    config = json.load(f)

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config["user"]}:{config["password"]}@{config["host"]}:{config["port"]}/{config["database"]}'

db.init_app(app)


@app.route('/')
def index():
    image_files = os.listdir('static/images')
    return render_template('index.html', images=image_files)


@app.route('/get_image_data', methods=['GET'])
def get_image_data():
    query_param = request.args.get('query')

    # Retrieve data from the database
    data = Proof.query.filter_by(img_name=query_param).all()
    if data:
        data_list = [
            {'proof_key': item.proof_key,
             'img_name': item.img_name,
             'created_at': item.created_at,
             'latitude': round(float(item.img_latitude), 2),
             'longitude': round(float(item.img_longitude), 2),
             'altitude': item.img_altitude}
            for item in data]

        # Return the data as JSON
        return jsonify(data_list)
    else:
        return jsonify({'message': 'Data not found'})


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True, use_reloader=True)
