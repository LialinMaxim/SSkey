from flask import Flask, Blueprint
from flask_restplus import Api, fields


app = Flask(__name__)
api = Api(app, version='0.1.1', title='SSkey', description='A simple application to safe yours passwords',)


# app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
# db = ...

# from src.app.errors import errors

# app.register_blueprint(errors)

from .base import Base, Session
from .migrate import (create_db, create_tables, create_user, insert_data_in_db,
                      drop_tables)
from .config import config
from .resources import Smoke, EntityResource, UserResource, \
    UserListResource, PasswordListResource, PasswordResource  # Home,
from .models import User, Password, SessionObject
from . import routes