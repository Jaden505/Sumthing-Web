import numpy as np
import pywt
import cv2
from skimage.feature import local_binary_pattern
from keras.applications.vgg16 import VGG16, preprocess_input


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
