from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker
from db_ORM import Base, Batch
import dotenv, json, psycopg2

from helper_batch import get_center_of_batch, get_first_last_date_from_batch
from db_ORM import ProofTable

dotenv.load_dotenv()


with open('../config.json') as f:
    config = json.load(f)

url = f'postgresql+psycopg2://{config["PG_user"]}:{config["PG_password"]}@{config["PG_host"]}:{config["PG_port"]}/{config["PG_database"]}'


def connect_database(url):
    try:
        engine = create_engine(url)
        conn = engine.connect()
        return engine, conn

    except Exception:
        print("Connection couldn't be made with database")
        return None, None

connect_database(url)

def create_tables(engine):
    Base.metadata.create_all(engine)


def get_metadata(url, image_name):
    engine, conn = connect_database(url)
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(ProofTable.proof_date, ProofTable.latitude, ProofTable.longitude).filter(ProofTable.img_name == image_name).first()
    session.close()
    conn.commit()
    conn.close()

    return results


def insert_all_images(url, picture_list):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        session.add_all(picture_list)
        session.commit()
        session.close()
    return None


def insert_batch_to_db(url, batchDict):
    engine, conn = connect_database(url)

    batch_key = batchDict['batch_key']
    batch_name = batchDict['zipname']

    first_date, last_date = get_first_last_date_from_batch(batch_name)
    center_lon, center_lat = get_center_of_batch(batch_name)

    stmt = (
        insert(Batch).
            values(batch_key=batch_key, batch_name=batch_name, center_long=center_lon, center_lat=center_lat,
                   first_photo_upload=first_date,
                   last_photo_upload=last_date)
    )
    conn.execute(stmt)
    conn.close()


def insert_batches_to_db(url, ls_zip):
    for zip in ls_zip:
        insert_batch_to_db(url, zip)


