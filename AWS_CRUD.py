import boto3, json, os
from PIL import Image
import numpy as np
import cv2

def conn_AWS():
    # Read AWS credentials and bucket configuration from JSON file
    with open('../config.json') as config_file:
        config = json.load(config_file)
        aws_access_key_id = config['AWS_access_key_id']
        aws_secret_access_key = config['AWS_secret_access_key']
        bucket_name = config['bucket_name']

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    return s3, bucket_name

def upload_img(s3, bucket_name, folder_name, file_path):
    s3.upload_file(file_path, bucket_name, folder_name + '/' + file_path)

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

def read_images_from_s3(s3, bucket_name, folder_name):
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

def DownloadWeatherImages(local_folder):
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


def upload_weather_images(s3, bucket_name, folder_name, local_folder_path):
    image_name_changer(local_folder_path, '.jpg', local_folder_path)

    for filename in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, filename)
        s3.upload_file(file_path, bucket_name, folder_name + '/' + filename)

def image_name_changer(directory, file_ends_with, dir_to_save_in):
    for folder_name in os.listdir(directory):
        for filename in os.listdir(os.path.join(directory, folder_name)):
            if filename.endswith(file_ends_with):
                joined_path = os.path.join(directory, folder_name, filename)
                im = Image.open(joined_path)
                name = folder_name + "_" + filename.split(".")[0] + '.JPG'
                try:
                    im.save(os.path.join(dir_to_save_in, name))
                except Exception as err:
                    print('Something went wrong trying to save the updated image.')

                os.remove(joined_path)
                continue
            else:
                continue

