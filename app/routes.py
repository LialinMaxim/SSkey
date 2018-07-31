from flask_restful import Resource, reqparse
from abc import ABCMeta, abstractmethod
from sqlalchemy.exc import SQLAlchemyError

from app.models import User
from app import app, api
from base import Session

session = Session()


class Home(Resource):
    def get(self):
        return {'message': 'Home Page'}, 200, {'Access-Control-Allow-Origin': '*'}


class Smoke(Resource):
    def get(self):
        return {'message': 'OK'}, 200, {'Access-Control-Allow-Origin': '*'}


class EntityResource(Resource):
    __metaclass__ = ABCMeta

    @abstractmethod
    def post(self):
        raise NotImplementedError

    @abstractmethod
    def get(self):
        raise NotImplementedError

    @abstractmethod
    def put(self):
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError


class UserResource(EntityResource):
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='')
        parser.add_argument('username', type=str, help='')
        parser.add_argument('userpass', type=str, help='')
        parser.add_argument('first_name', type=str, help='')
        parser.add_argument('last_name', type=str, help='')
        parser.add_argument('phone', type=str, help='')
        args = parser.parse_args()

        if not User.validate_user(args):
            msg = "REQUIRED DATA NOT VALID OR BLANK"
            status = 400
        elif session.query(User).filter(User.username == args['username']).first():
            msg = "User with username = {0} already exists".format(args['username'])
            status = 200
        elif session.query(User).filter(User.email == args['email']).first():
            msg = "Useer with email = {0} already exists".format(args['email'])
            status = 200
        else:
            user = User(args['username'], args['email'], args['userpass'], args['first_name'],
                        args['last_name'], args['phone'])
            status = 200
            msg = "USER {0} REGISTRATION SUCCESSFUL".format(user.username)
            try:
                session.add(user)
                session.commit()
            except SQLAlchemyError as e:
                msg = e
                status = 500
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, help='')

        headers = {'Access-Control-Allow-Origin': '*'}
        args = parser.parse_args()
        try:
            if args['user_id']:
                user = session.query(User).filter(User.id == args['user_id']).first()
                if not user:
                    return {'user': None}, 200, headers
            else:
                return {'msg': 'User id not given'}, 400, headers
        except SQLAlchemyError as e:
            return {'msg': e}, 500, headers
        return {'user': user.serialize}, 200, headers

    def put(self):
        pass

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, help='')

        args = parser.parse_args()

        if args['user_id']:
            try:
                if session.query(User).filter(User.id == args['user_id']).first():
                    session.query(User).filter(User.id == args['user_id']).delete()
                    session.commit()
                    status = 200
                    msg = 'User with id = {0} has been deleted successfully'.format(args['user_id'])
                else:
                    msg = 'User with id = {0} not exists!'.format(args['user_id'])
            except SQLAlchemyError as e:
                msg = e
                status = 500
        else:
            msg = "User id not given!"
            status = 400
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}


api.add_resource(Home, '/', "/home")
api.add_resource(Smoke, '/smoke')
api.add_resource(UserResource, '/user')
