import datetime
import os
import hashlib
from sqlalchemy import Column, String, Integer, Date, LargeBinary

from base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(100), unique=True, nullable=False)
    email = Column('email', String(150), unique=True, nullable=False)
    userpass = Column('userpass', LargeBinary, nullable=False)
    salt = Column('salt', LargeBinary, nullable=False)
    reg_date = Column('reg_date', Date, nullable=False)
    first_name = Column('first_name', String(150), nullable=True)
    last_name = Column('last_name', String(150), nullable=True)
    phone = Column('phone', String(100), nullable=True)

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
        hash_input_password = __class__.hash_password(input_password, self.salt)
        return hash_input_password == self.userpass

    def __init__(self, username, email, password, first_name, last_name, phone):
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
            format(self.username, self.email, self.first_name, self.last_name, self.phone)

    @staticmethod
    def validate_user_create_data(req_args):
        if req_args['userpass'] and req_args['username'] and req_args['email']:
            return True
        else:
            return False
