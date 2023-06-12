from PIL import Image
import requests
from io import BytesIO

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
            image_files.remove((url, img_name))
            continue

        metadata = get_metadata_from_image(AWS_FOLDER + img_name)

        images_data.append({'url': url, 'latitude': metadata['latitude'],
                            'longtitude': metadata['longitude'], 'date': metadata['taken_date']})

    return images_data
