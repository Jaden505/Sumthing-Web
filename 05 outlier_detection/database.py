import os

import boto3
import cv2
import numpy as np
import psycopg2
from botocore.exceptions import NoCredentialsError


def get_s3_client(AWS_access_key_id, AWS_secret_access_key):
    return boto3.client('s3', aws_access_key_id=AWS_access_key_id, aws_secret_access_key=AWS_secret_access_key)

## incrementele database functie toevoegen 
def clear_images_table(database, user, password, host, port):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("DELETE FROM images")

    conn.commit()
    cur.close()
    conn.close()


def add_images_to_database(AWS_access_key_id, AWS_secret_access_key, AWS_bucket_name, AWS_folder_name, database, user,
                           password, host, port):
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_access_key_id, aws_secret_access_key=AWS_secret_access_key)
        contents = s3.list_objects(Bucket=AWS_bucket_name, Prefix=AWS_folder_name)['Contents']
    except NoCredentialsError:
        print("No AWS credentials found.")
        return [], []
    except Exception as e:
        print("Error connecting to S3: ", e)
        return [], []

    images = []
    filenames = []

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        cur = conn.cursor()
    except Exception as e:
        print("Error connecting to the database: ", e)
        return [], []

    for obj in contents:
        filename = obj['Key']
        if not filename.endswith("/") and not filename.startswith(
                "._"):  # Ensure the file is not a directory or a hidden/system file
            try:
                s3.download_file(AWS_bucket_name, filename, '/tmp/' + filename.split('/')[-1])
                with open('/tmp/' + filename.split('/')[-1], "rb") as img_file:
                    img_data = img_file.read()
                    nparr = np.frombuffer(img_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if img is None:
                        print(f"Unable to decode image: {filename}")
                        continue
                    if img.shape[2] == 4:
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    img = cv2.resize(img, (128, 128))

                images.append(img)
                filenames.append(filename.split('/')[-1])

                cur.execute(
                    "INSERT INTO images (filename, folder_name, image_data, outlier_score) VALUES (%s, %s, %s, %s)",
                    (filename.split('/')[-1], AWS_folder_name, img_data, 0))
                os.remove(
                    '/tmp/' + filename.split('/')[-1])  # Removing the file after inserting its data into the database
            except Exception as e:
                print(f"Error processing file {filename}: ", e)

    conn.commit()
    cur.close()
    conn.close()

    return np.array(images), filenames


def update_outlier_scores(database, user, password, host, port, filenames, outlier_scores):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    for filename, outlier_score in zip(filenames, outlier_scores):
        cur.execute(
            "UPDATE images SET outlier_score = %s WHERE filename = %s",
            (outlier_score, filename)
        )

    conn.commit()
    cur.close()
    conn.close()
