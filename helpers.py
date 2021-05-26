import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(search):
    """Look up search for books."""
    # Contact API
    try:
        url = f'https://www.googleapis.com/books/v1/volumes?q={search}&key=AIzaSyAJGXLBDW269OHGuSblb0FTg80EmdLLdBQ'
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        search = response.json()
        return {
            "totalItems": int(search["totalItems"]),
            "items": search["items"]
            # "authors": search["items"][0]['volumeInfo']['authors']
            # "thumbnail": search["items"][1]['volumeInfo']['imageLinks']['thumbnail']
        }
    except (KeyError, TypeError, ValueError):
        return None
