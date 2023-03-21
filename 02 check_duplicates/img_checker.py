import hashlib
import os
from PIL import Image, ImageStat

from db_CRUD import update_image_score


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

def get_hash(img_path):
    # This function will return the md5 checksum for any input image.
    with open(img_path, "rb") as f:
        img_hash = hashlib.md5()
        while chunk := f.read(8192):
            img_hash.update(chunk)
    return img_hash.hexdigest()


def find_duplicates(dir_name):
    invalid_files = []
    # loop through images, assign hash value and check to see if hash value is double.
    hash_keys = dict()
    cwd = os.getcwd()
    for filename in os.listdir(dir_name):
        filepath = os.path.join(cwd, dir_name, filename)
        if os.path.isfile(filepath):
            filehash = get_hash(filepath)
            if filehash not in hash_keys:
                hash_keys[filehash] = filename
            else:
                file_dup = hash_keys[filehash]
                invalid_files.append([filename, file_dup])
                update_image_score(filename, 1, 3)
                update_image_score(file_dup, 1, 3)
                print(f"found duplicate hash: {filename} == {file_dup}")
    return invalid_files


def find_mean(imgPath):
    try:
        img = Image.open(imgPath)
        return ImageStat.Stat(img).mean
    except:
        print("could not open file, moving on")

def find_duplicate_mean(dir_name):
    invalid_files = []
    # loop through mean color values of all images and compare, remove duplicates if color values are identical
    mean_color_keys = dict()
    cwd = os.getcwd()
    for filename in os.listdir(dir_name):
        filepath = os.path.join(cwd, dir_name, filename)
        if os.path.isfile(filepath):
            mean = str(find_mean(filepath))
            if mean not in mean_color_keys:
                mean_color_keys[mean] = filename
            else:
                file_dup = mean_color_keys[mean]
                invalid_files.append([filename, file_dup])
                update_image_score(filename, 1, 4)
                update_image_score(file_dup, 1, 4)
                print(f"found duplicate mean color value: {filename} == {file_dup}")
    return invalid_files

