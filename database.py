from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_string = "postgres://donteco:donteco@localhost/library"

db = create_engine(db_string)
conn = db.connect()

meta = MetaData(db)
books_table = Table('books', meta,
                       Column('id', Integer,  primary_key=True),
                       Column('created_at', DateTime, nullable=False),
                       Column('updated_at', DateTime),
                       Column('title', String, nullable=False))


authors_table = Table('authors', meta,
                       Column('id', Integer,  primary_key=True),
                       Column('created_at', DateTime, nullable=False),
                       Column('updated_at', DateTime),
                       Column('name', String, nullable=False))


authorBooks_table = Table('authorbooks', meta,
                        Column('author_id', Integer, ForeignKey('authors.id'),  nullable=False),
                        Column('book_id', Integer, ForeignKey('books.id'), nullable=False))

def create_tables():
    books_table.create()
    authors_table.create()
    authorBooks_table.create()


Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer,  primary_key=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer,  primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)


class AuthorBookLink(Base):
    __tablename__ = 'authorbooks'
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False, primary_key=True)


Session = sessionmaker(bind=db)
Session = Session()