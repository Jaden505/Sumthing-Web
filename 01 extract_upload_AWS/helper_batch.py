from img_to_AWS_to_db import get_image_metadata
import datetime as dt

import os


def get_first_last_date_from_batch(dir_name):
    last_datetime = dt.datetime(1900, 1, 1)
    first_datetime = dt.datetime.now()

    for file in os.listdir(dir_name):
        path = os.path.join(dir_name, file)
        metadata = get_image_metadata(path)
        if metadata is None:
            continue

        date = metadata['img_creation_date']

        if date > last_datetime:
            last_datetime = date
        if date < first_datetime:
            first_datetime = date

    # print(last_datetime)
    # print(first_datetime)

    return first_datetime, last_datetime


def get_center_of_batch(dir_name):
    total_lon = 0
    total_lat = 0
    count = 0

    for index, file in enumerate(os.listdir(dir_name)):
        path = os.path.join(dir_name, file)
        metadata = get_image_metadata(path)

        if metadata is None or metadata['img_latitude'] is None or metadata['img_longitude'] is None:
            continue

        total_lon += metadata['img_longitude']
        total_lat += metadata['img_latitude']
        count += 1

    center_lon = total_lon / count
    center_lat = total_lat / count

    return center_lon, center_lat



