"""A Database sub-manager added as a command to Flask Application Manager"""

import os
from flask_script import Manager
from app.base import Base, engine, POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST, POSTGRES_NAME
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from dotenv import load_dotenv

from .models import UserModel, session

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

manager = Manager(usage="Perform database operations")

engine_cr = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}', isolation_level='AUTOCOMMIT')


@manager.command
def init():
    """Initialization of database. Drops old database, creates new database and inserts tables from SQLAlchemy models"""
    with engine_cr.connect() as conn:
        conn.execute(f'DROP DATABASE IF EXISTS {POSTGRES_NAME}')
        conn.execute(f'CREATE DATABASE {POSTGRES_NAME}')
    Base.metadata.create_all(engine)


@manager.command
def create():
    """Creates database and inserts tables from SQLAlchemy models"""
    try:
        with engine.connect() as conn:
            conn.execute(f'CREATE DATABASE {POSTGRES_NAME}')
    except ProgrammingError:
        print(f'ProgrammingError(SQLAlchemy): Database {POSTGRES_NAME} may be already exist')
    Base.metadata.create_all(engine)


@manager.command
def update():
    """Recreates and updates database tables from SQLAlchemy models"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@manager.command
def drop():
    """Drops database tables"""
    Base.metadata.drop_all(engine)


@manager.command
def add_admin(username, password, email):
    admin = UserModel({'username': username, 'password': password, 'email': email,
                  'first_name': '', 'last_name': '', 'phone': ''})
    try:
        admin.is_admin = True
        session.add(admin)
        session.commit()
    except SQLAlchemyError as err:
        print(err)
