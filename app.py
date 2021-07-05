import requests
from flask import render_template, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp

from config import *
from model.Books import Books
from model.User import User
from helpers import login_required

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()  # Check later
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Google Books API Key
APIKEY = 'AIzaSyAJGXLBDW269OHGuSblb0FTg80EmdLLdBQ'


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
    user_id = User.query.filter_by(email=session['email']).first().id
    return Books.query.filter_by(user_id=user_id).all()


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
        url = f'https://www.googleapis.com/books/v1/volumes?q={seek}&maxResults=40&printType=books&key={APIKEY}'
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get('items', [])
        no_image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/300px-No_image_available.svg.png'
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
    user = User.query.filter_by(email=session['email']).first()
    try:
        url = f'https://www.googleapis.com/books/v1/volumes/{book_id}'
        response = requests.get(url)
        response.raise_for_status()
        book = response.json()
        insert = Books(user_id=user.id,
                       book_id=book['id'],
                       title=book['volumeInfo']['title'],
                       thumbnail=book['volumeInfo']['imageLinks']['thumbnail'])
        db.session.add(insert)
        db.session.commit()
    except (KeyError, TypeError, ValueError, requests.RequestException) as e:
        print(e)
    return redirect("/")


@app.route('/remove/<book_id>')
@login_required
def remove(book_id):
    """Remove um livro do ID do usuário"""
    try:
        user = User.query.filter_by(email=session['email']).first()
        book = Books.query.filter_by(book_id=book_id, user_id=user.id).first()
        db.session.delete(book)
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
