from project import db
from project.models import User
from werkzeug.security import generate_password_hash

db.create_all()

hashed_password = generate_password_hash('12345', method="sha256")
new_user = User(name = 'ADMIN', password = hashed_password, admin = True)
db.session.add(new_user)
db.session.commit()