import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Flask App  and Database Configuration
app.config['SECRET_KEY'] = 'myverysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Imports to create" token_required" decorator
from project.models import User
from functools import wraps
import jwt

# This is a decorator which facilitates the login functionality by use of jwt tokens
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        if 'login_token' in request.headers:
            token = request.headers['login_token']
        
        if not token:
            return jsonify({'message' : 'Token is Missing !!'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id = data['id']).first()
        except:
            return jsonify({'message' : 'Token is Invalid !!'})

        return func(current_user, *args, **kwargs)
    return decorated

# Imports to register blueprints
from project.user.views import core
from project.book.views import book
from project.todo.views import todo

app.register_blueprint(core)
app.register_blueprint(book)
app.register_blueprint(todo)