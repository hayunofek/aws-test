import psycopg2
import os


def open_connection_and_cursor():
    connection = None

    try:
        connection = psycopg2.connect(
                    user = os.environ['DB_USER'],
                    password = os.environ['DB_PASSWORD'],
                    host = os.environ['DB_HOST'],
                    port = os.environ['DB_PORT'],
            )
        cursor = connection.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error connection to PostgreSQL database", error)
        connection = None

    return connection, cursor


def close_connection(connection, cursor):
    if connection:
        if cursor:
            cursor.close()
        connection.close()


def get_book_from_db(cursor, book_id):
    cursor.execute(f"SELECT ID, name, price FROM books WHERE ID={book_id}")
    result = cur.fetchone()
    return result


def init_db(cursor):
    cursor.execute(""" CREATE TABLE IF NOT EXISTS books (
                       ID INT GENERATED ALWAYS AS IDENTITY,
                       name VARCHAR NOT NULL,
                       price VARCHAR NOT NULL,
                       PRIMARY KEY (ID)) """)
