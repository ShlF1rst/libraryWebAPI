import json
import database
from database import Book, Author, Session, AuthorBookLink, create_tables
from datetime import  datetime

if __name__ == '__main__':
    Session.query(AuthorBookLink).delete()
    Session.query(Book).delete()
    Session.query(Author).delete()

    with open('books.json') as f:
        data = json.load(f)
    book_index = 1
    index = 1
    authors = {}
    for line in data:
        exists = Session.query(Author).filter_by(name=line['author']).first()
        if not exists:
            authors[line['author']] = index
            Session.add(Author(id = index,name = line['author'],created_at = datetime.now()))
            index += 1
        Session.add(Book(id = book_index,title = line['title'],created_at = datetime.now()))
        Session.commit()
        Session.add(AuthorBookLink(author_id = authors[line['author']], book_id = book_index))
        Session.commit()
        book_index += 1

