from .base import Base, Session
from .config import config
from .migrate import (create_db, create_tables, create_user, insert_data_in_db,
                      drop_tables)

from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
#
# from src.app.errors import handlers
#
# app.register_blueprint(errors)
from .models import User, Password
from .resources import Home, Smoke, EntityResource, UserResource, UserListResource, PasswordListResource, \
    PasswordResource, Login, Logout, Register
from . import routes
