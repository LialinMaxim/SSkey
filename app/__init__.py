
from flask import Flask
from app.routes import Smoke, UserResource
from flask_restful import Api



app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
#         user=DBUSER,
#         passwd=DBPASS,
#         host=DBHOST,
#         port=DBPORT,
#         db=DBNAME)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = 'foobarbaz'

api = Api(app)

from app import routes

api.add_resource(Smoke, '/smoke')
api.add_resource(UserResource, '/user')


# from flask import Flask
# from config import config
#
#
# def create_app(config_name):
#     app = Flask(__name__)
#     app.config.from_object(config[config_name])
#
#     return app
#
#
# from app import routes
