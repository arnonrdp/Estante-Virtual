from config import *
from werkzeug.security import generate_password_hash, check_password_hash


user_book = db.Table('user_book',
                     db.Column('uid', db.Integer, db.ForeignKey('user.uid'), primary_key=True),
                     db.Column('bid', db.Text, db.ForeignKey('book.bid'), primary_key=True),
                     db.Column('date_added', db.DateTime(timezone=True), server_default=db.func.now())
                     )


class User(db.Model):
    __tablename__ = 'user'

    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(25), nullable=False)
    hash = db.Column(db.String(), nullable=False)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    books = db.relationship('Book', secondary=user_book, back_populates='users')

    def set_password(self, password):
        self.hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hash, password)

    def __init__(self, email, first_name):
        self.email = email
        self.first_name = first_name

    def __repr__(self):
        return self.first_name


class Book(db.Model):
    __tablename__ = 'book'

    bid = db.Column(db.Text, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    authors = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.Text, nullable=True)
    users = db.relationship('User', secondary=user_book, back_populates='books')

    def __init__(self, bid, title, authors, thumbnail):
        self.bid = bid
        self.title = title
        self.authors = authors
        self.thumbnail = thumbnail

    def __repr__(self):
        return self.title


# db.create_all()
