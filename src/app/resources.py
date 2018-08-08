from flask import jsonify, request
from abc import ABCMeta, abstractmethod
from sqlalchemy.exc import SQLAlchemyError
from flask_restplus import Resource, reqparse, fields
from marshmallow import ValidationError

from . import api
from .base import Session
from .models import User, Password, SessionObject
from .shemas import UserSchema, PasswordSchema

session = Session()


class Home(Resource):
    def get(self):
        return {'message': 'Home Page'}, 200, {
            'Access-Control-Allow-Origin': '*'}


class Smoke(Resource):
    def get(self):
        return {'message': 'OK'}, 200, {'Access-Control-Allow-Origin': '*'}


class EntityListResource(Resource):
    """
    Abstract class of Entity list contain method POST and GET work with routs type /entities
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self):
        raise NotImplementedError

    @abstractmethod
    def post(self):
        raise NotImplementedError


class EntityResource(Resource):
    """
    Abstract class of Entity contain method  GET PUT delete work with routs type /entities/<int:entity_id>
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def put(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError


user_post = api.model('Crate New User', {
    'email': fields.String,
    'username': fields.String,
    'userpass': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'phone': fields.Integer,
})


class UserListResource(Resource):
    def get(self):
        try:
            users = session.query(User).all()
        except SQLAlchemyError:
            return {'msg': SQLAlchemyError}, 500,  # headers
        users_serialized = []
        for user in users:
            users_serialized.append(user.serialize)
        return {'users': users_serialized}, 200,  # headers

    @api.expect(user_post)
    def post(self):
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            data = UserSchema().load(json_data)
        except ValidationError as err:
            return {'message': str(err)}, 422  # Unprocessable Entity

        # Check if a new user is not exist in data base
        if session.query(User).filter(User.username == data['username']).first():
            msg = "User with username: '{0}' is ALREADY EXISTS.".format(data['username'])
            return {'message': msg}, 200  # OK
        elif session.query(User).filter(User.email == data['email']).first():
            msg = "User with email: '{0}' is ALREADY EXISTS".format(data['email'])
            return {'message': msg}, 200  # OK
        else:
            # TODO optimization USER CLASS
            # user = User(data)
            user = User(data['username'], data['email'], data['userpass'],
                        data['first_name'], data['last_name'], data['phone'])

            # crate a new user
            try:
                session.add(user)
                session.commit()
                msg = "New user: '{0}' is SUCCESSFUL ADDED".format(user.username)
                return {'message': msg}, 200  # OK
            except SQLAlchemyError:
                return {'message': SQLAlchemyError}, 500  # Internal Server Error


class UserResource(EntityResource):
    def get(self, user_id):
        try:
            user_data = session.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError:
            return {'message': SQLAlchemyError}, 500  # Internal Server Error
        if user_data:
            return {'user': UserSchema().dump(user_data)}, 200  # OK
        else:
            return {'message': 'User not found'}, 404  # Not Found

    def put(self, user_id):
        pass

    def delete(self, user_id):
        try:
            if session.query(User).filter(User.id == user_id).first():
                session.query(User).filter(User.id == user_id).delete()
                session.commit()
                msg = 'User ID:{0} has been DELETED.'.format(user_id)
                return {'message': msg}, 200  # OK
            else:
                msg = 'User ID:{0} NOT EXISTS!'.format(user_id)
                return {'message': msg}, 404  # Not Found
        except SQLAlchemyError:
            return {'message': SQLAlchemyError}, 500  # Internal Server Error


class PasswordResource(EntityResource):
    def get(self, user_id, pass_id):
        headers = {'Access-Control-Allow-Origin': '*'}
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {'msg': 'User not found'}, 404, headers
            passwords = session.query(Password).filter(Password.user_id == user_id).all()
            passwords_serialized = []
            for password in passwords:
                passwords_serialized.append(password.serialize)
        except SQLAlchemyError as e:
            return {'msg': e}, 500, headers
        return {'passwords': passwords_serialized}, 200, headers

    def put(self, user_id):
        pass

    def delete(self, user_id):
        pass


class PasswordListResource(EntityListResource):
    def get(self):
        pass

    def post(self):
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
