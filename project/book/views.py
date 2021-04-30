from flask import Blueprint, jsonify, request
from project.models import Book, User
from project import db, token_required


book = Blueprint('book',__name__)


# Book Routes
# This is the first and second route which gets all the book list of the current logged in user.
@book.route('/book', methods = ['GET', 'POST'])
@token_required
def get_or_create_books(current_user):
    if request.method == 'GET':
        books = Book.query.filter_by(user_id = current_user.id)
        all_books = []
    
        for book in books:
            book_data = {}
            book_data['id'] = book.id
            book_data['name'] = book.name
            book_data['author'] = book.author
            book_data['complete'] = book.complete
            all_books.append(book_data)

        return jsonify({"Book's" : all_books})

    elif request.method == 'POST':
        data = request.get_json()
        new_book = Book(name = data['name'], author = data['author'], complete = False, user_id = current_user.id)
        db.session.add(new_book)
        db.session.commit()

        return jsonify({'message' : 'Book added to library !!'})

# This is the third route which gets a single book of the current logged in user.
@book.route('/book/<book_id>', methods = ['GET'])
@token_required
def get_one_book(current_user, book_id):
    book = Book.query.filter_by(id = book_id).first()
    if not book:
        return jsonify({'message' : 'No Book found !!'})
    book_data = {}
    book_data['id'] = book.id
    book_data['name'] = book.name
    book_data['author'] = book.author
    book_data['complete'] = book.complete

    return jsonify({"Book" : book_data})


# This is the forth route which marks the selected book as completed for the current logged in user.
@book.route('/book/<book_id>', methods = ['PUT'])
@token_required
def complete_book(current_user, book_id):
    book = Book.query.filter_by(id = book_id).first()

    if not book:
        return jsonify({'message' : 'No Book found !!'})
    
    book.complete = True
    db.session.commit()

    return jsonify({'message' : 'Book Reading Completed !!'})

# This is the fifth route which deletes the specified book of the current logged in user.
@book.route('/book/<book_id>', methods = ['DELETE'])
@token_required
def delete_book(current_user, book_id):
    book = Book.query.filter_by(id = book_id).first()

    if not book:
        return jsonify({'message' : 'No book found !!'})
    
    db.session.delete(book)
    db.session.commit()

    return jsonify({'message' : 'Book Deleted !!'})