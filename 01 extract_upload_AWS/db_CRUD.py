from sqlalchemy import create_engine
from sqlalchemy import delete, text, insert
from sqlalchemy.orm import sessionmaker

from db_ORM import Base
from db_ORM import Batch, AllImage
from helper_batch import get_center_of_batch, get_first_last_date_from_batch

from config import load_config

config = load_config("../config.json")
url = f'postgresql://{config["user"]}:{config["password"]}@{config["host"]}:{config["port"]}/{config["database"]}'


def connect_database(url):
    try:
        engine = create_engine(url)
        conn = engine.connect()
        return engine, conn

    except Exception as err:
        print(err)
        return None, None


def create_tables(engine):
    Base.metadata.create_all(engine)


def upload_db_orm(url, picture_list):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        session.add_all(picture_list)
        session.commit()
    return None


def insert_all_images(url, picture_list):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        session.add_all(picture_list)
        session.commit()
    return None


def select_all_comparable_image():
    engine, conn = connect_database(url)

    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(AllImage).filter(AllImage.score_duplicate_tree != None).order_by(
        AllImage.score_duplicate_tree)
    return results


def delete_image(proof_key):
    engine, conn = connect_database(url)

    stmt = (
        delete(AllImage).
        where(AllImage.proof_key == proof_key)
    )

    conn.execute(stmt)

    return True


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


def insert_batches_to_db(url, ls_zip):
    for zip in ls_zip:
        insert_batch_to_db(url, zip)


def load_images_to_lz(df_images, engine):
    df_images.to_sql(name='orderline_contribution2', con=engine, if_exists='append', index=False)
    return None


def update_orderline_contribution(engine):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute('CALL pr_update_orderline_contribution_proof')
    connection.commit()
    cursor.close()
    connection.close()
    return None


def drop_lz_image_proof(engine):
    connection_to = engine.connect()
    connection_to.execute(text("DROP TABLE IF EXISTS lz_image_proof"))
    return None


def log_zip_images(df_zip, engine):
    df_zip.to_sql(name='log_zip_images', con=engine, if_exists='append', index=False)
    return None
