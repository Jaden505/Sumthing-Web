import psycopg2
import pandas as pd
from upload_images_extract_metadata import get_image_metadata
import datetime as dt

import os





def get_first_last_date_from_batch(ls_zip_name):
    cwd = os.getcwd()
    d = os.path.join(cwd, 'zipimages', ls_zip_name)

    last_datetime = dt.datetime(1900, 1, 1)
    first_datetime = dt.datetime.now()



    for file in os.listdir(os.path.join(os.getcwd(), 'zipimages', ls_zip_name)):
        path = os.path.join(d, file)
        date = get_image_metadata(path)['proof_date']

        if date > last_datetime:
            last_datetime = date
        if date < first_datetime:
            first_datetime = date

    # print(last_datetime)
    # print(first_datetime)

    return first_datetime, last_datetime


def get_center_of_batch(ls_zip_name):
    cwd = os.getcwd()
    d = os.path.join(cwd, 'zipimages', ls_zip_name)

    total_lon = 0
    total_lat = 0
    count = 0

    for index, file in enumerate(os.listdir(os.path.join(os.getcwd(), 'zipimages', ls_zip_name))):
        path = os.path.join(d, file)
        metadata = get_image_metadata(path)

        total_lon += metadata['longitude']
        total_lat += metadata['latitude']
        count += 1

    center_lon = total_lon / count
    center_lat = total_lat / count

    return center_lon, center_lat



