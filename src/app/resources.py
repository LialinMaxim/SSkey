import traceback

from flask import make_response, request
from flask_restplus import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from . import app, api
from .base import Session, session_scope
from .marshmallow_schemes import (UserSchema, UserPutSchema, UserLoginSchema, PasswordSchema, SearchSchema,
                                  PasswordPutSchema, UserIdsListSchema, AdminUsersSearchData)
from .models import UserModel
from .services.admin import AdminService
from .services.auth import AuthService
from .services.password import PasswordService
from .services.user import UserService
from .swagger_models import (user_post, user_login, password_api_model, user_put, search_password, users_ids_list,
                             admin_users_search)


@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    """Database exception logger

    :param error: Response with error
    :return: error
    """
    tb = traceback.format_exc()
    app.logger.error(f'5xx INTERNAL SERVER ERROR\n{tb}')
    return error


@app.after_request
def response_logger(response):
    if response.status_code == 400:
        app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 400 '
                         f'BAD REQUEST - {response.get_data(True)}')
        return response
    elif response.status_code == 403:
        app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 403 '
                         f'FORBIDDEN - {response.get_data(True)}')
        return response
    elif response.status_code == 422:
        app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 422 '
                         f'UNPROCESSABLE ENTITY - {response.get_data(True)}')
        return response
    else:
        return response


@app.before_request
def require_login():
    """
    Require login function will be run before each request.
    The function will be called without any arguments. This function checks whether requested route is allowed to
    unregistered user or not in allowed routes. Also, checks if session isn't empty. Otherwise, it will return 403 error
    """

    admin_endpoints = ['admin_admin_users', 'admin_admin_users_search_list', 'admin_admin_users_number',
                       'admin_admin_users_search']
    if request.endpoint in admin_endpoints:
        session = Session()
        try:
            current_user = AuthService.get_user_by_token(session)
        except AttributeError:
            return make_response('You are not allowed to use this resource without logging in!', 403)
        finally:
            session.close()
        if not current_user.is_admin:
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 403 '
                            f'User "{current_user.username}" requested allow to the administration functional')
            return make_response('You are not allowed to use admin functional', 403)

    if request.endpoint != 'login':
        allowed_routes = ['login', 'register', 'home', 'doc', 'restplus_doc.static', 'specs']
        with session_scope() as session:
            user_session = AuthService.get_user_session(session)
        expiration_time = is_expiry_time(user_session)
        if not expiration_time:
            del user_session
        if request.endpoint not in allowed_routes and not expiration_time:
            return make_response('You are not allowed to use this resource without logging in!', 403)


def is_expiry_time(user_session):
    if user_session:
        token = request.cookies.get('token')
        out_of_time = user_session.update_login_time() <= user_session.expiration_time
        if not out_of_time:
            with session_scope() as session:
                AuthService.delete_token(token, session)
        else:
            return True
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                        f'User token "{token}" was deleted by expired time')
    return False


# GENERAL RESOURCES:
# Home,
# Smoke,
# Login,
# Logout,
# Register


class Home(Resource):
    def get(self):
        """Simple test that works without authorization."""
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                        f'Requested Home Page')
        return {'message': 'This is a Home Page'}, 200  # OK


class Smoke(Resource):
    def get(self):
        """Simple test that requires authorization."""
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                        f'Requested Smoke Page')
        return {'message': 'OK'}, 200  # OK


