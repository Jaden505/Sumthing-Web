import boto3
from botocore.exceptions import NoCredentialsError


def upload_image_to_aws(filename, ACCESS_KEY, SECRET_KEY, bucketname):
    s3 = boto3.client('s3', 'eu-central-1', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    s3_filename=filename
    try:
        s3.upload_file(filename, bucketname, s3_filename)
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False




