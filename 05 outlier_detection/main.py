import os.path

import numpy as np

from config import load_config
from database import (
    add_images_to_database,
    update_outlier_scores, populate_if_different,
)
from feature_extraction import (
    extract_wavelet_features,
    extract_color_histograms,
    extract_lbp_features,
    extract_cnn_features,
)
from outlier import identify_outliers

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    config = load_config(config_path)

    aws_config = {key: config[key] for key in ["AWS_access_key_id", "AWS_secret_access_key", "AWS_bucket_name",
                                               "AWS_folder_name"]}
    db_config = {key: config[key] for key in ["PG_database", "PG_user", "PG_password", "PG_host", "PG_port"]}

    # Replace the table population line with the following:
    images, filenames = populate_if_different(**aws_config, **db_config)

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
            print("Possible Outlier images:")
            outlier_filenames = [filename for filename, score in outliers]
            outlier_scores = [score for filename, score in outliers]
            update_outlier_scores(PG_database=db_config['PG_database'], PG_user=db_config['PG_user'],
                                  PG_password=db_config['PG_password'],
                                  PG_host=db_config['PG_host'], PG_port=db_config['PG_port'], filenames=outlier_filenames,
                                  outlier_scores=outlier_scores)

            outliers_sorted = sorted(outliers, key=lambda x: x[1], reverse=True)
            for filename, score in outliers_sorted:
                print(f"{filename} - Score: {score}")

            # Export all image scores to a separate file
            scores_file_path = "image_scores.txt"
            with open(scores_file_path, "w") as file:
                for filename, score in outliers_sorted:
                    file.write(f"{filename} - Score: {score}\n")

            print(f"All image scores exported to {scores_file_path}.")
