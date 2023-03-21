from PIL import Image
from imagededup.methods import CNN

import os

from db_CRUD import update_image_score



def duplicate_check_CNN(path,  req_threshold):
    cnn = CNN()
    encodings = cnn.encode_images(path)
    duplicates = cnn.find_duplicates(encoding_map=encodings, scores=True, min_similarity_threshold=req_threshold)
    for key, value in duplicates.items():
        if len(value) > 0:
            for image, percentage in value:
                update_image_score(key, percentage, 2)



