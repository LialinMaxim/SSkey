from sqlalchemy import or_

from ..models import UserModel, PasswordModel, SessionObject


class AdminService:
    @staticmethod
    def get_user_list(session):
        users = session.query(UserModel).all()
        return users

    @staticmethod
    def delete_user_list(users_ids, session):
        for user_id in users_ids:
            user = UserModel.filter_by_id(user_id, session)
            if bool(user):
                passwords = session.query(PasswordModel).filter(PasswordModel.user_id == user_id).all()
                for password in passwords:
                    session.delete(password)
                session.delete(user)
        session.commit()

    @staticmethod
    def get_user_by_id(user_id, session):
        user = UserModel.filter_by_id(user_id, session)
        return user

    @staticmethod
    def delete_user_by_id(user_id, session):
        if UserModel.filter_by_id(user_id, session):
            session.query(SessionObject).filter(SessionObject.user_id == user_id).delete()
            session.query(PasswordModel).filter(PasswordModel.user_id == user_id).delete()
            session.query(UserModel).filter(UserModel.id == user_id).delete()
            session.commit()
            return True
        else:
            return False

    @staticmethod
    def search_user_by_username(username, session):
        user = UserModel.filter_by_username(username, session)
        return user

    @staticmethod
    def search_user_list(user_data, session):
        users = session.query(UserModel).filter(or_(
            UserModel.username.like(f'%{user_data}%'),
            UserModel.email.like(f'%{user_data}%'),
            UserModel.first_name.like(f'%{user_data}%'),
            UserModel.last_name.like(f'%{user_data}%'),
            UserModel.phone.like(f'%{user_data}%')
        )).all()
        return users
