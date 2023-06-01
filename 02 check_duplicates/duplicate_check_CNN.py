import os

from imagededup.methods import CNN
from AWS_CRUD import update_image_score

def duplicate_check_CNN(aws_folder, local_folder, req_threshold):
    cnn = CNN()
    encodings = cnn.encode_images(local_folder)
    duplicates = cnn.find_duplicates(encoding_map=encodings, scores=True, min_similarity_threshold=req_threshold)
    for key, value in duplicates.items():
        if len(value) > 0:
            for image, percentage in value:
                update_image_score(os.path.join(aws_folder, key), percentage, 'score_duplicate_tree')
