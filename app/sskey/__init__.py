from flask import Blueprint

sskey = Blueprint('talks', __name__)

from . import routes
