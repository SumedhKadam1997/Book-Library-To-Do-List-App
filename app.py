import os
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# These are the db models
class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.Text)
    password = db.Column(db.Text)
    admin = db.Column(db.Boolean)
    todo = db.relationship('Todo',backref='user',uselist=False)

class Todo(db.Model):

    __tablename__ = 'todos'

    id = db.Column(db.Integer,primary_key= True)
    text = db.Column(db.Text)
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

# This is a decorator which facilitates the login functionality by use of jwt tokens
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        if 'login_token' in request.headers:
            token = request.headers['login_token']
        
        if not token:
            return jsonify({'message' : 'Token is Missing !!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id = data['id']).first()
        except:
            return jsonify({'message' : 'Token is Invalid !!'}), 401

        return func(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def hello_world():
    return "Welcome to the Simple To-Do Web Application"

@app.route('/user', methods = ['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'User is not ADMIN'})

    users = User.query.all()
    total_users = []

    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        total_users.append(user_data)

    return jsonify({'users' : total_users})

@app.route('/user/<user_id>', methods = ['GET'])
@token_required
def get_one_users(current_user, user_id):
    if not current_user.admin:
        return jsonify({'message' : 'User is not ADMIN'})

    user = User.query.filter_by(id = user_id).first()

    if not user:
        return jsonify({'message' : 'No user found !!'})

    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user' : user_data})

@app.route('/user', methods = ['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'User is not ADMIN'})

    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method="sha256")
    new_user = User(name = data['name'], password = hashed_password, admin = False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created'})

@app.route('/user/<user_id>', methods = ['PUT'])
@token_required
def promote_user(current_user, user_id):
    if not current_user.admin:
        return jsonify({'message' : 'User is not ADMIN'})

    user = User.query.filter_by(id = user_id).first()

    if not user:
        return jsonify({'message' : 'No user found !!'})
    
    user.admin = True
    db.session.commit()

    return jsonify({'message' : 'User Promoted !!'})

@app.route('/user/<user_id>', methods = ['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if not current_user.admin:
        return jsonify({'message' : 'User is not ADMIN'})

    user = User.query.filter_by(id = user_id).first()

    if not user:
        return jsonify({'message' : 'No user found !!'})
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'User Deleted !!'})

# Login Function which takes authentication from requests and generate a token for the user valid for specified time
@app.route('/login', methods = ['GET', 'POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Please Enter Username or Password', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})
    
    user = User.query.filter_by(name = auth.username).first()

    if not user:
        return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})

# TO DO Routes
# This is the first route which gets all the to-do list of the current logged in user.
@app.route('/todo', methods = ['GET', 'POST'])
@token_required
def get_or_create_todos(current_user):
    if request.method == 'GET':
        todos = Todo.query.filter_by(user_id = current_user.id)
        all_todos = []
    
        for todo in todos:
            todo_data = {}
            todo_data['id'] = todo.id
            todo_data['text'] = todo.text
            todo_data['complete'] = todo.complete
            all_todos.append(todo_data)

        return jsonify({"To-Do's" : all_todos})
    else:
        data = request.get_json()
        new_todo = Todo(text = data['text'], complete = False, user_id = current_user.id)
        db.session.add(new_todo)
        db.session.commit()

        return jsonify({'message' : 'To-Do Created !!'})

# This is the second route which gets a single to-do of the current logged in user.
@app.route('/todo/<todo_id>', methods = ['GET', 'PUT', 'DELETE'])
@token_required
def get_one_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id = todo_id).first()
    if not todo:
        return jsonify({'message' : 'No Todo found !!'})
    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete

    return jsonify({"To-Do" : todo_data})

# This is the third route which create a new to-do for the current logged in user.
@app.route('/todo', methods = ['POST'])
@token_required
def create_todo(current_user):
    data = request.get_json()
    new_todo = Todo(text = data['text'], complete = False, user_id = current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'message' : 'To-Do Created !!'})

# This is the forth route which marks the selected to-do as completed for the current logged in user.
@app.route('/todo/<todo_id>', methods = ['PUT'])
@token_required
def complete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id = todo_id).first()

    if not todo:
        return jsonify({'message' : 'No Todo found !!'})
    
    todo.complete = True
    db.session.commit()

    return jsonify({'message' : 'Todo Completed !!'})

# This is the fifth route which deletes the specified to-do of the current logged in user.
@app.route('/todo/<todo_id>', methods = ['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id = todo_id).first()

    if not todo:
        return jsonify({'message' : 'No Todo found !!'})
    
    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message' : 'Todo Deleted !!'})

if __name__ == "__main__":
    app.run(debug=True)