from abc import ABCMeta, abstractmethod

from flask_restful import Resource, reqparse

from . import Session
from . import User

session = Session()


class Home(Resource):
    def get(self):
        return {'message': 'Home Page'}, 200, {
            'Access-Control-Allow-Origin': '*'}


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
        else:
            user = User(args['username'], args['email'], args['userpass'],
                        args['first_name'], args['last_name'], args['phone'])
            status = 200
            msg = "USER {0} REGISTRATION SUCCESSFUL".format(user.username)
            try:
                session.add(user)
                session.commit()
            except Exception as e:
                msg = str(e)
                status = 500
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='')
        parser.add_argument('email', type=str, help='')

        args = parser.parse_args()
        try:
            if args['username']:
                users = session.query(User).filter(
                    User.username == args['username']).all()
            elif args['email']:
                users = session.query(User).filter(
                    User.email == args['email']).all()
            else:
                users = session.query(User).all()
        except Exception as e:
            msg = str(e)
            status = 500
            return {'msg': msg}, status, {'Access-Control-Allow-Origin': '*'}
        status = 200
        users_resp = []
        for user in users:
            users_resp.append(user.serialize)
        return {'users': users_resp}, status, {
            'Access-Control-Allow-Origin': '*'}

    def put(self):
        pass

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='')
        args = parser.parse_args()
        if args['username']:
            try:
                session.query(User).filter(
                    User.username == args['username']).delete()
                session.commit()
                status = 200
                msg = 'User {0} has been deleted successfully'.format(
                    args['username'])
            except Exception as e:
                msg = str(e)
                status = 500
        else:
            msg = "USERNAME not given!"
            status = 400
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}