class Login(Resource):
    @api.expect(user_login)
    def post(self):
        """
        Login resource.

        Checks whether entered data is in DB. Create user session based on its id and then sets session lifetime.
        Otherwise, it will return 401 error.
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            data = UserLoginSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity

        # Check if a new user is not exist in data base
        with session_scope() as session:
            token = AuthService.login(data, session)
        if token:
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User with email "{data["email"]}" was assigned a token "{token}"')
            return {'message': f'You are LOGGED IN as {data["email"]}'}, 200, \
                   {'Set-Cookie': f'token="{token}"'}
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 401 '
                        f'User with email "{data["email"]}" tried to log in')
        return {'message': 'Could not verify your login!'}, 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}


class Logout(Resource):
    def get(self):
        """
        Logout resource.

        Remove the username from the session.
        """
        token = request.cookies.get('token')
        with session_scope() as session:
            AuthService.logout(token, session)
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                        f'User token "{token}" was deleted by logout')
        return {'message': 'Dropped!'}, 200  # OK


class Register(Resource):
    @api.expect(user_post)
    def post(self):
        """
        Register resource.

        Parsing requested data, checks if username or email doesn't exit in DB, then create user in DB. 200 OK
        Otherwise, return 500 or 400 error.
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request
        # Validate and deserialize input
        try:
            data = UserSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity
        # Check if a new user is not exist in data base
        with session_scope() as session:
            if UserModel.filter_by_username(data['username'], session):
                return {'message': f'User with username: {data["username"]} is ALREADY EXISTS.'}, 200  # OK
            elif UserModel.filter_by_email(data['email'], session):
                return {'message': f'User with email: {data["email"]} is ALREADY EXISTS.'}, 200  # OK
            else:
                # create a new user
                AuthService.register(data, session)
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User "{data["username"]}" registered with email {data["email"]}')
            return {'message': f"USER {data['username']} ADDED"}, 200  # OK


# RESOURCES FOR USER:
# User,
# UserPasswords,
# UserPasswordsSearch,
# UserPasswordsNumber


class User(Resource):
    def get(self):
        """Get user's data."""
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                            f'requested his own data')
            return {'user': UserSchema().dump(current_user)}, 200

    @api.expect(user_put)
    def put(self):
        """Update user's data."""
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request
        # Validate and deserialize input
        try:
            data = UserPutSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            UserService.update_user(data, current_user, session)
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                            f'updated his own data')
            return {'message': f'User {current_user.username} UPDATED'}, 200

    def delete(self):
        """Remove user with all his data."""
        token = request.cookies.get('token')
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            UserService.delete_user(token, current_user, session)
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                        f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                        f'deleted himself')
        return {'message': f'User {current_user.username} DELETED'}, 200


class UserPasswords(Resource):
    """
    User password resource.

    User gets his all passwords and may create a new one.
    """

    def get(self):
        """
        Get list of user's passwords.

        User defines by sess email, returns a list of passwords for current logged in user.
        :return: list of passwords or 500 SQLAlchemyError
        """
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            passwords_serialized = PasswordService.get_password_list(current_user, session)
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                            f'requested his own passwords')
        return {'passwords': passwords_serialized}, 200  # OK

    @api.expect(password_api_model)
    def post(self):
        """
        Create a new user's password.

        Create a new password for current logged in user, without specifying any parameters.
        :return: 200 OK or 500 SQLAlchemyError
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            data = PasswordSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity

        # create a new password
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            password_title = PasswordService.add_password(data, current_user, session)
        return {'message': f'PASSWORD with title {password_title} ADDED'}, 200  # OK


class UserPasswordsSearch(Resource):
    """
    Search for particular passwords using password's description.
    """

    @api.expect(search_password)
    def post(self):
        """
        Search for passwords by its description.

        Get json data, tries to find any matches in current logged in user list of passwords by its title and comment.
        :return: list with passwords that fit or 404 Error or 400 if no data provided or 422 ValidationError
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            data = SearchSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity

        condition = data.get('condition')
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            passwords_by_condition = PasswordService.search_password_by_condition(current_user.id, condition, session)
            if passwords_by_condition:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                                f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                                f'searched password by condition "{condition}"')
                return {'passwords': passwords_by_condition}, 200
            else:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 404 '
                                f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                                f'tried to search password by condition "{condition}"')
                return {'message': f'No matches found for {condition}'}, 404


