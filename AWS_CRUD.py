import boto3, json, os
from PIL import Image

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

