import os, shutil
from datetime import datetime
import zipfile

now = datetime.now()


def extract_all(dir, columns):
    dict = {}
    ext = ('.zip')
    now = datetime.now()

    ls_zip = []
    for filename in os.listdir(dir):
        zip_path = os.path.join(os.getcwd(), "zipimages", filename)
        batchid = filename.split('_', 1)[0]
        dict[columns[0]] = batchid

        zipname = filename.split('.', 1)[0]
        dict[columns[1]] = zipname

        dict[columns[2]] = now

        ls_zip.append(dict)
        if filename.endswith(ext):
            try:
                z = zipfile.ZipFile(zip_path, mode='r')
                z.extractall(os.path.join(os.getcwd(), 'zipimages', zipname))
                z.close()
            except Exception as err:
                print(err)
        else:
            continue
    return ls_zip


def rename_all(dirname):
    for root, dirs, files in os.walk(dirname):
        for file in files:
            if os.path.split(root)[1] != dirname:
                dir = os.path.split(root)[1]
                batch = dir.split('_', 1)[0]
                os.rename(os.path.join(root, file), os.path.join(root, batch + '_' + file))
    return


def clean_up(dirname):
    cwd = os.getcwd()
    dir_path = os.path.join(cwd, dirname)

    shutil.rmtree(dir_path)
    os.makedirs(dir_path)

