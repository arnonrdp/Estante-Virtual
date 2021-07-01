import requests
from cs50 import SQL
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def is_provided(field):
    if not request.form.get(field):
        return f"Faltou informar: {field}"


# Configure Library to use SQLite database
db = SQL("sqlite:///Estante.db")


@app.route("/")
@login_required
def index():
    # Consulta o Primeiro Nome do usuário para exibir no título
    names = db.execute("""
        SELECT first_name FROM users WHERE id=:user_id
        """, user_id=session["user_id"]
        )
    first_name = names[0]["first_name"] if names else None
# Consulta a DB para organizar a estante de livros
    livros = db.execute("""
        SELECT * FROM readingTest WHERE user_id=:user_id ORDER BY title
        """, user_id=session["user_id"]
        )
    return render_template("index.html", livros=livros, first_name=first_name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email and password was submitted
        result_checks = is_provided("email") or is_provided("password")
        if result_checks is not None:
            return result_checks

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "E-mail ou Senha inválidos"

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["email"] = request.form.get("email")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route('/search', methods=["GET", "POST"])
@login_required
def search():
    """Pesquisa um livro utilizando a API do Google Books"""
    livros = db.execute("""
        SELECT * FROM readingTest WHERE user_id=:user_id ORDER BY title
        """, user_id=session["user_id"]
        )
    infobooks = []
    if request.method == "POST":
        seek = request.form.get("seek")
        url = f'https://www.googleapis.com/books/v1/volumes?q={seek}&maxResults=40&key=AIzaSyAJGXLBDW269OHGuSblb0FTg80EmdLLdBQ'
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get('items', [])
        no_image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/300px-No_image_available.svg.png'
        for result in results:
            info = result.get('volumeInfo', {})
            imageLinks = info.get("imageLinks", {})
            thumbs = imageLinks.get('thumbnail')
            infobooks.append({
                "book_id": result.get('id'),
                "thumbnail": thumbs if thumbs else no_image,
                "title": info.get('title'),
                "authors": info.get('authors')
            })
    return render_template("index.html", infobooks=infobooks, livros=livros)
    

@app.route('/add/<book_id>')
@login_required
def add(book_id):
    """Atribui um livro ao ID do usuário"""
    try:
        url = f'https://www.googleapis.com/books/v1/volumes/{book_id}'
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        search = response.json()
        db.execute("""
            INSERT INTO readingTest (user_id, book_id, title, thumbnail)
            VALUES (:user_id, :book_id, :title, :thumbnail)
            """,
                   user_id=session["user_id"],
                   book_id=book_id,
                   title=search["volumeInfo"]["title"],
                   thumbnail=search["volumeInfo"]["imageLinks"]["thumbnail"]
                   )
        return redirect("/")
    except (KeyError, TypeError, ValueError):
        return render_template("index.html")


@app.route('/remove/<book_id>')
@login_required
def remove(book_id):
    """Remove um livro do ID do usuário"""
    try:
        db.execute("""
            DELETE FROM readingTest WHERE book_id LIKE :book_id;
            """, book_id=book_id
            )
        return redirect("/")
    except:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result_checks = is_provided("email") or is_provided(
            "password") or is_provided("confirmation")
        if result_checks != None:
            return result_checks
        if request.form.get("password") != request.form.get("confirmation"):
            return "As senhas precisam coincidir"
        try:
            prim_key = db.execute("INSERT INTO users (email, hash, first_name) VALUES (:email, :hash, :first_name)",
                                  email=request.form.get("email"),
                                  hash=generate_password_hash(
                                      request.form.get("password")),
                                  first_name=request.form.get("first_name")
                                  )
        except:
            return "Este e-mail já está cadastrado"
        if prim_key is None:
            return "Erro no cadastro"
        session["user_id"] = prim_key
        return redirect("/")
    else:
        return render_template("login.html")
