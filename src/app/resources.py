import traceback

from flask import request
from flask_restplus import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from . import app, api
from .base import session_scope
from .errors import InputDataError, AuthorizationError, AccessError, SearchError, ProcessingError
from .marshmallow_schemes import (UserSchema, UserPutSchema, UserLoginSchema, PasswordSchema, SearchSchema,
                                  PasswordPutSchema, UserIdsListSchema, AdminUsersSearchData)
from .models import UserModel
from .services.admin import AdminService
from .services.auth import AuthService
from .services.password import PasswordService
from .services.user import UserService
from .swagger_models import (user_post, user_login, password_api_model, user_put, search_password, users_ids_list,
                             admin_users_search)


@api.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    """SQLAlchemyError exception handler

    :param error: Response with error
    :return: error message, status code
    """
    tb = traceback.format_exc()
    app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 500 '
                     f'INTERNAL SERVER ERROR\n{tb}')
    return {'message': 'Internal Server Error'}, 500


@api.errorhandler(InputDataError)
def handle_input_data_error(error):
    """InputDataError exception handler

    :param error: Response with error
    :return: error message, status code
    """
    tb = traceback.format_exc()
    app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} {error.status_code} '
                     f'BAD REQUEST\n{tb}')
    return {'message': error.message}, error.status_code


@api.errorhandler(AuthorizationError)
def handle_authorized_error(error):
    """AuthorizationError exception handler

    :param error: Response with error
    :return: error message, status code
    """
    tb = traceback.format_exc()
    app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} {error.status_code} '
                     f'UNAUTHORIZED\n{tb}')
    return {'message': error.message}, error.status_code, {"WWW-Authenticate": 'Basic realm="Login Required"'}


@api.errorhandler(AccessError)
def handle_access_error(error):
    """AccessError exception handler

    :param error: Response with error
    :return: error message, status code
    """
    tb = traceback.format_exc()
    app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} {error.status_code} '
                     f'FORBIDDEN\n{tb}')
    return {'message': error.message}, error.status_code


@api.errorhandler(SearchError)
def handle_search_error(error):
    """NotFoundError exception handler

    :param error: Response with error
    :return: error message, status code
    """
    tb = traceback.format_exc()
    app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} {error.status_code} '
                     f'NOT FOUND\n{tb}')
    return {'message': error.message}, error.status_code


@api.errorhandler(ProcessingError)
def handle_processing_error(error):
    """ValidationError exception handler

    :param error: Response with error
    :return: error message, status code
    """
    tb = traceback.format_exc()
    app.logger.error(f'{request.scheme} {request.remote_addr} {request.method} {request.path} {error.status_code} '
                     f'UNPROCESSABLE ENTITY\n{tb}')
    return {'message': error.message}, error.status_code


@app.before_request
def require_login():
    """
    Require login function will be run before each request.
    The function will be called without any arguments. This function checks whether requested route is allowed to
    unregistered user or not in allowed routes. Also, checks if session isn't empty. Otherwise, it will raise
    AccessError.
    """

    admin_endpoints = ['admin_admin_users', 'admin_admin_users_search_list', 'admin_admin_users_number',
                       'admin_admin_users_search']
    if request.endpoint in admin_endpoints:
        with session_scope() as session:
            current_user = AuthService.get_user_by_token(session)
            if current_user is None:
                raise AccessError('You are not allowed to use this resource without logging in!')
            if not current_user.is_admin:
                app.logger.info(f'{request.scheme} {request.remote_addr} {request.method} {request.path} 403 '
                                f'User "{current_user.username}" as {"[ADMIN]" if current_user.is_admin else "[USER]"} '
                                f'requested allow to the administration functional')
                raise AccessError('You are not allowed to use admin functional!')

    if request.endpoint != 'login':
        allowed_routes = ['login', 'register', 'home', 'doc', 'restplus_doc.static', 'specs']
        with session_scope() as session:
            user_session = AuthService.get_user_session(session)
            expiration_time = AuthService.is_expiry_time(user_session, session)
        if not expiration_time:
            del user_session
        if request.endpoint not in allowed_routes and not expiration_time:
            raise AccessError('You are not allowed to use this resource without logging in!')


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
        Otherwise, it will raise UnauthorizedError.
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            raise InputDataError('No input data provided')  # Bad Request

        # Validate and deserialize input
        try:
            data = UserLoginSchema().load(json_data)
        except ValidationError as err:
            raise ProcessingError(err.messages)

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
        raise AuthorizationError('Could not verify your login!')


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
            raise InputDataError('No input data provided')  # Bad Request
        # Validate and deserialize input
        try:
            data = UserSchema().load(json_data)
        except ValidationError as err:
            raise ProcessingError(err.messages)
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
            raise InputDataError('No input data provided')  # Bad Request
        # Validate and deserialize input
        try:
            data = UserPutSchema().load(json_data)
        except ValidationError as err:
            raise ProcessingError(err.messages)
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
            raise InputDataError('No input data provided')  # Bad Request

        # Validate and deserialize input
        try:
            data = PasswordSchema().load(json_data)
        except ValidationError as err:
            raise ProcessingError(err.messages)

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
        :return: list with passwords that fit or 404 Error or 400 if no data provided or 422 UnprocessableEntityError
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            raise InputDataError('No input data provided')  # Bad Request

        # Validate and deserialize input
        try:
            data = SearchSchema().load(json_data)
        except ValidationError as err:
            raise ProcessingError(err.messages)

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
                raise SearchError(f'No matches found for {condition}')


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
                raise SearchError('Password Not Found')  # Not Found
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
            raise ProcessingError(err.messages)
        with session_scope() as session:
            if not PasswordService.is_password_exists(pass_id, session):
                raise SearchError('Password Not Found')
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
                raise SearchError('Password Not Found')  # Not Found


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
            raise InputDataError('No input data provided')  # Bad Request

        # Validate and deserialize input
        try:
            users_ids = (UserIdsListSchema().load(json_data))['users_ids']
        except ValidationError as err:
            raise ProcessingError(err.messages)
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
            raise SearchError(f'User ID {user_id} - Not Found')  # Not Found

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
            raise SearchError(f'User ID {user_id} - Not Found')  # Not Found


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
                raise SearchError('User not found')  # Not Found


class AdminUsersSearchList(Resource):

    @api.expect(admin_users_search)
    def post(self):
        """
        Search user by any data.

        Search user by - username, email, first_name, last_name or phone.
        """
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            raise InputDataError('No input data provided')  # Bad Request
        # Validate and deserialize input
        try:
            user_data = (AdminUsersSearchData().load(json_data))['user_data']
        except ValidationError as err:
            raise ProcessingError(err.messages)
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
                raise SearchError('User not found')  # Not Found
