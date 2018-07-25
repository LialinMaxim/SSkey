from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config["SECRET_KEY"] = "c4a173a46b433e9f4b588e549e594c33"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    # login_manager.login_message_category = "info"

    from .sskey import sskey as sskey_blueprint
    app.register_blueprint(sskey_blueprint)

    return app
