import os
import sqlalchemy as db
from img_to_AWS_to_db import get_image_metadata
from helper_batch import get_first_last_date_from_batch, get_center_of_batch
from db_CRUD import connect_database, create_tables

engine, conn = connect_database('postgresql://@localhost:5432/postgres')
create_tables(engine)

batch = db.Table('batch', db.MetaData(), autoload_with=engine)
proof = db.Table('proof', db.MetaData(), autoload_with=engine)


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

    return batch_key


def metadata_to_db(image_dir, batch_key):
    for filename in os.listdir(image_dir):
        filepath = os.path.join(image_dir, filename)

        metadata = get_image_metadata(filepath, batch_key)

        # Insert metadata into the proof table
        ins = proof.insert().values(
            proof_image_name=filename,
            batch_key=batch_key,
            proof_date=metadata['proof_date'],
            latitude=metadata['latitude'],
            longitude=metadata['longitude'],
        )
        try:
            conn.execute(ins)
        except db.exc.IntegrityError:
            print(f"Image {filename} already exists")
            continue


if __name__ == "__main__":
    plastic_key = batch_to_db('../Pictures/plastic/Batch 1')
    metadata_to_db('../Pictures/plastic/Batch 1', plastic_key)

    trees_key = batch_to_db('../Pictures/trees')
    metadata_to_db('../Pictures/trees', trees_key)

    conn.close()
