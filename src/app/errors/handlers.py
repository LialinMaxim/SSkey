from flask import Blueprint

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return "That page does not exist. Please, try a different location", 404


@errors.app_errorhandler(403)
def error_403(error):
    return "Please, check your account and try again", 403


@errors.app_errorhandler(500)
def error_500(error):
    return "We're experiencing some trouble on our end. Please, try again in the near future", 500
