from project import db



# These are the db models
class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.Text)
    password = db.Column(db.Text)
    admin = db.Column(db.Boolean)
    # Relationships
    book = db.relationship('Book',backref='user',uselist=False)
    todo = db.relationship('Todo',backref='user',uselist=False)


class Book(db.Model):

    __tablename__ = 'books'

    id = db.Column(db.Integer,primary_key= True)
    name = db.Column(db.Text)
    author = db.Column(db.Text)
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

class Todo(db.Model):

    __tablename__ = 'todos'

    id = db.Column(db.Integer,primary_key= True)
    text = db.Column(db.Text)
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
