from flask import Flask
from flask_restful import Api

from .config import config

app = Flask(__name__)
app.config.from_object(config['default'])
api = Api(app)

# app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
# db = ...

# from src.app.errors import errors

# app.register_blueprint(errors)
from . import routes
