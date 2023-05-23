from sqlalchemy import create_engine
from sqlalchemy import delete, update
from sqlalchemy.orm import sessionmaker
from db_ORM import Base
import dotenv

from db_ORM import AllImage

dotenv.load_dotenv()

user = ''
password = ''
host = 'localhost'
port = '5432'
database = 'postgres'

url = f'postgresql://{user}:{password}@{host}:{port}/{database}'


def connect_database(url):
    try:
        engine = create_engine(url)
        conn = engine.connect()
        return engine, conn

    except Exception as err:
        print(err)
        return None, None


engine, conn = connect_database(url)


def create_tables(engine):
    Base.metadata.create_all(engine)


def upload_db_orm(picture_list):
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        session.add_all(picture_list)
        session.commit()
    return None


def upload_all_images(picture_list):
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        session.add_all(picture_list)
        session.commit()
    return None


def select_all_comparable_image():
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(AllImage).filter(AllImage.score_duplicate_tree != None).order_by(
        AllImage.score_duplicate_tree)
    return results


def delete_image(proof_key):
    stmt = (
        delete(AllImage).
        where(AllImage.proof_key == proof_key)
    )

    conn.execute(stmt)

    return True


def get_metadata(image_name):
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(AllImage.proof_date, AllImage.latitude, AllImage.longitude).filter(AllImage.proof_image_name == image_name).first()
    session.close()

    return results


def update_image_score(image_name, score, index):
    """
    Image_name: Name of image to change. \n
    Score: Score for corresponding test. \n
    Index: \n
    1 = score_tree_not_tree,\n
    2 = score_duplicate_tree,\n
    3 = score_hash_image, \n
    4 = score_rgb_image, \n
    5 = score_weather\n
    6 = score_total
    :return: Updates correct line in database to show new score
    """
    score = float(score)
    updates = [
        update(AllImage).
        where(AllImage.proof_image_name == image_name).
        values(score_tree_not_tree=score),
        update(AllImage).
        where(AllImage.proof_image_name == image_name).
        values(score_duplicate_tree=score),
        update(AllImage).
        where(AllImage.proof_image_name == image_name).
        values(score_hash_image=score),
        update(AllImage).
        where(AllImage.proof_image_name == image_name).
        values(score_rgb_image=score),
        update(AllImage).
        where(AllImage.proof_image_name == image_name).
        values(score_weather=score),
        update(AllImage).
        where(AllImage.proof_image_name == image_name).
        values(score_total=score)
    ]

    stmt = updates[index - 1]
    conn.execute(stmt)
    conn.commit()
