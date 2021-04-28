from flask import Blueprint, jsonify, request, make_response, Response
from project.models import User
from werkzeug.security import check_password_hash, generate_password_hash
from project import db, app
from functools import wraps
import jwt
import datetime

core = Blueprint('core',__name__)


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
            # return jsonify({'data' : data})
            current_user = User.query.filter_by(id = data['id']).first()
        except:
            return jsonify({'message' : 'Token is Invalid !!'})

        return func(current_user, *args, **kwargs)
    return decorated

@core.route('/', methods = ['GET', 'POST'])
def hello_world():
    # if "Authorization" in request.headers:
    #     auth_header = (request.headers["Authorization"])
    #     return jsonify({'auth_header' : auth_header})
    # else:
    #     return "HELLO"
    # for i in request.headers:
        # token = request.headers['login_token']
        # return jsonify({'headers' : i})
    return "Hello, Welcome to a simple RestFULL app"


# Login Function which takes authentication from requests and generate a token for the user valid for specified time
@core.route('/login', methods = ['GET', 'POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Please Enter Username or Password', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})
    
    user = User.query.filter_by(name = auth.username).first()

    if not user:
        return make_response('No User Found', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})
    
    if check_password_hash(user.password, auth.password):
        payload = {'id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}
        token = jwt.encode({'id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        # decoded_token = token
        # url = 'https://127.0.0.1:5000/'
        # headers = {'login_token': decoded_token}
        # headers = Headers()
        # headers.add_header('login_token', decoded_token)
            # client.post('https://127.0.0.1:5000/login', headers={'login_token' : decoded_token});
        # with app.test_client() as client:
        #     client.get('/', headers=dict(Authorization='Bearer ' + decoded_token))
        # requests.get('https://127.0.0.1:5000/login', headers={'Authorization': token})
        # HEADERS = {'Authorization': 'token {}'.format(token)}
        # with requests.Session() as s:
        #     s.headers.update(HEADERS)
        #     s.post('http://127.0.0.1:5000/')
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required !!"'})

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

