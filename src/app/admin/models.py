from os import urandom
from hashlib import pbkdf2_hmac

from sqlalchemy import Column, String, Integer, LargeBinary
# from sqlalchemy.exc import SQLAlchemyError

from ..base import Base, Session

session = Session()


class Admin(Base):
    """
    Class describe Admin in application
    """
    __tablename__ = 'admins'
    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(100), unique=True, nullable=False)
    email = Column('email', String(150), unique=True, nullable=False)
    password = Column('userpass', LargeBinary, nullable=False)
    salt = Column('salt', LargeBinary, nullable=False)

    @staticmethod
    def generate_salt(salt_len=16):
        """
        Method generate salt of needed length. Salt use in process of get password hash
        :param salt_len:
        :return: bytes
        """
        return urandom(salt_len)

    @staticmethod
    def get_hash_password(password, salt, iterations=9723491, encoding='utf-8'):
        """
        Method create salted password hash
        :param password:
        :param salt:
        :param iterations:
        :param encoding:
        :return: tuple
        """
        hashed_password = pbkdf2_hmac(
            hash_name='sha256',
            password=bytes(password, encoding),
            salt=salt,
            iterations=iterations
        )
        return salt, iterations, hashed_password

    def compare_hash(self, input_password):
        """
        Method compare hash of input password with hash of admin password saved in database
        :param input_password:
        :return: boolean
        """
        hash_input_password = Admin.get_hash_password(input_password,
                                                      self.salt)
        return hash_input_password[2] == self.password

    def __init__(self, data):
        self.username = data['username']
        self.email = data['email']
        hashed_data = Admin.get_hash_password(data['password'], Admin.generate_salt())
        self.salt = hashed_data[0]
        self.password = hashed_data[2]
