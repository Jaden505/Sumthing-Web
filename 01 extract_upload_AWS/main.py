import os
import dotenv
from sqlalchemy import create_engine

from convert_to_jpg import convert_png_to_jpg
from helper_img import extract_all, rename_all, clean_up
from img_to_AWS_to_db import upload_image_extract_metadata_all
from db_CRUD import insert_all_images, insert_batches_to_db

dotenv.load_dotenv()

# postgres database
DATABASE_TO_URI = os.environ['DATABASE_TO_URI']

# aws image bucket
ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
bucketname = os.environ['bucketname']


def main():
    dirname = 'zipimages'
    zip_columns = ['batch_key',
                   'zipname',
                   'extractdatetime']

    zippathname = '.\\' + dirname
    zippath = os.path.join(os.getcwd(), dirname)

    ls_zip = extract_all(zippath, zip_columns)

    insert_batches_to_db(DATABASE_TO_URI, ls_zip)

    # All unzipped images renamed:catch batch_id as prefix
    rename_all(dirname)

    # Extract metadata from imagefile
    # Add seq_number (batch?)
    # Upload to aws
    ls_image = upload_image_extract_metadata_all(zippathname, ACCESS_KEY, SECRET_KEY, bucketname)
    insert_all_images(DATABASE_TO_URI, ls_image)

  
    # Remove all files from zipfiles
    clean_up(zippathname)
