from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

import dotenv

from db_ORM import Batch, AllImage
from config import load_config


dotenv.load_dotenv()
config = load_config("../config.json")
url = f'postgresql://{config["PG_user"]}:{config["PG_password"]}@{config["PG_host"]}:{config["PG_port"]}/{config["PG_database"]}'


def connect_database(url):
    try:
        engine = create_engine(url, echo = False) #echo=True
        conn = engine.connect()
        return engine, conn

    except Exception as err:
        print(err)
        return None, None


def select_all_comparable_image():
    engine, conn = connect_database(url)

    Session = sessionmaker(bind = engine)
    session = Session()

    results = session.query(AllImage).filter(AllImage.score_duplicate_tree != None).order_by(AllImage.score_duplicate_tree)
    return results

def get_first_last_date_from_batch():
    # new code
    # get from db
    first_datetime='1900-01-01'
    last_datetime='9999-12-31'
    # print(last_datetime)
    # print(first_datetime)

    return first_datetime, last_datetime


def get_center_of_batch():
    # new code
    # get from db
    center_lon=-1
    center_lat=-1

    return center_lon, center_lat
  
def select_lat_lon(url, batch_request):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()
        results = list()
        for key in batch_request:
            stmt = select(
                AllImage.proof_image_name,
                AllImage.latitude,
                AllImage.longitude,
                AllImage.proof_date,
                AllImage.batch_key,
                AllImage.score_duplicate_tree
            ).where(AllImage.batch_key == key).order_by(AllImage.proof_date)
            results.append(session.execute(stmt))
        return results


def select_batches(url):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        stmt = select(
            Batch.batch_name
        ).order_by(Batch.batch_name)

        result = session.execute(stmt)
        return result


def select_batches_metadata(url, batch_request):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        stmt = select(
            Batch.batch_key,
            Batch.batch_name,
            Batch.center_lat,
            Batch.center_long,
            Batch.first_photo_upload,
            Batch.first_photo_upload,
            AllImage.proof_image_name,
            AllImage.proof_medium
        ).join(Batch, Batch.batch_key == AllImage.batch_key)

        result = session.execute(stmt)
        return result

def select_batches_totalscore(url):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        stmt = select(
            Batch.batch_key,
            Batch.batch_name,
            AllImage.proof_image_name,
            AllImage.score_duplicate_tree,
        ).join(Batch, Batch.batch_key == AllImage.batch_key)

        result = session.execute(stmt)
        return result

