from PIL import Image
import requests
from io import BytesIO
import random
from datetime import datetime

import sys
sys.path.append('..')  

from AWS_CRUD import conn_AWS, get_image_urls, get_metadata_from_image


def is_valid_image(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img.verify()
        return True
    except (IOError, SyntaxError):
        return False


def get_img_urls_and_metadata():
    s3, bucket_name = conn_AWS()
    AWS_FOLDER = 'AllImages/'
    images_data = []

    image_files = get_image_urls(s3, bucket_name, AWS_FOLDER)

    for file in image_files:
        url, img_name = file[0], file[1]

        if not is_valid_image(url):
            continue

        metadata = get_metadata_from_image(AWS_FOLDER + img_name)
        metadata['taken_date'] = datetime.strptime(metadata['taken_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        random_id = random.randint(1, 1000000)

        images_data.append({'id': random_id, 'url': url, 'latitude': metadata['latitude'],
                            'longtitude': metadata['longitude'], 'date': metadata['taken_date']})

    return images_data
