from flask import request
from flask_restplus import Resource
from sqlalchemy.exc import SQLAlchemyError

from .. import api
from ..base import Session
from ..models import UserModel
from ..marshmallow_schemes import UserSchema
from ..swagger_models import user_put

session = Session()


@api.representation('/json')
class AdminUsers(Resource):
    def get(self):
        """Get all users by list."""
        try:
            users = session.query(UserModel).all()
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        return UserSchema(many=True).dump(users), 200  # OK


@api.representation('/json')
class AdminUsersNumber(Resource):
    def get(self, user_id):
        """Get user by user_id."""
        try:
            user_data = UserModel.filter_by_id(user_id, session)
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        if user_data:
            return UserSchema().dump(user_data), 200  # OK
        else:
            return f'User ID {user_id} - Not Found', 404  # Not Found

    def delete(self, user_id):
        """Delete user by user_id."""
        try:
            if UserModel.filter_by_id(user_id, session):
                session.query(UserModel).filter(UserModel.id == user_id).delete()
                session.commit()
                return f'User ID:{user_id} has been DELETED.', 200  # OK
            else:
                return f'User ID {user_id} - Not Found', 404  # Not Found
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error


@api.representation('/json')
class AdminUsersSearch(Resource):
    def get(self, username):
        """Get user by user name"""
        try:
            user_data = UserModel.filter_by_username(username, session)
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        if user_data:
            return UserSchema().dump(user_data), 200  # OK
        else:
            return 'User not found', 404  # Not Found
