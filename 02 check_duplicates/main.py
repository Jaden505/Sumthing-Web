import os
import dotenv

from duplicate_check_CNN import duplicate_check_CNN
from img_checker import find_corrupted, find_duplicates
from move_duplicates import move_duplicate_images
from AWS_CRUD import update_image_duplicates

dotenv.load_dotenv()

aws_folder = 'AllImages'
aws_duplicate_folder = 'DuplicateImages'
local_folder = '../zipimages'


def main():
    find_corrupted(aws_folder, local_folder)
    invalid_files = find_duplicates(aws_folder, local_folder)
    invalid_files = duplicate_check_CNN(local_folder, 0.92, invalid_files)

    # move duplicates in AWS bucket and remove locally
    for file in invalid_files:
        img, dup = file[0], file[1]
        img_path = os.path.join(aws_folder, img)
        dup_path = os.path.join(aws_folder, dup)

        update_image_duplicates(img_path, dup_path)

    # move duplicates in AWS bucket and remove locally
    for file in invalid_files:
        img, dup = file[0], file[1]

        try:
            move_duplicate_images(img, dup, aws_folder, aws_duplicate_folder, local_folder)
        except Exception:
            print('File is already in duplicate folder')
            continue


if __name__ == '__main__':
    main()
