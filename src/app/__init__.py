from .base import Base, Session
from .config import config
from .migrate import (create_db, create_tables, create_user, insert_data_in_db,
                      drop_tables)
from .models import User, Password
from .resources import Home, Smoke, EntityResource, UserResource, \
    UserListResource, PasswordListResource, PasswordResource
from .models import User, Password, RevokedTokenModel
from .resources import Home, Smoke, EntityResource, UserResource, Login, Logout, LogoutRefresh, TokenRefresh

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)

api = Api(app)

app.config["JWT_SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"

jwt = JWTManager(app)
# db = ...

# from src.app.errors import errors

# app.register_blueprint(errors)
from . import routes
