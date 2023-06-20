from flask import Flask, render_template, send_file, request, redirect
from datetime import datetime
import random
from flask_caching import Cache
from io import BytesIO
from AWS_CRUD import conn_AWS, get_images, get_images_with_metadata
import os
import botocore


s3, bucket_name = conn_AWS()

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

current_folder = 'test-trees'


@app.route('/')
def display_images():
    global current_folder
    objects = get_images_with_metadata(s3, bucket_name, current_folder)
    images = []

    for obj in objects:
        try:
            img, metadata = obj['Image'], obj['Metadata']
            metadata['taken_date'] = datetime.strptime(metadata['taken_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            random_id = random.randint(1, 1000000)

            images.append({'id': random_id, 'img': img, 'latitude': metadata['latitude'],
                        'longtitude': metadata['longitude'], 'date': metadata['taken_date']})
        except Exception as e:
            print(f"Image {img} does not have metadata.")

    return render_template('index.html', images=images)

@app.route('/weather/<int:image_id>', methods=['GET'])
def image_weather(image_id):
    images = get_images(s3, bucket_name, current_folder)
    image = next((data for data in images if data['id'] == image_id), None)
    return render_template('image_weather.html', image=image)

@app.route('/weather', methods=['GET'])
def weather():
    return render_template('weather.html')


@app.route('/image/<path:image_path>')
def serve_image(image_path):
    try:
        image_bytes = s3.get_object(Bucket=bucket_name, Key=image_path)['Body'].read()
        return send_file(BytesIO(image_bytes), mimetype='image/jpeg')
    except Exception as e:
        print(f"Error fetching image with path: {image_path}")
        print(e)
        return "Error: Image not found!", 404

@app.route('/get_metadata/<path:image_path>', methods=['GET'])
def get_metadata(image_path):
    try:
        response = s3.head_object(Bucket=bucket_name, Key=image_path)
        return response['Metadata']
    except Exception as e:
        print(f"Error fetching metadata for image with path: {image_path}")
        print(e)
        return "Error: Metadata not found!", 404


# Route to move image to a folder
@app.route('/move_image', methods=['POST'])
def move_image():
    global current_folder
    image_path = request.form['image_path']

    # Determine the new folder based on the current folder
    if current_folder == 'test-trees':
        new_folder_name = 'test-plastic'
    else:
        new_folder_name = 'test-trees'

    # Construct the new key with the new folder name
    new_key = f"{new_folder_name}/{os.path.basename(image_path)}"

    try:
        s3.copy({ 'Bucket': bucket_name, 'Key': image_path }, bucket_name, new_key)
    except botocore.exceptions.ClientError as e:
        print(f"Error copying object. Source bucket: {bucket_name}, Source key: {image_path}")
        print(e)
    else:
        # Only attempt to delete the original object if the copy succeeded
        s3.delete_object(Bucket=bucket_name, Key=image_path)

    return redirect('/')


@app.route('/delete_image', methods=['POST'])
def delete_image():
    image_path = request.form['image_path']

    # Delete the object
    s3.delete_object(Bucket=bucket_name, Key=image_path)
    return redirect('/')

# Route to switch the current folder
@app.route('/switch_folder', methods=['POST'])
def switch_folder():
    global current_folder
    # Switch between 'test-trees' and 'test-plastic'
    if current_folder == 'test-trees':
        current_folder = 'test-plastic'
    else:
        current_folder = 'test-trees'
    return redirect('/')


if __name__ == '__main__':
    try:
        app.run(debug=True, port=5081, host='0.0.0.0', threaded=True, use_reloader=True)
    except Exception as e:
        quit(e)