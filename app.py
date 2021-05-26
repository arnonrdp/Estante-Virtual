from cs50 import SQL
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup

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
        return f"must provide {field}"

# Configure Library to use SQLite database
db = SQL("sqlite:///Estante.db")


@app.route("/")
@login_required
def index():
    return render_template('index.html')


@app.route("/search")
@login_required
def add():
    return render_template('search.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password was submitted
        result_checks = is_provided("username") or is_provided("password")
        if result_checks is not None:
            return result_checks

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "invalid username and/or password"

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/lookup", methods=["GET", "POST"])
@login_required
def search():
    """Get book search."""
    if request.method == "POST":
        result_check = is_provided("search")
        if result_check is not None:
            return result_check
        search = request.form.get("search").upper()
        search = lookup(search)
        if search is None:
            return "Pesquisa Inválida"
        return render_template("search.html", search={
            'totalItems': search['totalItems'],
            'items': search['items']
            # "title": search["title"],
            # 'authors': search['authors'],
            # 'thumbnail': search['thumbnail']
        })
    else:
        return render_template("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result_checks = is_provided("username") or is_provided("password") or is_provided("confirmation")
        if result_checks != None:
            return result_checks
        if request.form.get("password") != request.form.get("confirmation"):
            return "passwords must match"
        try:
            prim_key = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                    username=request.form.get("username"),
                    hash=generate_password_hash(request.form.get("password")))
        except:
            return "registration already exists"
        if prim_key is None:
            return "registration error"
        session["user_id"] = prim_key
        return redirect("/")

    else:
        return render_template("register.html")
