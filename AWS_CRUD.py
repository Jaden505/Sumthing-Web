import numpy as np
import cv2
import boto3
import os
import json
from botocore.exceptions import ClientError


def conn_AWS():
    # Read AWS credentials and bucket configuration from JSON file
    with open('../config.json') as config_file:
        config = json.load(config_file)
        aws_access_key_id = config['AWS_access_key_id']
        aws_secret_access_key = config['AWS_secret_access_key']
        bucket_name = config['bucket_name']

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='eu-north-1')
    return s3, bucket_name


def upload_img(s3, bucket_name, folder_name, file_path):
    file_name = os.path.basename(file_path)
    s3.upload_file(file_path, bucket_name, f"{folder_name}/{file_name}")


def get_images(s3, bucket_name, folder_name):
    response = s3.list_objects(Bucket=bucket_name, Prefix=folder_name + '/')
    objects = []
    if 'Contents' in response:
        objects = [obj['Key'] for obj in response['Contents']]
    return objects


def update_img(s3, bucket_name, folder_name, file_path):
    s3.upload_file(file_path, bucket_name, folder_name + '/' + file_path)


def del_img(s3, bucket_name, folder_name, file_name):
    s3.delete_object(Bucket=bucket_name, Key=folder_name + '/' + file_name)


def move_image_within_s3_bucket(source_folder, destination_folder, image_filename):
    s3, bucket_name = conn_AWS()

    # Construct the source and destination object keys
    source_key = f"{source_folder}/{image_filename}"
    destination_key = f"{destination_folder}/{image_filename}"

    # Copy the object to the destination folder
    s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': source_key},
                          Key=destination_key)

    # Delete the object from the source folder
    s3.delete_object(Bucket=bucket_name, Key=source_key)


def add_metadata_to_image(aws_path_to_image, metadata):
    s3, bucket_name = conn_AWS()

    # Convert metadata values to strings or list of strings
    metadata = {key: json.dumps(value) if isinstance(value, list) else value for key, value in metadata.items()}

    s3.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': bucket_name, 'Key': aws_path_to_image},
        Key=aws_path_to_image,
        Metadata=metadata,
        MetadataDirective='REPLACE'
    )


def get_metadata_from_image(aws_path_to_image):
    s3, bucket_name = conn_AWS()

    response = s3.head_object(Bucket=bucket_name, Key=aws_path_to_image)

    return response['Metadata']


def update_metadata_of_image(aws_path_to_image, metadata):
    s3, bucket_name = conn_AWS()

    # Convert metadata values to strings or list of strings
    metadata = {key: json.dumps(value) if isinstance(value, list) else value for key, value in metadata.items()}

    s3.put_object(
        Bucket=bucket_name,
        Key=aws_path_to_image,
        Metadata=metadata
    )


def update_duplicate(path_to_image, path_to_dup_img):
    metadata = get_metadata_from_image(path_to_image)
    if 'duplicates' in metadata:
        parsed_duplicates = json.loads(metadata['duplicates'])
        parsed_duplicates.append(path_to_dup_img)
        metadata['duplicates'] = parsed_duplicates
        update_metadata_of_image(path_to_image, metadata)
    else:
        metadata['duplicates'] = [path_to_dup_img]
        update_metadata_of_image(path_to_image, metadata)


def update_image_duplicates(path_to_image, path_to_dup_img):
    update_duplicate(path_to_image, path_to_dup_img)
    update_duplicate(path_to_dup_img, path_to_image)


def read_images_from_s3_as_train_data(s3, bucket_name, folder_name):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name + '/')
    objects = response.get('Contents', [])

    train_images = []
    train_labels = []

    for obj in objects:
        image_key = obj['Key']
        image_bytes = s3.get_object(Bucket=bucket_name, Key=image_key)['Body'].read()
        np_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        train_images.append(img)

        label = image_key.split('/')[1].split('_')[0]
        train_labels.append(label)

    return train_images, train_labels


def download_weather_train_data(local_folder):
    train_images = []
    train_labels = []
    shape = (300, 300)
    AWS_folder = 'weather/updated_dataset'

    s3, bucket_name = conn_AWS()
    os.mkdir(local_folder)

    for image_path in get_images(s3, bucket_name, AWS_folder):
        if image_path.lower().endswith('.jpg') or image_path.lower().endswith(
                '.jpeg') or image_path.lower().endswith('.png'):
            local_filepath = os.path.join(local_folder, os.path.basename(image_path))
            s3.download_file(bucket_name, image_path, local_filepath)

            img = cv2.imread(local_filepath)
            train_labels.append(os.path.basename(image_path).split('_')[0])
            img = cv2.resize(img / 255, shape)
            train_images.append(img)

    return train_images, train_labels
