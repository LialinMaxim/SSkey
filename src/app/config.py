import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'insecure_key'


class TestingConfig(Config):
    TESTING = True
    EMAIL = 'testuser@gmail.com'
    USERNAME = 'testuser'
    PASSWORD = 'testpassword'
    FIRST_NAME = 'test name'
    LAST_NAME = 'test lastname'
    PHONE = '911'

    # post a new password
    URL = 'https://www.test.com'
    TITLE = 'test.com'
    LOGIN = 'testpasslogin'
    URL_PASS = 'testpass'
    COMMENT = 'my test password for best site ever'

    # put password
    TITLE_PUT = 'anothertest.com'
    COMMENT_PUT = 'another test password'


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
