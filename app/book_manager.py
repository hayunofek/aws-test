from flask import Flask
import db_utils as db

connection, cursor = db.open_connection_and_cursor()
db.init_db(cursor)
db.close_connection(connection, cursor)

app = Flask(__name__)


@app.route("/books", methods=['GET'])
def get_all_books():
    return "get_all_books"


@app.route("/books/<book_id>", methods=['GET'])
def get_book(book_id):
    return "get_book"


# POST
@app.route("/books", methods=['POST'])
def add_book():
    data = request.form
    return "post books"


# PUT
@app.route("/books/<book_id>", methods=['PUT'])
def edit_book(book_id):
    return "put book"


# DELETE
@app.route("/books/<book_id>", methods=['DELETE'])
def delete_book(book_id):
    return "put delete"

@app.route("/")
def health_check():
    return "ok"
