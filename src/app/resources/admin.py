from flask import request
from flask_restplus import Resource
from sqlalchemy.exc import SQLAlchemyError

from .. import api
from ..base import Session
from ..models import User, SessionObject, Password
from ..marshmallow_schemes import UserSchema
from ..swagger_models import user_put

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
                token = request.cookies.get('token')
                session.query(SessionObject).filter(SessionObject.user_id == token).delete()
                session.query(Password).filter(Password.user_id == token).delete()
                session.query(User).filter(User.id == user_id).delete()
                session.commit()
                return f'User ID:{user_id} has been DELETED.', 200  # OK
            else:
                return f'User ID {user_id} - Not Found', 404  # Not Found
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
