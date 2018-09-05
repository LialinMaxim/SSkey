import os
from logging import Formatter
from logging.handlers import RotatingFileHandler


def make_logger(app):
    """Logger

    Creates logger handler for application.

    :param app: Application
    """

    if not os.path.exists('logs/'):
        os.makedirs('logs/')

    file_handler = RotatingFileHandler(app.config['LOGFILE'], maxBytes=1000000, backupCount=1)
    file_handler.setLevel(app.config['HANDLER_LEVEL'])
    file_format = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    file_handler.setFormatter(Formatter(file_format))
    app.logger.addHandler(file_handler)
