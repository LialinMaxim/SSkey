import datetime
import os
import hashlib


# from app import db

# class User(db.Model):
class User:
    # id = db.Column('id', db.Integer, primary_key=True)
    # login = db.Column('login', db.String(100), unique=True, nullable=False)
    # email = db.Column('email', db.String(150), unique=True, nullable=False)
    # password = db.Column('password', db.LargeBinary, nullable=False)
    # salt = db.Column('salt', db.LargeBinary, nullable=False)
    # reg_date = db.Column('reg_date', db.Date, nullable=False)
    # first_name = db.Column('first_name', db.String(150), nullable=True)
    # last_name = db.Column('last_name', db.String(150), nullable=True)
    # phone = db.Column('phone', db.String(100), nullable=True)

    @staticmethod
    def generate_salt(salt_len=16):
        return os.urandom(salt_len)

    @staticmethod
    def hash_password(password, salt, iterations=100001, encoding='utf-8'):
        hashed_password = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=bytes(password, encoding),
            salt=salt,
            iterations=iterations
        )
        return salt, iterations, hashed_password

    def compare_hash(self, input_password):
        hash_input_password = __class__.hash_password(input_password, self.salt)
        return hash_input_password == self.password

    def __init__(self, login, email, password, first_name, last_name, phone):
        self.login = login
        hashed_data = __class__.hash_password(password, __class__.generate_salt())
        self.salt = hashed_data[0]
        self.password = hashed_data[2]
        self.email = email
        self.reg_date = datetime.datetime.now()
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone

    def __str__(self):
        return "User login - {0}; Email - {1}; First_name - {2}; Last name - {3}; Phone - {4}". \
            format(self.login, self.email, self.first_name, self.last_name, self.phone)

    @staticmethod
    def validate_user_create_data(req_args):
        if 'password' in req_args and 'login' in req_args and 'email' in req_args:
            return True
        else:
            return False
