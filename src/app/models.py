import datetime
import hashlib
import os
import base64

from sqlalchemy import Column, String, Integer, Date, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet

from .base import Base, Session

session = Session()


class User(Base):
    """
    Class describe User in application
    """
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
        """
        Method generate salt of needed length. Salt use in process of get password hash
        :param salt_len:
        :return:
        """
        return os.urandom(salt_len)

    @staticmethod
    def get_hash_password(userpass, salt, iterations=100001, encoding='utf-8'):
        """
        Method create salted password hash
        :param userpass:
        :param salt:
        :param iterations:
        :param encoding:
        :return: tuple
        """
        hashed_password = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=bytes(userpass, encoding),
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
        return hash_input_password[2] == self.userpass

    # TODO with Marshmallow
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
        hashed_data = __class__.get_hash_password(password, User.generate_salt())
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
        cipher_key = base64.urlsafe_b64encode(user.userpass) + Password.SECRET_KEY
        return Fernet(cipher_key)

    def crypt_and_save_password(self, raw_password):
        """Encrypt password and set it into self.password"""
        cipher = self.get_cipher()
        encrypted_password = cipher.encrypt(bytes(raw_password, encoding="utf-8"))
        self.password = encrypted_password

    def decrypt_password(self):
        """Get self.password decrypt it transform into string and return"""
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
