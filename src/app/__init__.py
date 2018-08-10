from flask import Flask
from flask_restplus import Api

from .config import config

app = Flask(__name__)
from .config import config
app.config.from_object(config['default'])
api = Api(app, version='0.1.1', title='SSkey', description='A simple application to safe yours passwords')

# app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"

from . import routes
