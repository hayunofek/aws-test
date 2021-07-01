from flask import Flask, request, Response
import traceback
import json
import utils as utils

utils.startup_db()

app = Flask(__name__)


@app.route("/books", methods=['GET'])
def get_all_books():
    """
    This function returns all books
    :return: Response object
    """
    connection, cursor = None, None
    try:
        connection, cursor = utils.open_connection_and_cursor()
        books = utils.get_all_books_from_db(cursor)
        return Response(json.dumps({"status": "ok", "message": books}), status=200, mimetype='application/json')
    except (Exception, utils.psycopg2.Error) as e:
        print(f"An excepct occured, exception: {e}")
        connection = None
        return Response(json.dumps({"status": "error", "message": "an error has occured"}), status=500,
                        mimetype="application/json")
    finally:
        if connection:
            utils.close_connection(connection, cursor)


@app.route("/books/<book_id>", methods=['GET'])
def get_book(book_id):
    """
    This function retrieves a book by its id
    :param book_id: int
    :return: Response object
    """
    connection, cursor = None, None
    try:
        connection, cursor = utils.open_connection_and_cursor()
        if not book_id.isnumeric():
            return Response(json.dumps({"status": "error", "message": "book_id needs to be a number"}), status=400,
                            mimetype="application/json")
        book_object = utils.get_book_from_db(cursor, book_id)
        return Response(json.dumps({"status": "ok", "message": book_object}), status=200, mimetype="application/json")
    except (Exception, utils.psycopg2.Error) as e:
        print(f"An excepct occured, exception: {e}")
        connection = None
        return Response(json.dumps({"status": "error", "message": "an error has occured"}), status=500,
                        mimetype="application/json")
    finally:
        if connection:
            utils.close_connection(connection, cursor)


# POST
@app.route("/books", methods=['POST'])
def add_book():
    """
    This function adds a book to the database given a book object over a POST request
    book object should look like this: {'name': str, 'price': str}
    :return: Response object
    """
    connection, cursor = None, None
    try:
        connection, cursor = utils.open_connection_and_cursor()
        data = request.json
        print(data)
        if not utils.is_book_object_valid(data):
            return Response(json.dumps({"status": "error",
                                        "message": "book_object sent is invalid. It should look like this: {'price': "
                                                   "str, "
                                                   "'name': str}"}),
                            status=400, mimetype="application/json")
        book_id = utils.add_book_to_db(cursor, data)
        return Response(json.dumps({"status": "ok", "message": f"Book id {book_id} was added successfully"}),
                        status=200,
                        mimetype="application/json")
    except (Exception, utils.psycopg2.Error) as e:
        print(f"An excepct occured, exception: {e}")
        connection = None
        return Response(json.dumps({"status": "error", "message": "an error has occured"}), status=500,
                        mimetype="application/json")
    finally:
        if connection:
            utils.close_connection(connection, cursor)


@app.route("/books", methods=['PUT'])
def edit_book():
    """
    This function edits a book given a book object over PUT
    book object should look like this: {'name': str, 'price': str, 'ID': int}
    :return: Response object
    """
    connection, cursor = None, None
    try:
        connection, cursor = utils.open_connection_and_cursor()
        data = request.json
        print(data)
        if not utils.is_book_object_valid(data, should_contain_id=True):
            return Response(json.dumps({"status": "error",
                                        "message": "book_object sent is invalid. It should look like this: {'ID': "
                                                   "int, 'price': "
                                                   "str, 'name': str}"}),
                            status=400, mimetype="application/json")
        book_id = utils.edit_book(cursor, data)
        if book_id:
            return Response(json.dumps({"status": "ok", "message": f"Book id {book_id} was edited successfully"}),
                            status=200,
                            mimetype="application/json")
        return Response(json.dumps({"status": "ok", "message": f"Book id {data['ID']} doesn't exist"}),
                        status=200,
                        mimetype="application/json")
    except (Exception, utils.psycopg2.Error) as e:
        traceback.print_exc()
        print(f"An excepct occured, exception: {e}")
        connection = None
        return Response(json.dumps({"status": "error", "message": "an error has occured"}), status=500,
                        mimetype="application/json")
    finally:
        if connection:
            utils.close_connection(connection, cursor)


@app.route("/books/<book_id>", methods=['DELETE'])
def delete_book(book_id):
    """
    This function deletes a book given a book_id
    :param book_id: integer
    :return: Response object
    """
    connection, cursor = None, None
    try:
        connection, cursor = utils.open_connection_and_cursor()
        if not book_id.isnumeric():
            return Response(json.dumps({"status": "error", "message": "book_id needs to a number"}),
                            status=400, mimetype="application/json")
        utils.delete_book_from_db(cursor, book_id)
        return Response(json.dumps({"status": "ok", "message": "Book removed successfully"}), status=200,
                        mimetype="application/json")
    except (Exception, utils.psycopg2.Error) as e:
        print(f"An excepct occured, exception: {e}")
        connection = None
        return Response(json.dumps({"status": "error", "message": "an error has occured"}), status=500,
                        mimetype="application/json")
    finally:
        if connection:
            utils.close_connection(connection, cursor)


@app.route("/")
def health_check():
    """
    This function is an endpoint for checking the health of the application
    """
    return "ok"
