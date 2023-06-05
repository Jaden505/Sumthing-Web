from imagededup.methods import CNN


def duplicate_check_CNN(local_folder, req_threshold, invalid_files):
    cnn = CNN()
    encodings = cnn.encode_images(local_folder)
    duplicates = cnn.find_duplicates(encoding_map=encodings, scores=True, min_similarity_threshold=req_threshold)
    for key, value in duplicates.items():
        if len(value) > 0:
            for image, percentage in value:
                invalid_files.append((key, image))
            print(f'{key} is a duplicate of {image} with {percentage}% similarity')

    return invalid_files