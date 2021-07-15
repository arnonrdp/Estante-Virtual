import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configure application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')

# Configure Library to use SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Google Books API
API = 'AIzaSyAJGXLBDW269OHGuSblb0FTg80EmdLLdBQ'
# os.environ.get('APIKEY')
