"""A Database sub-manager added as a command to Flask Application Manager"""

from flask_script import Manager
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError, IntegrityError

from . import app
from .base import Base, engine
from .models import UserModel, session

manager = Manager(usage="Perform database operations")
engine_cr = create_engine('%s://%s:%s@%s' % (app.config['DATABASE'],
                                             app.config['DB_USER'],
                                             app.config['DB_PASS'],
                                             app.config['DB_HOST']
                                             ),
                          isolation_level='AUTOCOMMIT')


@manager.command
def init():
    """Initialization of database. Drops old database, creates new database and inserts tables from SQLAlchemy models"""
    with engine_cr.connect() as conn:
        # conn.execute(f'DROP DATABASE IF EXISTS {app.config["DB_NAME"]}')
        conn.execute(f'CREATE DATABASE {app.config["DB_NAME"]}')
    Base.metadata.create_all(engine)


@manager.command
def create():
    """Creates database and inserts tables from SQLAlchemy models"""
    try:
        with engine_cr.connect() as conn:
            conn.execute(f'CREATE DATABASE {app.config["DB_NAME"]}')
    except ProgrammingError:
        print(f'ProgrammingError(SQLAlchemy): Database {app.config["DB_NAME"]} may be already exist')
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
def add_admin(username=app.config['ADMIN_NAME'], password=app.config['ADMIN_PASS'], email=app.config['ADMIN_EMAIL'],
              first_name='', last_name='', telephone=''):
    """
    Create super user, example:
    add_admin username password email [first_name] [last_name] [phone]
    """
    admin = UserModel({'username': username, 'password': password, 'email': email,
                       'first_name': first_name, 'last_name': last_name, 'phone': telephone})
    try:
        admin.is_admin = True
        session.add(admin)
        session.commit()
    except IntegrityError as err:
        print('User already exists')
        session.rollback()
    except SQLAlchemyError as err:
        print(err)
