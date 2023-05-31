from sqlalchemy import create_engine
from sqlalchemy import delete, update, insert
from sqlalchemy.orm import sessionmaker
from db_ORM import Base
import dotenv, json

from db_ORM import ProofTable, WeatherData

dotenv.load_dotenv()

with open('config.json') as f:
    config = json.load(f)

url = f'postgresql://{config["user"]}:{config["password"]}@{config["host"]}:{config["port"]}/{config["database"]}'


def connect_database(url):
    try:
        engine = create_engine(url)
        conn = engine.connect()
        return engine, conn

    except Exception:
        print("Connection couldn't be made with database")
        return None, None


engine, conn = connect_database(url)


def create_tables(engine):
    Base.metadata.create_all(engine)


def delete_image(proof_key):
    stmt = (
        delete(ProofTable).
        where(ProofTable.proof_key == proof_key)
    )

    conn.execute(stmt)
    conn.commit()

    return True


def get_metadata(image_name):
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(ProofTable.proof_date, ProofTable.latitude, ProofTable.longitude).filter(ProofTable.img_name == image_name).first()
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
        update(ProofTable).
        where(ProofTable.img_name == image_name).
        values(score_tree_not_tree=score),
        update(ProofTable).
        where(ProofTable.img_name == image_name).
        values(score_duplicate_tree=score),
        update(ProofTable).
        where(ProofTable.img_name == image_name).
        values(score_hash_image=score),
        update(ProofTable).
        where(ProofTable.img_name == image_name).
        values(score_rgb_image=score),
        update(ProofTable).
        where(ProofTable.img_name == image_name).
        values(score_weather=score),
        update(ProofTable).
        where(ProofTable.img_name == image_name).
        values(score_total=score)
    ]

    stmt = updates[index - 1]
    conn.execute(stmt)
    conn.commit()


def update_weather_check(geo_info):
    engine, conn = connect_database(url)
    cur = conn.cursor()

    # Create a database connection
    engine = create_engine('your_database_connection_string')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a new Image instance and set its attributes
    new_image = ProofTable(
        image_name=geo_info['image_name'],
        date_time=geo_info['date_time'],
        latitude=geo_info['latitude'],
        longitude=geo_info['longitude'],
        altitude=geo_info['altitude'],
        temperature=geo_info['temperature'],
        weather_desc=geo_info['weather_desc'],
        visibility=geo_info['visibility']
    )

    # Add the new_image instance to the session and commit the changes
    session.add(new_image)
    session.commit()

    cur.close()
    conn.close()    


def insert_weather_(batch_key2, date, weather, hour):
    engine, conn = connect_database(url)
    stmt = (insert(WeatherData).
            values(date=date,weather_desc=weather,three_hourly=hour, batch_key = batch_key2))
    conn.execute(stmt)

    conn.commit()
    conn.close()
