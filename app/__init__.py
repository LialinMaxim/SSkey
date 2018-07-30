from flask import Flask
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

app = Flask(__name__)
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"

api = Api(app)

basic_auth = HTTPBasicAuth()
# token_auth = HTTPTokenAuth('Bearer')
# token_serializer = Serializer(app.config["SECRET_KEY"], expires_in=1800)

# db = ...

from app.errors.handlers import errors

app.register_blueprint(errors)
from app import routes
