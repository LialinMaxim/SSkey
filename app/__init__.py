
from flask import Flask
from flask_restful import Api


app = Flask(__name__)

api = Api(app)

# app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
# db = ...

from app import routes
