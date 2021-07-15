import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configure application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')

# Configure Library to use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

# Google Books API
API = os.environ.get('APIKEY')

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
