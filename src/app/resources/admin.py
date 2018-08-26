from flask import request
from flask_restplus import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

from .. import api
from ..base import Session
from ..models import User, Password
from ..marshmallow_schemes import UserSchema, UserIdsListSchema, AdminUsersSearchData
from ..swagger_models import users_ids_list, admin_users_search

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

    @api.expect(users_ids_list)
    def delete(self):
        """
        Batch Users removal.

        Remove users by list. Get list of users ids. If delete successfull, return 200 OK
        Otherwise, return 500 or 400 error.
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return 'No input data provided', 400  # Bad Request

        # Validate and deserialize input
        try:
            users_ids = (UserIdsListSchema().load(json_data))['users_ids']
        except ValidationError as err:
            return str(err), 422  # Unprocessable Entity
        try:
            for user_id in users_ids:
                user = User.filter_by_id(user_id, session)
                if bool(user):
                    passwords = session.query(Password).filter(Password.user_id == user_id).all()
                    for password in passwords:
                        session.delete(password)
                    session.delete(user)
            session.commit()
            return 'Users has been deleted successfully', 200
        except SQLAlchemyError as err:
            return str(err), 500


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

    def delete(self, user_id):
        """Delete user by user_id."""
        try:
            user = User.filter_by_id(user_id, session)
            if bool(user):
                passwords = session.query(Password).filter(Password.user_id == user_id).all()
                for password in passwords:
                    session.delete(password)
                session.delete(user)
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


@api.representation('/json')
class AdminUsersSearch(Resource):
    """
    Search user by any data - username, email, first_name, last_name or phone
    """

    @api.expect(admin_users_search)
    def post(self):
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return 'No input data provided', 400  # Bad Request
        # Validate and deserialize input
        try:
            user_data = (AdminUsersSearchData().load(json_data))['user_data']
        except ValidationError as err:
            return str(err), 422  # Unprocessable Entity
        # Search users
        try:
            users = session.query(User).filter(
                or_(User.username.like(f'%{user_data}%'), User.email.like(f'%{user_data}%'),
                    User.first_name.like(f'%{user_data}%'), User.last_name.like(f'%{user_data}%'),
                    User.phone.like(f'%{user_data}%')
                    )).all()
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        if users:
            return UserSchema(many=True).dump(users), 200  # OK
        else:
            return 'User not found', 404  # Not Found
