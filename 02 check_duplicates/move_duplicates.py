import os

from AWS_CRUD import move_image_within_s3_bucket


def move_duplicate_images(img, duplicate, aws_src_folder, aws_dst_folder, local_folder):
    cwd = os.getcwd()
    local_src = os.path.join(cwd, local_folder, img)
    local_dst = os.path.join(cwd, local_folder, duplicate)

    # move images to duplicate bucket folder
    move_image_within_s3_bucket(aws_src_folder, aws_dst_folder, img)
    move_image_within_s3_bucket(aws_src_folder, aws_dst_folder, duplicate)

    # remove locally
    os.remove(local_src)
    os.remove(local_dst)
