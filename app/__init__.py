import sqlalchemy
from flask import Flask

app = Flask(__name__)
# app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
# db = ...

from app import routes




# from flask import Flask
# from config import config
#
#
# def create_app(config_name):
#     app = Flask(__name__)
#     app.config.from_object(config[config_name])
#
#     return app
#
#
# from app import routes
