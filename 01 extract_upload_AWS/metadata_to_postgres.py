import os

import sqlalchemy as db

from db_CRUD import connect_database, create_tables
from db_ORM import Batch, ProofTable
from helper_batch import get_first_last_date_from_batch, get_center_of_batch
from img_to_AWS_to_db import get_image_metadata

import json

with open('config.json') as f:
    config = json.load(f)

url = f'postgresql://{config["PG_user"]}:{config["PG_password"]}@{config["PG_host"]}:{config["PG_port"]}/{config["PG_database"]}'

engine, conn = connect_database(url)
create_tables(engine)

batch = Batch.__table__
images = ProofTable.__table__


def batch_to_db(batch_name):
    ins = batch.insert().values(batch_name=batch_name)
    batch_key = conn.execute(ins).inserted_primary_key[0]

    first_datetime, last_datetime = get_first_last_date_from_batch(batch_name, batch_key)
    center_lon, center_lat = get_center_of_batch(batch_name, batch_key)

    # Insert batch key into the batch table
    ins = batch.update().where(batch.c.batch_key == batch_key).values(
        center_long=center_lon,
        center_lat=center_lat,
        first_photo_upload=first_datetime,
        last_photo_upload=last_datetime,
        batch_name=batch_name
    )
    conn.execute(ins)
    conn.commit()
    return batch_key


def metadata_to_db(image_dir, batch_key):
    for filename in os.listdir(image_dir):
        filepath = os.path.join(image_dir, filename)

        metadata = get_image_metadata(filepath, batch_key)
        if metadata is None:
            print(f"Image {filename} is corrupted")
            continue

        # Insert metadata into the proof table
        ins = images.insert().values(
            img_name=filename,
            img_creation_date=metadata['img_creation_date'],
            img_device_model=metadata['img_device_model'],
            img_format=metadata['img_format'],
            img_iso=metadata['img_iso'],
            img_f_number=metadata['img_f_number'],
            img_focal_length=metadata['img_focal_length'],
            img_flash=metadata['img_flash'],
            img_shutterspeed=metadata['img_shutterspeed'],
            img_exposure_time=metadata['img_exposure_time'],
            img_dimensions=metadata['img_dimensions'],
            img_total_pixels= metadata['img_total_pixels'],
            img_latitude=metadata['img_latitude'],
            img_longitude=metadata['img_longitude'],
            img_altitude=metadata['img_altitude'],
            batch_key=batch_key,
            )
        try:
            conn.execute(ins)
            conn.commit()
        except db.exc.IntegrityError:
            print(f"Image {filename} already exists")
            continue


if __name__ == "__main__":


    conn.close()
