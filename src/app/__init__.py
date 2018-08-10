from flask import Flask, Blueprint
from flask_restplus import Api, fields

from .config import config

app = Flask(__name__)
app.config.from_object(config['default'])
api = Api(app, version='0.1.1', title='SSkey', description='A simple application to safe yours passwords',)

# app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
# db = ...

# from src.app.errors import errors

# app.register_blueprint(errors)

from . import routes
