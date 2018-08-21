import datetime
import hashlib
import os


from sqlalchemy import Column, String, Integer, Date, LargeBinary
from sqlalchemy.exc import SQLAlchemyError

from ..models import User
from ..base import Base, Session

session = Session()


class Admin(User):
    """
    Class describe Admin in application
    """
    __tablename__ = 'admins'
    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(100), unique=True, nullable=False)
    email = Column('email', String(150), unique=True, nullable=False)
    password = Column('userpass', LargeBinary, nullable=False)
    salt = Column('salt', LargeBinary, nullable=False)

