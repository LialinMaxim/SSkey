from flask import Flask

from .config import config
from .api import RepresentationApi

app = Flask(__name__)
app.config.from_object(config['default'])
api = RepresentationApi(app,
                        # doc='/swagger',
                        version='0.1.2',
                        title='SSkey',
                        description='A simple application to safe yours passwords')

from . import routes
