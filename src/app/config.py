import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    HANDLER_LEVEL = os.environ.get('HANDLER_LEVEL')
    HANDLER_FORMAT = '%(asctime)s - %(levelname)s: %(message)s'


class DevelopmentConfig(Config):
    DEBUG = True
    LOGFILE = 'logs/Development.log'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'insecure_key'


class TestingConfig(Config):
    TESTING = True
    # post a new user
    EMAIL = 'testuser@gmail.com'
    USERNAME = 'testuser'
    PASSWORD = 'testpassword'
    FIRST_NAME = 'test name'
    LAST_NAME = 'test lastname'
    PHONE = '911'

    # admin post data
    ADMIN_EMAIL = 'admin_email@gmail.com'
    ADMIN_USERNAME = 'admin911'
    ADMIN_PASSWORD = 'admin911'

    # tuple wit tuples of test users (user1, user2, user3)
    # user = (email, username, password, first_name, last_name, phone)
    USER_BATCH = (
        ('alice@gmail.com', 'alice', 'alice', 'Alice', '', '333-555-333'),
        ('bob@yandex.com', 'walle', 'bob', '', '', '333-555-333'),
        ('eva@gmail.com', 'eva', 'eva', 'Eva', 'Brown', '333-555-333'),
        ('alex@gmail.com', 'alex', 'alex', 'Alesha', '', '333-555-333'),
    )

    # post a new password
    URL = 'https://www.test.com'
    TITLE = 'test.com'
    LOGIN = 'testpasslogin'
    URL_PASS = 'testpass'
    COMMENT = 'my test password for the best site ever'

    # put password
    TITLE_PUT = 'anothertest.com'
    COMMENT_PUT = 'another test password'


class ProductionConfig(Config):
    DEBUG = False
    LOGFILE = 'logs/Production.log'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    # 'RESTPLUS_VALIDATE': True,
    'default': DevelopmentConfig
}
