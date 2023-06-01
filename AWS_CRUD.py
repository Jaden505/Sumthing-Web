import numpy as np
import cv2
import boto3
import botocore
import os
import json
from botocore.exceptions import NoCredentialsError


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

    # Convert metadata values to strings
    metadata = {key: str(value) for key, value in metadata.items()}

    s3.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': bucket_name, 'Key': aws_path_to_image},
        Key=aws_path_to_image,
        Metadata=metadata,
        MetadataDirective='REPLACE'
    )


def get_metadata_from_image(path_to_image):
    s3, bucket_name = conn_AWS()

    response = s3.head_object(Bucket=bucket_name, Key=path_to_image)

    return response['Metadata']


def update_image_score(path_to_image, score, score_type):
    metadata = get_metadata_from_image(path_to_image)
    metadata[score_type] = score

    add_metadata_to_image(path_to_image, metadata)
