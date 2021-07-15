import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configure application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')

# Configure Library to use SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bqucsxtgiaflnu:5d54470ffd2d712c5bf3097db3b11de74543613f4911ff1ed6af05ebc0d9ac93@ec2-54-157-100-65.compute-1.amazonaws.com:5432/d1qschqsh1ocns'
# os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Google Books API
API = 'AIzaSyAJGXLBDW269OHGuSblb0FTg80EmdLLdBQ'
# os.environ.get('APIKEY')
