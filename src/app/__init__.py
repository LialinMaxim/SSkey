from flask import Flask

from .config import config
from .api import RepresentationApi

app = Flask(__name__)
app.config.from_object(config['default'])
api = RepresentationApi(app,
                        # doc='/swagger',
                        version='0.1.2',
                        title='SSkey',
                        description='A simple application to safe yours passwords',
                        default='general',
                        default_label='Base requests')
admin_api = api.namespace('', description='Requests for admin')
user_api = api.namespace('/', description='Requests for user')

from . import routes
