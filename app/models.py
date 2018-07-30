import datetime
import hashlib
import os

from sqlalchemy import Column, String, Integer, Date, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

from base import Base, Session
from app import app


session = Session()


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(100), unique=True, nullable=False)
    email = Column('email', String(150), unique=True, nullable=False)
    password_hash = Column('userpass', LargeBinary, nullable=False)
    # salt = Column('salt', LargeBinary, nullable=False)
    reg_date = Column('reg_date', Date, nullable=False)
    first_name = Column('first_name', String(150), nullable=True)
    last_name = Column('last_name', String(150), nullable=True)
    phone = Column('phone', String(100), nullable=True)

    def __init__(self, username, email, first_name, last_name, phone):
        self.username = username
        # hashed_data = __class__.hash_password(password, User.generate_salt())
        # self.salt = hashed_data[0]
        # self.userpass = hashed_data[2]
        # self.password_hash = password_hash
        self.email = email
        self.reg_date = datetime.datetime.now()
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone

    def __str__(self):
        return "Username - {0}; Email - {1}; First_name - {2}; Last name - {3}; Phone - {4}". \
            format(self.username, self.email, self.first_name, self.last_name, self.phone)

    # @staticmethod
    # def generate_salt(salt_len=16):
    #     return os.urandom(salt_len)
    #
    # @staticmethod
    # def hash_password(userpass, salt, iterations=100001, encoding='utf-8'):
    #     hashed_password = hashlib.pbkdf2_hmac(
    #         hash_name='sha256',
    #         password=bytes(userpass, encoding),
    #         salt=salt,
    #         iterations=iterations
    #     )
    #     return salt, iterations, hashed_password
    #
    # def compare_hash(self, input_password):
    #     hash_input_password = __class__.hash_password(input_password, self.salt)
    #     return hash_input_password == self.userpass

    def hash_password(self, password):
        """Encrypts the password

        Encrypt with PassLib package based on sha256 hashing algorithm

        :param password: Inputted password
        """
        self.password_hash = pwd_context.encrypt(password)
        print('====================')
        print('PASSWORD WAS HASHED:', self.password_hash)
        print('====================')

    def verify_password(self, password):
        """Verifies the password

        Compares the passwords' hashes. Returns True if passwords' hashes
        are the same or False if they are not.

        :param password: Inputted password
        :return: True or False
        """
        return pwd_context.verify(password, self.password_hash)

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

    def generate_auth_token(self, expiration=1800):
        """Authentication token generator

        Generates the token for authentication. The token is an encrypted
        version of a dictionary that has the id of the user.

        :param expiration: Token expiration
        :return: Token
        """
        serializer = Serializer(app.config['SECRET_KEY'],
                                expires_in=expiration)
        return serializer.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """Authentication token verifier

        Verifies the token for authentication. If the token can be decoded
        then the id encoded in it is used to load the user,
        and that user is returned.

        :param token: Authentication token
        :return: User
        """
        serializer = Serializer(app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except SignatureExpired:
            return None  # Valid token, but expired
        except BadSignature:
            return None  # Invalid token
        user = session.query(User).get(data['id'])
        return user

    @staticmethod
    def validate_user(req_args):
        if req_args['userpass'] and req_args['username'] and req_args['email']:
            return True
        else:
            return False


class Password(Base):
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
            'username': self.username,
            'email': self.email,
            'register_date': str(self.reg_date),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone
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
