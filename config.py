from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Library to use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Estante.db'
db = SQLAlchemy(app)
