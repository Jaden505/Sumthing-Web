import os

from helper_checker import *
from AWS_CRUD import update_image_score, get_metadata_from_image, move_image_within_s3_bucket

def find_corrupted(aws_folder, local_folder):
    invalid_files = []
    # check for invalid files and append them to invalid list
    for image in os.listdir(local_folder):
        img_path = os.path.join(local_folder, image)
        try:
            im = Image.open(img_path)
            im.verify()
            im.close()
        except(IOError, OSError):
            invalid_files.append(image)

            # move invalid file to invalid folder and remove locally
            move_image_within_s3_bucket(aws_folder, 'InvalidImages', image)
            os.remove(img_path)

            print("found corrupt file: ", image)

    return invalid_files


def find_duplicate_coordinates(aws_folder, metadata, filename, invalid_files, coordinate_keys):
    location = (float(metadata['latitude']), float(metadata['longitude']))
    nearby = check_within_one_meter(coordinate_keys.keys(), location[0], location[1])

    if nearby is not None:
        file_dup = coordinate_keys[nearby]
        invalid_files.append([filename, file_dup])
        update_image_score(os.path.join(aws_folder, filename), 1, 'score_weather')
        update_image_score(os.path.join(aws_folder, file_dup), 1, 'score_weather')
        print(f"found duplicate coordinates nearby: {filename} == {file_dup}")
    else:
        coordinate_keys[location] = filename

    return coordinate_keys, invalid_files


def find_duplicate_time(aws_folder, metadata, filename, invalid_files, time_keys):
    time = metadata['taken_date']
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    date_times = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f') for x in time_keys.keys()]
    quickly = check_within_10_seconds(date_times, time)

    if quickly is not None:
        file_dup = time_keys[quickly.strftime('%Y-%m-%d %H:%M:%S.%f')]
        invalid_files.append([filename, file_dup])
        update_image_score(os.path.join(aws_folder, filename), 1, 'score_tree_not_tree')
        update_image_score(os.path.join(aws_folder, file_dup), 1, 'score_tree_not_tree')
        print(f"found duplicate time: {filename} == {file_dup}")
    else:
        time_keys[time.strftime('%Y-%m-%d %H:%M:%S.%f')] = filename

    return time_keys, invalid_files


def find_duplicate_mean(aws_folder, filepath, filename, invalid_files, mean_color_keys):
    mean = str(find_mean(filepath))
    if mean in mean_color_keys:
        file_dup = mean_color_keys[mean]
        invalid_files.append([filename, file_dup])
        update_image_score(os.path.join(aws_folder, filename), 1, 'score_rgb_image')
        update_image_score(os.path.join(aws_folder, file_dup), 1, 'score_rgb_image')
        print(f"found duplicate mean color value: {filename} == {file_dup}")
    else:
        mean_color_keys[mean] = filename

    return mean_color_keys, invalid_files


def find_duplicate_hash(aws_folder, filepath, filename, invalid_files, hash_keys):
    filehash = get_hash(filepath)
    if filehash in hash_keys:
        file_dup = hash_keys[filehash]
        invalid_files.append([filename, file_dup])
        update_image_score(os.path.join(aws_folder, filename), 1, 'score_hash_image')
        update_image_score(os.path.join(aws_folder, file_dup), 1, 'score_hash_image')
        print(f"found duplicate hash: {filename} == {file_dup}")
    else:
        hash_keys[filehash] = filename

    return hash_keys, invalid_files


def find_duplicates(aws_folder, local_folder):
    """
    Find duplicates of images in directory by compring mean color values,
    hash of pixels, near locations, and time taken.
    """
    invalid_files = []
    mean_color_keys = {}
    hash_keys = {}
    coordinate_keys = {}
    time_keys = {}

    cwd = os.getcwd()

    for filename in os.listdir(local_folder):
        filepath = os.path.join(cwd, local_folder, filename)
        if os.path.isfile(filepath):
            mean_color_keys, invalid_files = find_duplicate_mean(aws_folder, filepath, filename, invalid_files, mean_color_keys)
            hash_keys, invalid_files = find_duplicate_hash(aws_folder, filepath, filename, invalid_files, hash_keys)

            try:
                metadata = get_metadata_from_image(os.path.join(aws_folder, filename))

                coordinate_keys, invalid_files = find_duplicate_coordinates(aws_folder, metadata, filename, invalid_files,
                                                                            coordinate_keys)
                time_keys, invalid_files = find_duplicate_time(aws_folder, metadata, filename, invalid_files, time_keys)
            except Exception as e:
                print("Error with metadata: ", e)
                continue

    return invalid_files
