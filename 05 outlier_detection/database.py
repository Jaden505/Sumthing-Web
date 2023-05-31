import os

import boto3
import cv2
import numpy as np
import psycopg2
from botocore.exceptions import NoCredentialsError


def get_s3_client(AWS_access_key_id, AWS_secret_access_key):
    return boto3.client('s3', aws_access_key_id=AWS_access_key_id, aws_secret_access_key=AWS_secret_access_key)


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
        return
    except Exception as e:
        print("Error connecting to S3: ", e)
        return

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        cur = conn.cursor()
    except Exception as e:
        print("Error connecting to the database: ", e)
        return

    for obj in contents:
        filename = obj['Key']
        if not filename.endswith("/"):  # Ensure the file is not a directory
            try:
                s3.download_file(AWS_bucket_name, filename, '/tmp/' + filename.split('/')[-1])
                with open('/tmp/' + filename.split('/')[-1], "rb") as img_file:
                    img_data = img_file.read()

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


def load_images_from_db(database, user, password, host, port):
    # Establish a connection to the database
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

    cur = conn.cursor()

    # Execute an SQL query to retrieve the filenames and image data for all images in the database
    cur.execute("SELECT filename, image_data FROM images")

    # Initialize lists to store the loaded images and their corresponding filenames
    images = []
    filenames = []

    # Loop through each row of the query results
    for filename, image_data in cur.fetchall():
        try:
            # Use OpenCV to read the image data as a numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # If the image has an alpha channel, remove it
            if image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

            # Resize the image to a fixed size
            image = cv2.resize(image, (128, 128))

            images.append(image)
            filenames.append(filename)

        except Exception as e:
            print(f"Error loading image: {filename}")
            print(str(e))
            continue

    print(f"Loaded {len(images)} images from the database.")

    cur.close()
    conn.close()

    return np.array(images), filenames
