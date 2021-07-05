from config import *


class Books(db.Model):
    __tablename__ = 'readingTest'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    book_id = db.Column(db.String(30), unique=True)
    title = db.Column(db.String(80))
    thumbnail = db.Column(db.String(80))
    date_add = db.Column(db.String(20))
