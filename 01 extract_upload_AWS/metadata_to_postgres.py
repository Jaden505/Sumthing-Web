from img_to_AWS_to_db import get_image_metadata
from helper_batch import get_first_last_date_from_batch, get_center_of_batch

import psycopg2
import os


def batch_to_db(batch_name):
    cur.execute("INSERT INTO batch (batch_name) VALUES (%s) RETURNING batch_key", (batch_name,))
    batch_key = cur.fetchone()[0]

    first_datetime, last_datetime = get_first_last_date_from_batch(batch_name, batch_key)
    center_lon, center_lat = get_center_of_batch(batch_name, batch_key)

    # Insert batch key into the batch table
    insert_batch_query = "UPDATE batch SET batch_name = %s, center_long = %s, center_lat = %s, " \
                         "first_photo_upload = %s, last_photo_upload = %s WHERE batch_key = %s"
    execute_query(insert_batch_query, tuple([batch_name, center_lon,
                  center_lat, first_datetime, last_datetime, batch_key]))

    conn.commit()

    return batch_key


def metadata_to_db(image_dir, batch_key):
    for filename in os.listdir(image_dir):
        filepath = os.path.join(image_dir, filename)

        metadata = get_image_metadata(filepath, batch_key)

        # Insert metadata into the proof table
        columns = ", ".join(metadata.keys())
        values = tuple(metadata.values())
        placeholders = ", ".join(["%s" for _ in range(len(values))])

        insert_proof_query = f"INSERT INTO proof ({columns}) VALUES ({placeholders})"
        proof_insert_success = execute_query(insert_proof_query, values)

        if not proof_insert_success:
            print(f"Image {filename} already exists")
            continue


def execute_query(query, values):
    try:
        cur.execute(query, tuple(values))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False

    return True


if __name__ == "__main__":
    # Initialise the database connection
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="",
        password=""
    )
    cur = conn.cursor()

    plastic_key = batch_to_db('../Pictures/plastic/Batch 1')
    metadata_to_db('../Pictures/plastic/Batch 1', plastic_key)

    trees_key = batch_to_db('../Pictures/trees')
    metadata_to_db('../Pictures/trees', trees_key)

    # Close the database connection
    cur.close()
    conn.close()
