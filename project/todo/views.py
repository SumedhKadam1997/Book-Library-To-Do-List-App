from flask import Blueprint, jsonify, request
from project.models import Todo, User
from project import db, app
from functools import wraps
import jwt

todo = Blueprint('todo',__name__)

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

# TO DO Routes
# This is the first route which gets all the to-do list of the current logged in user.
@todo.route('/todo', methods = ['GET', 'POST'])
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
    elif request.method == 'POST':
        data = request.get_json()
        new_todo = Todo(text = data['text'], complete = False, user_id = current_user.id)
        db.session.add(new_todo)
        db.session.commit()

        return jsonify({'message' : 'To-Do Created !!'})

# This is the second route which gets a single to-do of the current logged in user.
@todo.route('/todo/<todo_id>', methods = ['GET'])
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
# @app.route('/todo', methods = ['POST'])
# @token_required
# def create_todo(current_user):
#     data = request.get_json()
#     new_todo = Todo(text = data['text'], complete = False, user_id = current_user.id)
#     db.session.add(new_todo)
#     db.session.commit()

#     return jsonify({'message' : 'To-Do Created !!'})

# This is the forth route which marks the selected to-do as completed for the current logged in user.
@todo.route('/todo/<todo_id>', methods = ['PUT'])
@token_required
def complete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id = todo_id).first()

    if not todo:
        return jsonify({'message' : 'No Todo found !!'})
    
    todo.complete = True
    db.session.commit()

    return jsonify({'message' : 'Todo Completed !!'})

# This is the fifth route which deletes the specified to-do of the current logged in user.
@todo.route('/todo/<todo_id>', methods = ['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id = todo_id).first()

    if not todo:
        return jsonify({'message' : 'No Todo found !!'})
    
    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message' : 'Todo Deleted !!'})