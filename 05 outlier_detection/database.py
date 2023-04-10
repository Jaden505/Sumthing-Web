import os
import numpy as np
import cv2
import psycopg2
import base64


def insert_image(database, user, password, host, port, image_path, folder_name):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read())

    filename = os.path.basename(image_path)
    cur.execute("INSERT INTO images (filename, folder_name, image_data) VALUES (%s, %s, %s)",
                (filename, folder_name, img_data))

    conn.commit()
    cur.close()
    conn.close()


# Function to add images to the database from a directory
def add_images_to_database(database, user, password, host, port, image_directory, folder_name):
    image_files = [f for f in os.listdir(image_directory) if f.lower().endswith(('.png', '.jpg', '.JPG'))]

    for image_file in image_files:
        image_path = os.path.join(image_directory, image_file)
        insert_image(database, user, password, host, port, image_path, folder_name)


# Function to load images from the database
def load_images_from_db(database, user, password, host, port):
    # Establish a connection to the database
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

    # Create a cursor object to execute SQL queries
    cur = conn.cursor()

    # Execute an SQL query to retrieve the filenames and image data for all images in the database
    cur.execute("SELECT filename, image_data FROM images")

    # Initialize lists to store the loaded images and their corresponding filenames
    images = []
    filenames = []

    # Loop through each row of the query results
    for filename, image_data in cur.fetchall():
        try:
            # Decode the base64 image data
            img_data_decoded = base64.b64decode(image_data)

            # Use OpenCV to read the image
            image = cv2.imdecode(np.frombuffer(img_data_decoded, np.uint8), cv2.IMREAD_UNCHANGED)

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

    # Convert the image list to a numpy array and return it along with the corresponding filenames
    return np.array(images, dtype=object), filenames


def clear_images_table(database, user, password, host, port):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("DELETE FROM images")

    conn.commit()
    cur.close()
    conn.close()
