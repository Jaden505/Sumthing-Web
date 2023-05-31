import os, json
import dotenv

from helper_img import extract_all, rename_all, clean_up
from img_to_AWS_to_db import upload_image_extract_metadata_all
from db_CRUD import insert_all_images, insert_batches_to_db

dotenv.load_dotenv()

with open('../config.json') as f:
    config = json.load(f)

# postgres database
url = f'postgresql://{config["PG_user"]}:{config["PG_password"]}@{config["PG_host"]}:{config["PG_port"]}/{config["PG_database"]}'

# aws image bucket
ACCESS_KEY = config['AWS_access_key_id']
SECRET_KEY = config['AWS_secret_access_key']
bucketname = config['bucket_name']


def main():
    zip_columns = ['batch_key',
                   'zipname',
                   'extractdatetime']

    dirname = 'zipimages'
    zippathname = '.\\' + dirname

    zippath = os.path.abspath(dirname)

    # Use the full path to extract and upload the images
    ls_zip = extract_all(zippath, zip_columns)
    ls_image = upload_image_extract_metadata_all(zippath, ACCESS_KEY, SECRET_KEY, bucketname)

    insert_batches_to_db(url, ls_zip)

    # All unzipped images renamed:catch batch_id as prefix
    rename_all(dirname)

    # Extract metadata from imagefile
    # Add seq_number (batch?)
    # Upload to aws
    ls_image = upload_image_extract_metadata_all(zippathname, ACCESS_KEY, SECRET_KEY, bucketname)
    insert_all_images(url, ls_image)

  
    # Remove all files from zipfiles
    clean_up(zippathname)

if __name__ == '__main__':
    main()