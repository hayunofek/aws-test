import os

from flask import Flask
from db_utils import *


app = Flask(__name__)

@app.route("/books", methods = ['GET'])
def get_all_books():
    pass

@app.route("/books/<book_id>", methods = ['GET'])
def get_book(book_id):
    pass

# POST
@app.route("/books", methods = ['POST'])
def add_book():
    data = request.form
    pass

# PUT
@app.route("/books/<book_id>", methods = ['PUT'])
def edit_book(book_id):
    pass

# DELETE
@app.route("/books/<book_id>", methods = ['DELETE'])
def delete_book(book_id):
    pass
