from ..models import SessionObject


class UserService:
    @staticmethod
    def update_user(data, current_user, session):
        for key in data.keys():
            if key != 'password':
                current_user.__setattr__(key, data[key])
        session.add(current_user)

    @staticmethod
    def delete_user(token, current_user, session):
        session.query(SessionObject).filter(SessionObject.token == token).delete()
        session.delete(current_user)

    @staticmethod
    def get_access_status(user):
        """User access rights

        :param user:
        :return: '[ADMIN]' or '[USER]' string
        """
        return '[ADMIN]' if user.is_admin else '[USER]'