class UserPasswordsNumber(Resource):
    """
    Class for dealing with user's passwords.

    User can get a password by id, update password by id and delete password by id.
    """

    def get(self, pass_id):
        """
        Get particular password by pass_id.

        Get password from current logged in user by pass_id.
        :param pass_id: id of specific user's password
        :return: password or 500 SQLAlchemyError
        """
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            password = PasswordService.get_password_by_id(current_user.id, pass_id, session)
            if not password:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 404 '
                                f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                                f'tried to search password by id "{pass_id}"')
                return {'message': 'Password Not Found'}, 404  # Not Found
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                            f'searched password by id "{pass_id}"')
            return {'password': password.serialize}, 200  # OK

    @api.expect(password_api_model)
    def put(self, pass_id):
        """
        Update password data.

        You can update all data of password or just a part of it.
        :param pass_id: id of password data you'd like to update of
        :return: 200 OK or 500 SQLAlchemyError
        """
        json_data = request.get_json()
        try:
            data = PasswordPutSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity
        with session_scope() as session:
            if not PasswordService.is_password_exists(pass_id, session):
                return {'message': 'Password Not Found'}, 404
            password = PasswordService.filter_password_by_id(pass_id, session)
            updated_password = PasswordService.update_password(password, data, session)
            return {'message': f'Data for {updated_password.title} has been updated successfully'}, 200

    def delete(self, pass_id):
        """
        Delete specific password.

        Delete password from current logged in user by pass_id.
        :param pass_id: id of specific user's password
        :return: 200 OK or 404 Password Not Found or 500 SQLAlchemyError
        """
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            password = PasswordService.get_password_by_id(current_user.id, pass_id, session)
            if password:
                PasswordService.delete_password(pass_id, current_user, session)
                session.commit()
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                                f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                                f'deleted password by id "{pass_id}"')
                return {'message': f'Password ID {pass_id} DELETED'}, 200  # OK
            else:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 404 '
                                f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                                f'tried to deleted password by id "{pass_id}"')
                return {'message': 'Password Not Found'}, 404  # Not Found


# RESOURCES FOR ADMIN:
# AdminUsers,
# AdminUsersNumber,
# AdminUsersSearch,
# AdminUsersSearchList


class AdminUsers(Resource):
    def get(self):
        """Get all users by list."""
        with session_scope() as session:
            users = AdminService.get_user_list(session)
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                        f'Admin requested user list')
        return {'users': UserSchema(many=True).dump(users)}, 200  # OK

    @api.expect(users_ids_list)
    def delete(self):
        """
        Batch Users removal.

        Remove users by list. Get list of users ids. If delete successfull, return 200 OK
        Otherwise, return 500 or 400 error.
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            users_ids = (UserIdsListSchema().load(json_data))['users_ids']
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity
        with session_scope() as session:
            AdminService.delete_user_list(users_ids, session)
        app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                        f'Admin deleted users by ids {users_ids}')
        return {'message': 'Users has been deleted successfully'}, 200


class AdminUsersNumber(Resource):
    def get(self, user_id):
        """Get user by user_id."""
        with session_scope() as session:
            user = AdminService.get_user_by_id(user_id, session)
        if user:
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'Admin requested user by id "{user_id}"')
            return {'user': UserSchema().dump(user)}, 200  # OK
        else:
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 404 '
                            f'Admin tried to find user by id "{user_id}"')
            return {'message': f'User ID {user_id} - Not Found'}, 404  # Not Found

    def delete(self, user_id):
        """Delete user by user_id."""
        with session_scope() as session:
            delete_status = AdminService.delete_user_by_id(user_id, session)
        if delete_status:
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                            f'Admin deleted user by id "{user_id}"')
            return {'message': f'User ID:{user_id} has been DELETED.'}, 200  # OK
        else:
            app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 404 '
                            f'Admin tried to delete user by id "{user_id}"')
            return {'message': f'User ID {user_id} - Not Found'}, 404  # Not Found


class AdminUsersSearch(Resource):
    def get(self, username):
        """Get user by user name"""
        with session_scope() as session:
            user = AdminService.search_user_by_username(username, session)
            if user:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                                f'Admin searched user by username "{username}"')
                return {'user': UserSchema().dump(user)}, 200  # OK
            else:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 404 '
                                f'Admin tried to find user by username "{username}"')
                return {'message': 'User not found'}, 404  # Not Found


class AdminUsersSearchList(Resource):

    @api.expect(admin_users_search)
    def post(self):
        """
        Search user by any data.

        Search user by - username, email, first_name, last_name or phone.
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request
        # Validate and deserialize input
        try:
            user_data = (AdminUsersSearchData().load(json_data))['user_data']
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity
        # Search users
        with session_scope() as session:
            users = AdminService.search_user_list(user_data, session)
            if users:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 200 '
                                f'Admin searched user by data "{user_data}"')
                return {'users': UserSchema(many=True).dump(users)}, 200  # OK
            else:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 404 '
                                f'Admin tried to find user by data "{user_data}"')
                return {'message': 'User not found'}, 404  # Not Found
