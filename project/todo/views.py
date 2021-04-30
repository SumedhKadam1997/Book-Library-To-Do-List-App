from flask import Blueprint, jsonify, request
from project.models import Todo, User
from project import db, token_required


todo = Blueprint('todo',__name__)


# To do routes
# This is the first and second route which gets all the todo list of the current logged in user.
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

        return jsonify({"Todo's" : all_todos})

    elif request.method == 'POST':
        data = request.get_json()
        new_todo = Todo(text = data['text'], complete = False, user_id = current_user.id)
        db.session.add(new_todo)
        db.session.commit()

        return jsonify({'message' : 'To-do Created !!'})


# This is the third route which gets a single todo of the current logged in user.
@todo.route('/todo/<todo_id>', methods = ['GET'])
@token_required
def get_one_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id = todo_id).first()
    if not todo:
        return jsonify({'message' : 'No todo found !!'})
    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete

    return jsonify({"To Do" : todo_data})


# This is the forth route which marks the selected todo as completed for the current logged in user.
@todo.route('/todo/<todo_id>', methods = ['PUT'])
@token_required
def complete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id = todo_id).first()

    if not todo:
        return jsonify({'message' : 'No To Do found !!'})
    
    todo.complete = True
    db.session.commit()

    return jsonify({'message' : 'To Do Completed !!'})


# This is the fifth route which deletes the specified todo of the current logged in user.
@todo.route('/todo/<todo_id>', methods = ['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id = todo_id).first()

    if not todo:
        return jsonify({'message' : 'No todo found !!'})
    
    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message' : 'To Do Deleted !!'})