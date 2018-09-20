from flask import Flask

from .api import RepresentationApi
from .config import config
from .logger import make_logger

app = Flask(__name__)
app.config.from_object(config['default'])
make_logger(app)

api = RepresentationApi(app,
                        version='0.1.2',
                        title='SSkey',
                        description='A simple application to safe yours passwords',
                        default='general',
                        default_label='Base requests')
admin_api = api.namespace('admin', description='Requests for admin')
user_api = api.namespace('user', description='Requests for user')

from . import routes
