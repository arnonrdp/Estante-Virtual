import requests
from flask import render_template, redirect, request, session
from flask_login import LoginManager
from flask_session import Session
from tempfile import mkdtemp

from config import *
from model.Models import User, Book, user_book
from helpers import login_required

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()  # Check later
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    livros = bookshelf()
    return render_template("index.html", livros=livros)


def bookshelf():
    """
    Gets the id of the logged in user, queries the
    database for the books that this id has already added.
    """
    user_id = db.session.query(User).filter_by(email=session['email']).first().uid
    return db.session.query(Book).join(user_book).filter_by(uid=user_id).all()


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        # Query database for email
        session['email'] = email = request.form["email"]
        user = User.query.filter_by(email=email).first()

        # Remember which user has logged in
        session['name'] = user.first_name

        # Verify password and redirect user to home page
        if user.check_password(request.form["password"]):
            return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session["name"] = None
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route('/search', methods=["GET", "POST"])
@login_required
def search():
    """Pesquisa um livro utilizando a API do Google Books"""
    livros = bookshelf()
    infobooks = []
    if request.method == "POST":
        seek = request.form.get("seek")
        url = f'https://www.googleapis.com/books/v1/volumes?q={seek}&maxResults=40&printType=books&key={API}'
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get('items', [])
        no_image = '/static/img/no_cover.jpg'
        for result in results:
            info = result.get('volumeInfo', {})
            imageLinks = info.get("imageLinks", {})
            thumbs = imageLinks.get('thumbnail')
            infobooks.append(
                {
                    "book_id": result.get('id'),
                    "thumbnail": thumbs or no_image,
                    "title": info.get('title'),
                    "authors": info.get('authors'),
                }
            )
    return render_template("index.html", infobooks=infobooks, livros=livros)


@app.route('/add/<book_id>')
@login_required
def add(book_id):
    """Atribui um livro ao ID do usuário"""
    user = db.session.query(User).filter_by(email=session['email']).first()
    try:
        url = f'https://www.googleapis.com/books/v1/volumes/{book_id}'
        response = requests.get(url)
        response.raise_for_status()
        gbook = response.json()
        book_query = db.session.query(Book).filter_by(bid=book_id).first()
        if not book_query:
            book_query = Book(bid=book_id,
                              title=gbook['volumeInfo']['title'],
                              authors=gbook['volumeInfo']['authors'][0],
                              thumbnail=gbook['volumeInfo']['imageLinks']['thumbnail']
                              )
            db.session.add(book_query)
            db.session.commit()
        db.session.execute(user_book.insert().values(uid=user.uid, bid=gbook['id']))
        db.session.commit()
    except Exception as e:
        print(e)
    return redirect("/")


@app.route('/remove/<book_id>')
@login_required
def remove(book_id):
    """Remove um livro do ID do usuário"""
    try:
        user = db.session.query(User).filter_by(email=session['email']).first()
        book_rm = Book.query.get(book_id) 
        user.books.remove(book_rm)
        db.session.commit()
    except Exception as e:
        print(e)
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method != "POST":
        return render_template("login.html")
    first_name = request.form['first_name']
    email = request.form['email']

    user = User(first_name=first_name, email=email)
    user.set_password(request.form['password'])
    db.session.add(user)
    db.session.commit()
    return redirect("/")
