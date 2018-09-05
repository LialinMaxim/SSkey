from logging.handlers import RotatingFileHandler
from logging import Formatter, DEBUG

from flask import Flask

from .config import config
from .api import RepresentationApi

app = Flask(__name__)
app.config.from_object(config['default'])

"""
If backupCount is non-zero, the system will save old log files 
by appending the extensions ‘.1’, ‘.2’ etc., to the filename.
"""
handler = RotatingFileHandler(app.config['LOGFILE'], maxBytes=1000000, backupCount=1)
handler.setLevel(DEBUG)
file_format = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
handler.setFormatter(Formatter(file_format))
app.logger.addHandler(handler)

api = RepresentationApi(app,
                        # doc='/swagger',
                        version='0.1.2',
                        title='SSkey',
                        description='A simple application to safe yours passwords',
                        default='general',
                        default_label='Base requests')
admin_api = api.namespace('admin', description='Requests for admin')
user_api = api.namespace('user', description='Requests for user')

from . import routes
