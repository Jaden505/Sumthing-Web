import boto3
import json

# Read AWS credentials and bucket configuration from JSON file
with open('config.json') as config_file:
    config = json.load(config_file)
    aws_access_key_id = config['AWS_access_key_id']
    aws_secret_access_key = config['AWS_secret_access_key']
    bucket_name = config['bucket_name']

# Create an S3 client using the credentials
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

def create_object(folder_name, file_path):
    """
    Uploads a file to the specified folder in the S3 bucket.
    """
    s3.upload_file(file_path, bucket_name, folder_name + '/' + file_path)

def read_objects(folder_name):
    """
    Retrieves a list of objects from the specified folder in the S3 bucket.
    """
    response = s3.list_objects(Bucket=bucket_name, Prefix=folder_name + '/')
    objects = []
    if 'Contents' in response:
        objects = [obj['Key'] for obj in response['Contents']]
    return objects

def update_object(folder_name, file_path):
    """
    Updates an existing file in the specified folder in the S3 bucket.
    """
    s3.upload_file(file_path, bucket_name, folder_name + '/' + file_path)

def delete_object(folder_name, file_name):
    """
    Deletes a file from the specified folder in the S3 bucket.
    """
    s3.delete_object(Bucket=bucket_name, Key=folder_name + '/' + file_name)

# Example usage
folder_name = '<FOLDER_NAME>'
file_path = '/path/to/image.jpg'

# Create an object in the specified folder
# create_object(folder_name, file_path)

# Get all images from the 'plastic' folder
plastic_images = read_objects('plastic')
print("Plastic folder contents:", plastic_images)

# Get all images from the 'trees' folder
trees_images = read_objects('trees')
print("Trees folder contents:", trees_images)

# Update an existing object in the specified folder
# update_object(folder_name, file_path)

# Delete an object from the specified folder
# delete_object(folder_name, 'image.jpg')
