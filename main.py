
from flask import Flask, jsonify, abort
from database import Book, Author, Session, AuthorBookLink, create_tables
from flask import request
from datetime import datetime
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)


@app.route('/books/<path:id>', methods=['GET'])
def get_book(id):
    book = Session.query(Book).filter(Book.id == id).first()

    if book:
        return jsonify({'id':book.id, 'title':book.title, 'created_at': book.created_at, 'updated_at' : book.updated_at })
    else:
        abort(404)


@app.route('/books', methods=['GET'])
def get_books():
    limit = request.args.get('limit')
    result = []
    books = Session.query(Book).order_by(Book.id)
    if limit:
        books = books.limit(limit)

    for book in books:
        result.append({'id':book.id, 'title':book.title, 'created_at': book.created_at, 'updated_at' : book.updated_at })

    return jsonify(books = result)


@app.route('/books', methods=['POST'])
def add_book():
    if not request.json or Session.query(Book).filter(Book.id == request.json['id']).first():
        abort(400)

    new_book = Book(id = request.json['id'],title = request.json['title'],created_at = datetime.now())
    Session.add(new_book)
    authors = request.json['authors_id']
    for author_id in authors:
        author = Session.query(Author).filter(Author.id == author_id)
        if not author:
            Session.rollback()
            return 'No author with id %i' % author_id
        Session.add(AuthorBookLink(author_id = author_id, book_id = request.json['id']))

    Session.commit()

    return 'OK', 200


@app.route('/books/<path:id>', methods=['PUT'])
def update_book(id):
    book = Session.query(Book).filter(Book.id == id)
    if not request.json or not book.first():
        abort(400)

    Session.query(AuthorBookLink).filter(AuthorBookLink.book_id == request.json['id']).delete()

    authors = request.json['authors_id']

    try:
        book.update({'id': request.json['id'], 'title': request.json['title'] , 'updated_at' : datetime.now()})
    except IntegrityError:
        Session.rollback()
        return 'Id currently exists', 400

    for author_id in authors:
        author = Session.query(Author).filter(Author.id == author_id)
        if not author:
            Session.rollback()
            return 'No author with id %i' % author_id
        Session.add(AuthorBookLink(author_id = author_id, book_id = request.json['id']))

    Session.commit()

    return 'OK', 200


@app.route('/books/<path:id>', methods=['DELETE'])
def delete_book(id):
    Session.query(AuthorBookLink).filter(AuthorBookLink.book_id == id).delete()
    Session.query(Book).filter(Book.id == id).delete()
    Session.commit()

    return 'OK', 200


@app.route('/authors/<path:id>', methods=['GET'])
def get_author(id):
    author = Session.query(Author).filter(Author.id == id).first()

    if author:
        return jsonify({'id': author.id, 'name': author.name, 'created_at': author.created_at, 'updated_at' : author.updated_at})
    else:
        abort(404)


@app.route('/authors', methods=['GET'])
def get_authors():
    limit = request.args.get('limit')
    result = []
    authors = Session.query(Author).order_by(Author.id)
    if limit:
        authors = authors.limit(limit)

    for author in authors:
        result.append({'id': author.id, 'name': author.name, 'created_at': author.created_at, 'updated_at' : author.updated_at })

    return jsonify(authors = result)


@app.route('/authors', methods=['POST'])
def add_author():
    if not request.json or Session.query(Author).filter(Author.id == request.json['id']).first():
        abort(400)
    new_author = Author(id = request.json['id'],name = request.json['name'], created_at = datetime.now())
    Session.add(new_author)
    Session.commit()

    return 'OK', 200


@app.route('/authors/<path:id>', methods=['PUT'])
def update_author(id):
    author = Session.query(Author).filter(Author.id == id)
    if not request.json or not author.first():
        abort(400)
    connected_books_ids = []

    links = Session.query(AuthorBookLink).filter(AuthorBookLink.author_id == author.first().id)
    for link in links:
        connected_books_ids.append(link.book_id)
    links.delete()

    try:
        author.update({'id': request.json['id'], 'name': request.json['name'], 'updated_at' : datetime.now()})
    except IntegrityError:
        Session.rollback()
        return 'Id already exists', 400
    for book_id in connected_books_ids:
        Session.add(AuthorBookLink(author_id = request.json['id'], book_id = book_id))
    Session.commit()

    return 'OK', 200


@app.route('/authors/<path:id>', methods=['DELETE'])
def delete_author(id):
    Session.query(AuthorBookLink).filter(AuthorBookLink.author_id == id).delete()
    Session.query(Author).filter(Author.id == id).delete()
    Session.commit()

    return 'OK', 200


@app.route('/find-books', methods=['GET'])
def find_books():
    title = request.args.get('title')
    author_name = request.args.get('author-name')
    result = []
    books = Session.query(Book)
    if title:
        books = books.filter(Book.title == title)
    if author_name:
        books = books.join(AuthorBookLink).join(Author).filter(Author.name == author_name)
    for book in books:
        result.append({'id': book.id, 'title': book.title, 'created_at': book.created_at, 'updated_at' : book.updated_at })
    return jsonify(books = result)


if __name__ == '__main__':
    #create_tables()
    app.run(debug = True)
