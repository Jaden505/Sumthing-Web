import os, json
import dotenv
import boto3

from AWS_CRUD import *
from metadata import get_image_metadata

dotenv.load_dotenv()

with open('../config.json') as f:
    config = json.load(f)

# aws image bucket
ACCESS_KEY = config['AWS_access_key_id']
SECRET_KEY = config['AWS_secret_access_key']
BUCKETNAME = config['bucket_name']

local_img_folder = 'zipimages'
AWS_folder = 'AllImages'


def main():
    s3, bucket_name = conn_AWS()

    for file in os.listdir(local_img_folder):
        file_path = os.path.join(local_img_folder, file)
        file_name = os.path.basename(file_path)

        upload_img(s3, bucket_name, AWS_folder, file_path)
        print(f'Uploaded {file_name} to AWS bucket {bucket_name}/{AWS_folder}')

        # Add metadata to image
        metadata = get_image_metadata(file_path)
        add_metadata_to_image(f'{AWS_folder}/{file}', metadata)
        print(f'Added metadata to {file_name}')

    print('Uploaded all images to AWS with metadata')


if __name__ == '__main__':
    main()