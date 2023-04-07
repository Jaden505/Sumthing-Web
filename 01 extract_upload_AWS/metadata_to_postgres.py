from img_to_AWS_to_db import get_image_metadata
import psycopg2, os


def images_from_dir_to_db(image_dir):
    # Loop through each file in the directory
    for filename in os.listdir(image_dir):
        filepath = os.path.join(image_dir, filename)

        try:
            metadata = get_image_metadata(filepath)
        except:
            print(f"Error extracting metadata from {filename}")
            continue

        batch_key = metadata['batch_key']

        insert = insert_query("INSERT INTO batch (batch_key) VALUES (%s)", (batch_key,))
        if not insert:
            print(f"Batch {batch_key} already exists")
            continue

        query = "INSERT INTO proof ("
        columns = []
        values = []
        for key, value in metadata.items():
            columns.append(key)
            values.append(str(value))
        query += ", ".join(columns) + ") VALUES ("
        query += ", ".join(["%s" for _ in range(len(values))]) + ")"

        insert = insert_query(query, tuple(values))
        if not insert:
            print(f"Image {filename} already exists")
            continue


def insert_query(query, values):
    try:
        cur.execute(query, tuple(values))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False

    return True

if __name__ == "__main__":
    # Initialise the database connection
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="",
        password=""
    )
    cur = conn.cursor()

    images_from_dir_to_db('../Pictures/plastic/Batch 1')
    images_from_dir_to_db('../Pictures/trees')

    # Close the database connection
    cur.close()
    conn.close()
