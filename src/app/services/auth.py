from flask import request

from .. import app
from ..models import UserModel, SessionObject


class AuthService:
    @staticmethod
    def is_expiry_time(user_session, session):
        if user_session is not None:
            token = request.cookies.get('token')
            out_of_time = user_session.expiration_time >= user_session.update_login_time()
            if not out_of_time:
                AuthService.delete_token(token, session)
            else:
                return True
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User token "{token}" was deleted by expired time')
        return False

    @staticmethod
    def get_user_session(session):
        token = request.cookies.get('token')
        user_session = session.query(SessionObject).filter(SessionObject.token == token).first()
        return user_session

    @staticmethod
    def get_user_by_token(session):
        token = request.cookies.get('token')
        user_session = AuthService.get_user_session(session)
        if user_session is not None:
            user = UserModel.filter_by_id(user_session.user_id, session)
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User "{user.username}" as {"[ADMIN]" if user.is_admin else "[USER]"} '
                            f'requested by token "{token}"')
            return user
        else:
            return None

    @staticmethod
    def delete_token(token, session):
        session.query(SessionObject).filter(SessionObject.token == token).delete()

    @staticmethod
    def login(data, session):
        user = UserModel.filter_by_email(data['email'], session)
        if user and user.compare_hash(data['password']):
            user_session = SessionObject(user.id)
            session.add(user_session)
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User "{user.username}" logged in as {"[ADMIN]" if user.is_admin else "[USER]"}')
            return user_session.token
        else:
            return False

    @staticmethod
    def logout(token, session):
        session.query(SessionObject).filter(SessionObject.token == token).delete()

    @staticmethod
    def register(data, session):
        session.add(UserModel(data))
