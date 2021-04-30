from flask import Blueprint, jsonify, request, make_response
from project.models import User
from werkzeug.security import check_password_hash, generate_password_hash
from project import db, app, token_required
from functools import wraps
import jwt
import datetime

core = Blueprint('core',__name__)

# Home route
@core.route('/', methods = ['GET', 'POST'])
def hello_world():
    return "Hello, Welcome to a simple RestFULL app"


# Login Function which takes authentication from requests 
# and generate a token for the user valid for specified time
@core.route('/login', methods = ['GET', 'POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Please Enter Username or Password', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})
    
    user = User.query.filter_by(name = auth.username).first()

    if not user:
        return make_response('No User Found', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})

# Route to get all registered users 
@core.route('/user', methods = ['GET'])
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

# Route to get single user
@core.route('/user/<user_id>', methods = ['GET'])
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

# Route to create a user
@core.route('/user', methods = ['POST'])
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

# Route to promote a user to ADMIN
@core.route('/user/<user_id>', methods = ['PUT'])
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

# Route to delete a user
@core.route('/user/<user_id>', methods = ['DELETE'])
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

