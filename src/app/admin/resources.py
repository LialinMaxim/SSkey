from flask_restplus import Resource
from sqlalchemy.exc import SQLAlchemyError

from .. import api
from ..base import Session
from ..scheme import UserSchema
from ..models import User

session = Session()


@api.representation('/json')
class AdminTest(Resource):
    def get(self):
        return 'OK', 200  # OK


@api.representation('/json')
class AdminUsersListResource(Resource):
    def get(self):
        try:
            users = session.query(User).all()
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        return UserSchema(many=True).dump(users), 200  # OK


@api.representation('/json')
class AdminUsersResource(Resource):
    def get(self, user_id):
        try:
            user_data = User.filter_by_id(user_id, session)
        except SQLAlchemyError as err:
            return str(err), 500  # Internal Server Error
        if user_data:
            return UserSchema().dump(user_data), 200  # OK
        else:
            return f'User ID {user_id} - Not Found', 404  # Not Found
