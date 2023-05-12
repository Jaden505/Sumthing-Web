import numpy as np

from config import load_config
from database import add_images_to_database, load_images_from_db, clear_images_table
from feature_extraction import (
    extract_wavelet_features,
    extract_color_histograms,
    extract_lbp_features,
    extract_cnn_features,
)
from outlier import identify_outliers

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
        contamination = 0.1
        outliers = identify_outliers(combined_features, filenames, contamination=contamination)

        if len(outliers) == 0:
            print("No outlier images found.")
        else:
            print("Outlier images:")
            outliers_sorted = sorted(outliers, key=lambda x: x[1], reverse=True)
            for filename, score in outliers_sorted:
                print(f"{filename} - Score: {score}")
