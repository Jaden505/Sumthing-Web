import os

from db_CRUD import update_image_score
from helper_checker import *


def find_corrupted(dir):
    invalid_files = []
    # check for invalid files and append them to invalid list
    for image in os.listdir(dir):
        img_path = os.path.join(dir, image)
        im = None
        try:
            im = Image.open(img_path)
            im.verify()
            im.close()
        except(IOError, OSError):
            invalid_files.append(image)
            print("found corrupt file: ", image)
    return invalid_files


def find_duplicate_coordinates(filepath, filename, invalid_files, coordinate_keys):
    metadata =

    if check_within_one_meter(coordinate_keys.keys(), mean[0], mean[1]):
        file_dup = coordinate_keys[mean]
        invalid_files.append([filename, file_dup])
        update_image_score(filename, 1, 2)
        update_image_score(file_dup, 1, 2)
        print(f"found duplicate coordinates nearby: {filename} == {file_dup}")
    else:
        coordinate_keys[mean] = filename

    return coordinate_keys, invalid_files


def find_duplicate_mean(filepath, filename, invalid_files, mean_color_keys):
    mean = str(find_mean(filepath))
    if mean in mean_color_keys:
        file_dup = mean_color_keys[mean]
        invalid_files.append([filename, file_dup])
        update_image_score(filename, 1, 4)
        update_image_score(file_dup, 1, 4)
        print(f"found duplicate mean color value: {filename} == {file_dup}")
    else:
        mean_color_keys[mean] = filename

    return mean_color_keys, invalid_files


def find_duplicate_hash(filepath, filename, invalid_files, hash_keys):
    filehash = get_hash(filepath)
    if filehash in hash_keys:
        file_dup = hash_keys[filehash]
        invalid_files.append([filename, file_dup])
        update_image_score(filename, 1, 3)
        update_image_score(file_dup, 1, 3)
        print(f"found duplicate hash: {filename} == {file_dup}")
    else:
        hash_keys[filehash] = filename

    return hash_keys, invalid_files


def find_duplicates(dir_name):
    """
    Find duplicates of images in directory by compring mean color values,
    hash of pixels, near locations, and time taken.
    """
    invalid_files = []
    mean_color_keys = {}
    hash_keys = {}
    coordinate_keys = {}

    cwd = os.getcwd()

    for filename in os.listdir(dir_name):
        filepath = os.path.join(cwd, dir_name, filename)
        if os.path.isfile(filepath):
            mean_color_keys, invalid_files = find_duplicate_mean(filepath, filename, invalid_files, mean_color_keys)
            hash_keys, invalid_files = find_duplicate_hash(filepath, filename, invalid_files, hash_keys)

    return invalid_files

