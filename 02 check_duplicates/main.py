import os, json
import dotenv

from duplicate_check_CNN import duplicate_check_CNN
from img_checker import find_corrupted, find_duplicates

dotenv.load_dotenv()

with open('../config.json') as config_file:
    config = json.load(config_file)

ACCESS_KEY = config['AWS_access_key_id']
SECRET_KEY = config['AWS_secret_access_key']
bucketname = config['bucket_name']

AWS_folder = 'AllImages'
local_folder = '../zipimages'

def main():
    find_corrupted(local_folder)
    find_duplicates(local_folder)
    duplicate_check_CNN(local_folder, 0.85)


if __name__ == '__main__':
    main()
