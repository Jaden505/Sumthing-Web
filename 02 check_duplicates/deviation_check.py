import os
import numpy as np
import pywt
import cv2
from skimage.feature import local_binary_pattern
from keras.applications.vgg16 import VGG16, preprocess_input
from pyod.models.hbos import HBOS
import psycopg2
import base64
import json


def load_config(config_path):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        return config


# Function to insert images into the database
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


# Extract wavelet features from images
def extract_wavelet_features(images, mode="db1", level=2):
    print(f"Number of input images in extract_wavelet_features: {len(images)}")
    features = []

    for img in images:
        if img.dtype != np.uint8:
            img = img.astype(np.uint8)  # Convert the image to uint8 if necessary

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert the image to grayscale
        coeffs = pywt.wavedecn(img_gray, mode, level=level)
        coeffs = [coeff for coeff in coeffs if not isinstance(coeff, dict)]  # Add this line to filter out dictionaries
        features.append(np.hstack([np.array(coeff).flatten() for coeff in coeffs]))

    return np.array(features)


# Identify outlier images based on wavelet features
def identify_outliers(features, filenames, contamination=0.1):
    # Create HBOS model
    hbos = HBOS(contamination=contamination)

    # Fit the model
    hbos.fit(features)

    # Identify outliers
    is_outlier = hbos.predict(features) == 1
    outliers = [(filenames[i], hbos.decision_scores_[i]) for i in range(len(features)) if is_outlier[i]]

    return outliers


def extract_color_histograms(images, num_bins=32):
    print(f"Number of input images in extract_color_histograms: {len(images)}")
    histograms = []

    for img in images:
        img = (img * 255).astype(np.uint8)  # Convert the image back to uint8 format
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert the image to BGR format

        # Compute histograms for each color channel (B, G, R)
        hist_b = cv2.calcHist([img], [0], None, [num_bins], [0, 256])
        hist_g = cv2.calcHist([img], [1], None, [num_bins], [0, 256])
        hist_r = cv2.calcHist([img], [2], None, [num_bins], [0, 256])

        # Concatenate histograms and normalize
        hist = np.hstack([hist_b, hist_g, hist_r]).flatten()
        hist = hist / hist.sum()

        histograms.append(hist)

    return np.array(histograms)


def extract_lbp_features(images, num_points=24, radius=3, method="uniform"):
    print(f"Number of input images in extract_lbp_features: {len(images)}")
    lbp_features = []

    for img in images:
        img_gray = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        lbp = local_binary_pattern(img_gray, num_points, radius, method)
        hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, num_points + 3), range=(0, num_points + 2))
        hist = hist / hist.sum()
        lbp_features.append(hist)

    return np.array(lbp_features)


def extract_cnn_features(images, model=None, target_size=(128, 128)):
    print(f"Number of input images in extract_cnn_features: {len(images)}")
    if model is None:
        model = VGG16(weights='imagenet', include_top=False, pooling='avg')

    # Resize images to the target size and convert them to uint8 format
    images_resized = [cv2.resize(img.astype(np.uint8), target_size) for img in images]

    # Convert the list to a NumPy array
    images_resized = np.array(images_resized)

    # Preprocess images for the VGG16 model
    if len(images_resized) == 0:
        return np.array([])  # Return empty array if there are no images
    else:
        preprocessed_images = preprocess_input(images_resized * 255)

    features = model.predict(preprocessed_images)

    return features


def clear_images_table(database, user, password, host, port):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("DELETE FROM images")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    config_path = "/Users/ayoubezzaouia/sumting-1/config.json"
    config = load_config(config_path)

    image_directory = config["pictures_dir"]
    folder_name = config["folder_name"]
    db_config = {key: config[key] for key in ["database", "user", "password", "host", "port"]}

    # Clear the images table
    clear_images_table(**db_config)

    # Populate the database with images
    add_images_to_database(image_directory=image_directory, **db_config, folder_name=folder_name)

    # Load images from the database
    images, filenames = load_images_from_db(**db_config)

    # Extract wavelet features and other features
    features = extract_wavelet_features(images)
    color_histograms = extract_color_histograms(images)
    lbp_features = extract_lbp_features(images)
    cnn_features = extract_cnn_features(images)

    print("Features shape:", features.shape)
    print("Color histograms shape:", color_histograms.shape)
    print("LBP features shape:", lbp_features.shape)
    print("CNN features shape:", cnn_features.shape)

    # Combine features
    if features.size == 0 or color_histograms.size == 0 or lbp_features.size == 0 or cnn_features.size == 0:
        print("No features were extracted. Check the image_directory and make sure it contains .jpg or .png images.")
    else:
        combined_features = np.concatenate((features, color_histograms, lbp_features, cnn_features), axis=1)

        # Identify outliers
        contamination = 0.02
        outliers = identify_outliers(combined_features, filenames, contamination=contamination)

        if len(outliers) == 0:
            print("No outlier images found.")
        else:
            print("Outlier images:")
            outliers_sorted = sorted(outliers, key=lambda x: x[1], reverse=True)
            for filename, score in outliers_sorted:
                print(f"{filename} - Score: {score}")
