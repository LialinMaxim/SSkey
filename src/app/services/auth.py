from flask import request

from .. import app
from ..models import UserModel, SessionObject


class AuthService:
    @staticmethod
    def get_user_session(session):
        token = request.cookies.get('token')
        user_session = session.query(SessionObject).filter(SessionObject.token == token).first()
        return user_session

    @staticmethod
    def get_user_by_token(session):
        token = request.cookies.get('token')
        user_session = AuthService.get_user_session(session)
        user = UserModel.filter_by_id(user_session.user_id, session)
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                        f'User "{user.username}" requested by token "{token}"')
        return user

    @staticmethod
    def delete_token(token, session):
        session.query(SessionObject).filter(SessionObject.token == token).delete()
