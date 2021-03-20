
from project import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    first_name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    su_id = db.Column(db.Integer, unique=True, index=True)
    password_hash = db.Column(db.String(128))
    used_port = db.Column(db.Integer, nullable=True)
    last_process_time = db.Column(db.DateTime, nullable=True)

    def __init__(self, email, username, password, first_name, surname, su_id):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name
        self.su_id = su_id
        self.surname = surname

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_active_process(self):
        if not self.used_port:
            return False
        # return datetime.now() - self.last_process_time < timedelta(hours=1)
        return True

    def update_last_process(self, port):
        self.used_port = port
        self.last_process_time = datetime.now()
