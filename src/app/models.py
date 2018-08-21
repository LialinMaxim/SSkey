import datetime
import hashlib
import os
import base64

from sqlalchemy import Column, String, Integer, Date, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet

from .base import Base, Session
from .admin.models import Admin

session = Session()


class User(Base):
    """
    Class describe User in application
    """
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(100), unique=True, nullable=False)
    email = Column('email', String(150), unique=True, nullable=False)
    password = Column('userpass', LargeBinary, nullable=False)
    salt = Column('salt', LargeBinary, nullable=False)
    reg_date = Column('reg_date', Date, nullable=False)
    first_name = Column('first_name', String(150), nullable=True)
    last_name = Column('last_name', String(150), nullable=True)
    phone = Column('phone', String(100), nullable=True)

    @staticmethod
    def is_user_exists(user_id):
        """
        Method check is user exists in the database
        :param user_id:
        :return: boolean or Exception SQLAlchemy error if dont have connect to db
        """
        user = session.query(User).filter(User.id == user_id).first()
        return bool(user)

    @staticmethod
    def generate_salt(salt_len=16):
        """
        Method generate salt of needed length. Salt use in process of get password hash
        :param salt_len:
        :return: bytes
        """
        return os.urandom(salt_len)

    @staticmethod
    def get_hash_password(password, salt, iterations=100001, encoding='utf-8'):
        """
        Method create salted password hash
        :param password:
        :param salt:
        :param iterations:
        :param encoding:
        :return: tuple
        """
        hashed_password = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=bytes(password, encoding),
            salt=salt,
            iterations=iterations
        )
        return salt, iterations, hashed_password

    def compare_hash(self, input_password):
        """
        Method compare hash of input password with hash of user password saved in database
        :param input_password:
        :return: boolean
        """
        hash_input_password = User.get_hash_password(input_password,
                                                     self.salt)
        return hash_input_password[2] == self.password

    def __init__(self, data):
        self.reg_date = datetime.datetime.now()
        self.username = data['username']
        self.email = data['email']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.phone = data['phone']
        hashed_data = User.get_hash_password(data['password'], User.generate_salt())
        self.salt = hashed_data[0]
        self.password = hashed_data[2]

    def __str__(self):
        return f'Username - {self.username}, Email - {self.email}, First Name - {self.first_name}, \
        Last Name - {self.last_name}, Phone - {self.phone}'

    @classmethod
    def filter_by_email(cls, email, session):
        email = session.query(cls).filter(cls.email == email).first()

        return email

    @classmethod
    def filter_by_username(cls, username, session):
        username = session.query(cls).filter(cls.username == username).first()

        return username

    @classmethod
    def filter_by_id(cls, id, session):
        id = session.query(cls).filter(cls.id == id).first()

        return id


class Password(Base):
    """
    Class describe passwords of user
    """
    SECRET_KEY = b'hQaS02VVLD4P_eedMd1tmi2w2PVFgJutLwV-6W-MBq4='

    __tablename__ = 'passwords'

    pass_id = Column('pass_id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))

    user = relationship("User", backref="passwords", cascade='all,delete')

    url = Column('url', String(250), nullable=True)
    title = Column('title', String(250), nullable=True)
    login = Column('login', String(150), nullable=False)
    password = Column('pass', LargeBinary, nullable=False)
    comment = Column('comment', String(450), nullable=True)

    @staticmethod
    def is_password_exists(pass_id):
        """
        Method check is password exists in the database
        :param pass_id:
        :return: boolean or Exception SQLAlchemy error if dont have connect to db
        """
        password = session.query(Password).filter(Password.pass_id == pass_id).first()
        return bool(password)

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
        """
        Function get user.password of of owner for this Password and combine it
        with Password.SECRET_KEY - it be a key for encrypt and decrypt passwords.
        and return Fernet object - its class that can encrypt and decrypt
        :return: Fernet
        """
        try:
            user = User.filter_by_id(self.user_id, session)
        except SQLAlchemyError as e:
            # TO DO add error into logs
            raise SQLAlchemyError(str(e))
        cipher_key = base64.urlsafe_b64encode(user.password) + Password.SECRET_KEY
        return Fernet(cipher_key)

    def crypt_password(self, raw_password):
        """Encrypt password and set it into self.password"""
        cipher = self.get_cipher()
        encrypted_password = cipher.encrypt(bytes(raw_password, encoding="utf-8"))
        self.password = encrypted_password

    def decrypt_password(self):
        """Get self.password decrypt it transform into string and return"""
        cipher = self.get_cipher()
        decrypted_password = cipher.decrypt(self.password)
        return decrypted_password.decode('utf-8')

    def __init__(self, user_id, data):
        self.login = data['login']
        self.user_id = user_id
        self.url = data['url']
        self.title = data['title']
        self.comment = data['comment']
        self.crypt_password(data['password'])

    @classmethod
    def find_pass(cls, current_user_id, pass_id, session):
        password = session.query(cls) \
            .filter(cls.user_id == current_user_id) \
            .filter(cls.pass_id == pass_id) \
            .first()
        return password

    @classmethod
    def filter_pass_by_id(cls, pass_id, session):
        password = session.query(Password).filter(Password.pass_id == pass_id).first()
        return password
