import os
from imagededup.methods import CNN

# Set the path for your images directories
plastic_dir = '/Users/ayoubezzaouia/Downloads/Pictures/plastic/Batch 1'
tree_dir = '/Users/ayoubezzaouia/Downloads/Pictures/trees'

# Set the similarity threshold for identifying duplicates
threshold = 0.7

# Initialize a CNN model
cnn = CNN()

# Generate image encodings for each directory
encodings_plastic = cnn.encode_images(plastic_dir)
encodings_tree = cnn.encode_images(tree_dir)


# Find outlier images in each directory
def find_outlier(image_dir, threshold):
    image_filenames = os.listdir(image_dir)
    outlier_image = cnn.find_outliers(image_dir=image_dir, encoding_map=encodings_plastic, threshold=threshold)
    return outlier_image


# Print the results
print(f"Outlier image in plastic directory: {find_outlier(plastic_dir, threshold)}")
print(f"Outlier image in tree directory: {find_outlier(tree_dir, threshold)}")
