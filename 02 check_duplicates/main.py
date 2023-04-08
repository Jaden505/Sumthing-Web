import os
import dotenv

from duplicate_check_CNN import duplicate_check_CNN
from img_checker import find_corrupted, find_duplicates, find_duplicate_mean

from helper_images import clean_up

dotenv.load_dotenv()

# postgres database
DATABASE_TO_URI = 'postgresql://@localhost:5432/postgres'


# aws image bucket
# ACCESS_KEY = os.environ['ACCESS_KEY']
# SECRET_KEY = os.environ['SECRET_KEY']
# bucketname = os.environ['bucketname']


def main(dirname):
    # ## DOWNLOAD FROM AWS
    # dirname = 'AWSimages'
    # awspathname = '.\\' + dirname

    for directory in os.listdir(dirname):
        path = os.path.join(os.getcwd(), dirname, directory)
        if os.path.isdir(path):
            find_corrupted(path)
            find_duplicates(path)
            find_duplicate_mean(path)

            # check_if_tree(path)
            # check if is look - a - like  
            duplicate_check_CNN(path, 0.85)

    # Remove all files from folder
    clean_up(dirname)


main('../Pictures')
