from flask import Blueprint

sskey = Blueprint('sskey', __name__)

from . import routes
