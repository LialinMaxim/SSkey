from flask import Flask
from config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from .sskey import sskey as sskey_blueprint
    app.register_blueprint(sskey_blueprint)

    return app
