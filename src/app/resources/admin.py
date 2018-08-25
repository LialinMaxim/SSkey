from flask import make_response, request, session as sess
from flask_restplus import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from .. import api
from ..base import Session
from ..models import User, Password
from ..marshmallow_schemes import UserSchema, PasswordSchema, SearchSchema, SearchPasswordUrlSchema
from ..swagger_models import user_post, password_api_model, user_login, user_put, search_password, search_password_url

session = Session()


@api.representation('/json')
class AdminUsersListResource(Resource):
    def get(self):
        """Get all users by list."""
        try:
            users = session.query(User).all()
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        return UserSchema(many=True).dump(users), 200  # OK


@api.representation('/json')
class AdminUsersResource(Resource):
    def get(self, user_id):
        """Get user by user_id."""
        try:
            user_data = User.filter_by_id(user_id, session)
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        if user_data:
            return UserSchema().dump(user_data), 200  # OK
        else:
            return f'User ID {user_id} - Not Found', 404  # Not Found

    @api.expect(user_put)
    def put(self, user_id):
        """Update user data by user_id."""
        args = request.get_json()
        # TODO validation
        # if not json_data or not isinstance(json_data, dict):
        #     return 'No input data provided', 400  # Bad Request

        try:
            if not User.is_user_exists(user_id):
                return 'User not found', 404  # Not Found
            user = User.filter_by_id(user_id, session)
            for arg_key in args.keys():
                if arg_key != 'password':
                    user.__setattr__(arg_key, args[arg_key])
            session.add(user)
            session.commit()
            msg = f'User {user.username} with id {user_id} has been successfully updated.'
            return msg, 200  # OK
        except SQLAlchemyError as err:
            return err, 500  # Internal Server Error

    def delete(self, user_id):
        """Delete user by user_id."""
        try:
            if User.filter_by_id(user_id, session):
                session.query(User).filter(User.id == user_id).delete()
                session.commit()
                return f'User ID:{user_id} has been DELETED.', 200  # OK
            else:
                return f'User ID {user_id} - Not Found', 404  # Not Found
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error


@api.representation('/json')
class PasswordListResource(Resource):
    @api.expect(password_api_model)
    def post(self, user_id):
        # TODO discuss this topic
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return 'No input data provided', 400  # Bad Request

        # Validate and deserialize input
        try:
            data = PasswordSchema().load(json_data)
        except ValidationError as err:
            return str(err), 422  # Unprocessable Entity

        if not User.filter_by_id(user_id, session):
            return f'User ID {user_id} - Not Found', 404  # Not Found

        # crate a new password
        try:
            session.add(Password(user_id, data))
            session.commit()
            return 'PASSWORD ADDED', 200  # OK
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error

    def get(self, user_id):
        """Get all passwords of user by user_id."""
        try:
            if not User.filter_by_id(user_id, session):
                return f'User ID {user_id} - Not Found', 404  # Not Found
            passwords = session.query(Password).filter(Password.user_id == user_id).all()
            passwords_serialized = []
            for password in passwords:
                passwords_serialized.append(password.serialize)
            return {'all user passwords': passwords_serialized}, 200  # OK
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error


@api.representation('/json')
class PasswordResource(Resource):
    def get(self, user_id, pass_id):
        """Get password by pass_id for user by user_id."""
        try:
            if not User.filter_by_id(user_id, session):
                return f'User ID {user_id} - Not Found', 404  # Not Found
            password = session.query(Password) \
                .filter(Password.user_id == user_id) \
                .filter(Password.pass_id == pass_id) \
                .first()
            if not password:
                return 'Password Not Found', 404  # Not Found
            return {'password': password.serialize}, 200  # OK
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error


@api.representation('/json')
class UserSearch(Resource):
    def get(self, username):
        """Get user by user name"""
        try:
            user_data = User.filter_by_username(username, session)
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        if user_data:
            return UserSchema().dump(user_data), 200  # OK
        else:
            return 'User not found', 404  # Not Found
