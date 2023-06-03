import os
import dotenv

from duplicate_check_CNN import duplicate_check_CNN
from img_checker import find_corrupted, find_duplicates
from move_duplicates import move_duplicate_images
from AWS_CRUD import update_image_score_duplicate

from botocore.exceptions import ClientError

dotenv.load_dotenv()

aws_folder = 'AllImages'
aws_duplicate_folder = 'DuplicateImages'
local_folder = '../zipimages'


def main():
    find_corrupted(aws_folder, local_folder)
    invalid_files = find_duplicates(aws_folder, local_folder)
    invalid_files = duplicate_check_CNN(local_folder, 0.85, invalid_files)

    # move duplicates in AWS bucket and remove locally
    for file in invalid_files:
        img, dup, score_name = file[0], file[1], file[2]
        img_path = os.path.join(aws_folder, img)
        dup_path = os.path.join(aws_folder, dup)

        # If score is in the file, update it to the certainty of the CNN on being a duplicate else set to 1 (100%)
        if len(file) == 4:
            score = file[3]
            update_image_score_duplicate(os.path.join(aws_folder, img), os.path.join(aws_folder, dup), score, score_name)
        else:
            update_image_score_duplicate(img_path, dup_path, 1, score_name)

        move_duplicate_images(img, dup, aws_folder, aws_duplicate_folder, local_folder)


if __name__ == '__main__':
    main()
