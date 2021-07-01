import psycopg2
import os


def open_connection_and_cursor():
    connection, cursor = None, None

    try:
        connection = psycopg2.connect(
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
            dbname='postgres'
        )
        connection.set_session(autocommit=True)
        cursor = connection.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error connection to PostgreSQL database", error)
        connection = None

    return connection, cursor


def close_connection(connection, cursor):
    if connection:
        connection.commit()
        if cursor:
            cursor.close()
        connection.close()


def add_book_to_db(cursor, book_object):
    """
    This function adds a book to the database, this function assumes book_object is valid
    :param cursor: PostgreSQL connection cursor
    :param book_object: A book object dictionary without ID {'name': str, 'price': str}
    :return: ID (int) of book
    """
    sql_query = "INSERT INTO books(name, price) VALUES (%s, %s) RETURNING ID"
    cursor.execute(sql_query, (book_object['name'], book_object['price']))
    result = cursor.fetchone()[0]
    return result


def edit_book(cursor, book_object):
    """
    This function edits a book in the database, this function assumes book_object is valid
    :param cursor: PostgreSQL connection cursor
    :param book_object: A book object dictionary with ID {'name': str, 'price': str, 'ID': int}
    :return: ID (int) of book
    """
    sql_query = f"UPDATE books SET name = %s, price = %s WHERE ID = {book_object['ID']} RETURNING ID"
    cursor.execute(sql_query, (book_object['name'], book_object['price']))
    result = cursor.fetchone()
    if result:
        result = result[0]
    return result


def get_book_from_db(cursor, book_id):
    cursor.execute(f"SELECT ID, name, price FROM books WHERE ID={book_id}")
    result = cursor.fetchone()
    result_dict = {}
    if result:
        result_dict['ID'] = result[0]
        result_dict['name'] = result[1]
        result_dict['price'] = result[2]
    return result_dict


def init_db(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS books (ID INT GENERATED ALWAYS AS IDENTITY, name VARCHAR NOT NULL, 
    price VARCHAR NOT NULL, PRIMARY KEY (ID)) """)


def startup_db():
    connection, cursor = open_connection_and_cursor()
    if connection and cursor:
        init_db(cursor)
    close_connection(connection, cursor)


def get_all_books_from_db(cursor):
    cursor.execute("SELECT ID, name, price FROM books")
    results = cursor.fetchall()
    results_json = []
    for result in results:
        results_json.append({'ID': result[0],
                             'name': result[1],
                             'price': result[2]})

    return results_json


def delete_book_from_db(cursor, book_id):
    print(book_id)
    print(type(book_id))
    sql_query = f"DELETE FROM books WHERE ID = {book_id}"
    cursor.execute(sql_query)


def is_book_object_valid(book_object, should_contain_id=False):
    print(book_object)
    is_valid = True
    if should_contain_id:
        is_valid = is_valid and 'ID' in book_object and isinstance(book_object['ID'], int)
    is_valid = is_valid and 'name' in book_object and isinstance(book_object['name'], str)
    is_valid = is_valid and 'price' in book_object and isinstance(book_object['price'], str)
    print(is_valid)
    return is_valid
