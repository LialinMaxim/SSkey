import datetime
import hashlib
import os
import base64

from sqlalchemy import Column, String, Integer, Date, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet

from . import Base
from . import Session
session = Session()

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


class Password(Base):
    SECRET_KEY = b'hQaS02VVLD4P_eedMd1tmi2w2PVFgJutLwV-6W-MBq4='

    __tablename__ = 'passwords'

    pass_id = Column('pass_id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))

    user = relationship("User", backref="passwords", cascade='all,delete')

    url = Column('url', String(250), nullable=True)
    title = Column('title', String(250), nullable=True)
    login = Column('login', String(150), nullable=False)
    password = Column('pass', String(150), nullable=False)
    comment = Column('comment', String(450), nullable=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'pass_id': self.pass_id,
            'url': self.url,
            'title': self.title,
            'login': str(self.login),
            'password': self.decrypt_password(),
            'comment': self.comment,

        }

    def get_cipher(self):
        try:
            user = session.query(User).filter(User.id == self.user_id).first()
        except SQLAlchemyError as e:
            # TO DO add error into logs
            raise SQLAlchemyError(str(e))
        cipher_key = base64.urlsafe_b64encode(user.userpass) + Password.SECRET_KEY
        return Fernet(cipher_key)

    def crypt_and_save_password(self, raw_password):
        cipher = self.get_cipher()
        encrypted_password = cipher.encrypt(bytes(raw_password, encoding="utf-8"))
        self.password = encrypted_password

    def decrypt_password(self):
        cipher = self.get_cipher()
        decrypted_password = cipher.decrypt(self.password)
        return decrypted_password.decode('utf-8')

    def __init__(self, login, password, user_id, url, title, comment):
        self.login = login
        self.user_id = user_id
        self.url = url
        self.title = title
        self.comment = comment
        self.crypt_and_save_password(password)


class SessionObject(Base):
    __tablename__ = 'session_objects'

    id = Column('id', Integer, primary_key=True)
    token = Column('token', String(100), unique=True, nullable=False)

    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    user = relationship("User", backref="session_objects", cascade='all,delete')

    login_time = Column('login_time', DateTime, nullable=False)
    time_out_value = Column('time_out_value', Integer, nullable=False)


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

