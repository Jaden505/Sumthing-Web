from PIL import Image
import os


def convert_png_to_jpg(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            joined_path = os.path.join(directory, filename)
            im = Image.open(joined_path)
            name = filename.split(".")[0] + '.JPG'
            rgb_im = im.convert('RGB')
            rgb_im.save(os.path.join(directory, name))
            os.remove(joined_path)
            continue
        else:
            continue


def resizer(picture_path):
    try:
        cwd = os.getcwd()
        img = Image.open(picture_path)

        # format to 65x65
        new_img = img.resize((65, 65))
        new_img.save(f'{os.path.splitext(picture_path)[0]}_small{os.path.splitext(picture_path)[1]}', 'JPEG')

        # format to 300x300
        new_img = img.resize((300, 300))
        new_img.save(f'{os.path.splitext(picture_path)[0]}_medium{os.path.splitext(picture_path)[1]}', 'JPEG')
    except Exception as err:
        print(err)


def image_name_changer(directory, file_ends_with, dir_to_save_in):
    for folder_name in os.listdir(directory):
        for filename in os.listdir(os.path.join(directory, folder_name)):
            if filename.endswith(file_ends_with):
                joined_path = os.path.join(directory, folder_name, filename)
                im = Image.open(joined_path)
                name = folder_name + "_" + filename.split(".")[0] + '.JPG'
                try:
                    im.save(os.path.join(dir_to_save_in, name))
                except Exception as err:
                    print('Something went wrong trying to save the updated image.')

                # os.remove(joined_path)
                continue
            else:
                continue

