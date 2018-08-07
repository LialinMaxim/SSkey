import datetime
import hashlib
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# from base import Base

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
"""
Flask app for migration database PostgresSQL
Use in console:
# python models.py db init
# python models.py db init
# python models.py db upgrade
or
# python models.py db downgrade
"""
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/db_sskey"
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(100), unique=True, nullable=False)
    email = db.Column('email', db.String(150), unique=True, nullable=False)
    userpass = db.Column('userpass', db.LargeBinary, nullable=False)
    salt = db.Column('salt', db.LargeBinary, nullable=False)
    reg_date = db.Column('reg_date', db.Date, nullable=False)
    first_name = db.Column('first_name', db.String(150), nullable=True)
    last_name = db.Column('last_name', db.String(150), nullable=True)
    phone = db.Column('phone', db.String(100), nullable=True)

    def __init__(self, id, username, email, userpass, salt, reg_date, first_name, last_name, phone):
        self.id = id
        self.username = username
        self.email = email
        self.userpass = userpass
        self.salt = salt
        self.reg_date = reg_date
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone


@staticmethod
def generate_salt(salt_len=16):
    return os.urandom(salt_len)


@staticmethod
def hash_password(userpass, salt, iterations=100001, encoding='utf-8'):
    hashed_password = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=bytes(userpass, encoding),
        salt=salt,
        iterations=iterations
    )
    return salt, iterations, hashed_password


def compare_hash(self, input_password):
    hash_input_password = User.hash_password(input_password,
                                             self.salt)
    return hash_input_password[2] == self.userpass


@property
def serialize(self):
    """Return object data in easily serializeable format"""
    return {
        'id': self.id,
        'username': self.username,
        'email': self.email,
        'register_date': str(self.reg_date),
        'first_name': self.first_name,
        'last_name': self.last_name,
        'phone': self.phone
    }


def __init__(self, username, email, password, first_name, last_name,
             phone):
    self.username = username
    hashed_data = __class__.hash_password(password, User.generate_salt())
    self.salt = hashed_data[0]
    self.userpass = hashed_data[2]
    self.email = email
    self.reg_date = datetime.datetime.now()
    self.first_name = first_name
    self.last_name = last_name
    self.phone = phone


def __str__(self):
    return "Username - {0}; Email - {1}; First_name - {2}; Last name - {3}; Phone - {4}". \
        format(self.username, self.email, self.first_name, self.last_name,
               self.phone)


@staticmethod
def validate_user(req_args):
    if req_args['userpass'] and req_args['username'] and req_args['email']:
        return True
    else:
        return False


class Password(db.Model):
    __tablename__ = 'passwords'

    pass_id = db.Column('pass_id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))

    user = db.relationship("User", backref="passwords", cascade='all,delete')

    url = db.Column('url', db.String(250), nullable=True)
    title = db.Column('title', db.String(250), nullable=True)
    login = db.Column('login', db.String(150), nullable=False)
    password = db.Column('pass', db.String(150), nullable=False)
    comment = db.Column('comment', db.String(450), nullable=True)

    def __init__(self, pass_id, user_id, url, title, login, password, comment):
        self.pass_id = pass_id
        self.user_id = user_id
        self.url = url
        self.title = title
        self.login = login
        self.password = password
        self.comment = comment

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'pass_id': self.pass_id,
            'url': self.url,
            'title': self.title,
            'login': str(self.login),
            'password': self.password,
            'comment': self.comment,

        }

    def crypt_and_save_password(self, raw_password):
        # TO DO - realize crypt password method
        crypted_password = raw_password
        self.password = crypted_password

    def decrypt_password(self):
        # TO DO - decrypt password and return it
        return self.password

    def __init__(self, login, password, user_id, url, title, comment):
        self.login = login
        self.crypt_and_save_password(password)
        self.user_id = user_id
        self.url = url
        self.title = title
        self.comment = comment


class SessionObject(db.Model):
    __tablename__ = 'session_objects'

    id = db.Column('id', db.Integer, primary_key=True)
    token = db.Column('token', db.String(100), unique=True, nullable=False)

    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", backref="session_objects", cascade='all,delete')

    login_time = db.Column('login_time', db.DateTime, nullable=False)
    time_out_value = db.Column('time_out_value', db.Integer, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'token': self.token,
            'user_id': self.user_id,
            'login_time': str(self.login_time),
            'time_out_value': self.time_out_value,
        }

    def __init__(self, user_id, time_out_value=1800, token_len=16):
        self.token = SessionObject.generate_token(token_len)
        self.user_id = user_id
        self.login_time = datetime.datetime.now()
        self.time_out_value = time_out_value

    @staticmethod
    def generate_token(token_len):
        return str(os.urandom(token_len))

    def update_login_time(self):
        self.login_time = datetime.datetime.now()


if __name__ == '__main__':
    manager.run()
