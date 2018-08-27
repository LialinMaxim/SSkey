from flask import make_response, request
from flask_restplus import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

from . import app, api
from .base import Session
from .models import UserModel, PasswordModel, SessionObject
from .marshmallow_schemes import UserSchema, PasswordSchema, SearchSchema, SearchPasswordUrlSchema, \
    PasswordPutSchema, UserIdsListSchema, AdminUsersSearchData
from .swagger_models import user_post, user_login, password_api_model, user_put, search_password, \
    search_password_url, users_ids_list, admin_users_search

session = Session()


def get_user_by_token():
    token = request.cookies.get('token')
    user_session = session.query(SessionObject).filter(SessionObject.token == token).first()
    user = UserModel.filter_by_id(user_session.user_id, session)
    return user


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
        user = get_user_by_token()
        if not user.is_admin:
            return make_response('You are not allowed to use admin functional', 403)
    if request.endpoint != 'login':
        allowed_routes = ['login', 'register', 'home', 'doc', 'restplus_doc.static', 'specs']
        token_from_cookie = request.cookies.get('token')
        user_session = session.query(SessionObject).filter(SessionObject.token == token_from_cookie).first()
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
            session.query(SessionObject).filter(SessionObject.token == token).delete()
            session.commit()
        else:
            return True
    return False


# GENERAL RESOURCES:
# Home,
# Smoke,
# Login,
# Logout,
# Register


class Home(Resource):
    """Simple test that works without authorization."""

    def get(self):
        return {'message': 'This is a Home Page'}, 200  # OK


class Smoke(Resource):
    """Simple test that requires authorization."""

    def get(self):
        return {'message': 'OK'}, 200  # OK


class Login(Resource):
    """
    Login resource.

    Checks whether entered data is in DB. Create user session based on its id and then sets session lifetime.
    Otherwise, it will return 401 error.
    """

    @api.expect(user_login)
    def post(self):
        data = request.get_json()
        user = UserModel.filter_by_email(data['email'], session)
        if user and user.compare_hash(data['password']):
            user_session = SessionObject(user.id)
            session.add(user_session)
            session.commit()
            return f'You are LOGGED IN as {user.email}', 200, {"Set-Cookie": f'token="{user_session.token}"'}
        return 'Could not verify your login!', 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}



class Logout(Resource):
    """
    Logout resource.

    Remove the username from the session.
    """

    def get(self):
        token = request.cookies.get('token')
        session.query(SessionObject).filter(SessionObject.token == token).delete()
        session.commit()
        return {'message': 'Dropped!'}, 200  # OK


class Register(Resource):
    """
    Register resource.

    Parsing requested data, checks if username or email doesn't exit in DB, then create user in DB. 200 OK
    Otherwise, return 500 or 400 error.
    """

    @api.expect(user_post)
    def post(self):
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return 'No input data provided', 400  # Bad Request
        # Validate and deserialize input
        try:
            data = UserSchema().load(json_data)
        except ValidationError as err:
            return {'error': str(err)}, 422  # Unprocessable Entity
        # Check if a new user is not exist in data base
        if UserModel.filter_by_username(data['username'], session):
            return {'message': f'User with username: {data["username"]} is ALREADY EXISTS.'}, 200  # OK
        elif UserModel.filter_by_email(data['email'], session):
            return {'message': f'User with email: {data["email"]} is ALREADY EXISTS.'}, 200  # OK
        else:
            # create a new user
            try:
                session.add(UserModel(data))
                session.commit()
                return {'message': f"USER {data['username']} ADDED"}, 200  # OK
            except SQLAlchemyError as err:
                return {'error': str(err)}, 500  # Internal Server Error


class User(Resource):
    def get(self):
        """Get user's data."""
        try:
            user_data = get_user_by_token()
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500
        return {'user': UserSchema().dump(user_data)}, 200

    @api.expect(user_put)
    def put(self):
        """Update user's data."""
        args = request.get_json()
        try:
            current_user = get_user_by_token()
            for arg_key in args.keys():
                if arg_key != 'password':
                    current_user.__setattr__(arg_key, args[arg_key])
            session.add(current_user)
            session.commit()
            return {'message': f'User {current_user.username} UPDATED'}, 200
        except SQLAlchemyError as err:
            return {'error': err}, 500

    def delete(self):
        """Remove user with all his data."""
        token = request.cookies.get('token')
        try:
            current_user = get_user_by_token()
            session.query(SessionObject).filter(SessionObject.token == token).delete()
            session.delete(current_user)
            session.commit()
            return {'message': f'User {current_user.username} DELETED'}, 200
        except SQLAlchemyError as err:
            session.rollback()
            return {'error': str(err)}, 500


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
        try:
            current_user = get_user_by_token()
            passwords = session.query(PasswordModel).filter(PasswordModel.user_id == current_user.id).all()
            passwords_serialized = []
            for password in passwords:
                passwords_serialized.append(password.serialize)
            return {'passwords': passwords_serialized}, 200  # OK
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error

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
            return {'error': str(err)}, 422  # Unprocessable Entity

        current_user = get_user_by_token()

        # create a new password
        try:
            session.add(PasswordModel(current_user.id, data))
            session.commit()
            return {'message': 'PASSWORD ADDED'}, 200  # OK
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error


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
            return {'error': str(err)}, 422  # Unprocessable Entity

        try:
            user = get_user_by_token()
            filtered_passwords = PasswordModel.search_pass_by_description(user.id, data.get('condition'), session)
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500

        passwords_by_comment_title = []
        for password in filtered_passwords:
            passwords_by_comment_title.append(password.serialize)
        if passwords_by_comment_title:
            return {'passwords': passwords_by_comment_title}, 200
        else:
            return {'message': 'No matches found'}, 404


class UserPasswordsSearchUrl(Resource):
    @api.expect(search_password_url)
    def post(self):
        """Get all user passwords for the particular site."""
        json_data = request.get_json()

        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400
        # Input data validation by Marshmallow schema
        try:
            data = SearchPasswordUrlSchema().load(json_data)
        except ValidationError as err:
            return {'error': str(err)}, 422

        try:
            user = get_user_by_token()
            filtered_passwords = PasswordModel.search_pass_by_url(user.id, data.get('url'), session)
        except SQLAlchemyError as err:
            return {'message': str(err)}, 500

        passwords_by_url = []
        for password in filtered_passwords:
            passwords_by_url.append(password.serialize)
        if passwords_by_url:
            return {'passwords': passwords_by_url}, 200
        else:
            return {'message': 'No matches found'}, 404


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
        try:
            current_user = get_user_by_token()
            password = PasswordModel.find_pass(current_user.id, pass_id, session)
            if not password:
                return {'message': 'Password Not Found'}, 404  # Not Found
            return {'password': password.serialize}, 200  # OK
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error

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
            return {'error': str(err)}, 422  # Unprocessable Entity
        try:
            if not PasswordModel.is_password_exists(pass_id):
                return {'message': 'Password Not Found'}, 404
            password = PasswordModel.filter_pass_by_id(pass_id, session)
            previous_pass = password.title

            for arg_key in data.keys():
                if arg_key != 'password':
                    password.__setattr__(arg_key, data[arg_key])
                else:
                    password.crypt_password(data[arg_key])
            session.add(password)
            session.commit()
            return {'message': f'Data for {previous_pass} has been updated successfully'}, 200
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500

    def delete(self, pass_id):
        """
        Delete specific password.

        Delete password from current logged in user by pass_id.
        :param pass_id: id of specific user's password
        :return: 200 OK or 404 Password Not Found or 500 SQLAlchemyError
        """
        try:

            current_user = get_user_by_token()
            password = PasswordModel.find_pass(current_user.id, pass_id, session)
            if password:
                session.query(PasswordModel) \
                    .filter(PasswordModel.user_id == current_user.id) \
                    .filter(PasswordModel.pass_id == pass_id) \
                    .delete()
                session.commit()
                return {'message': f'Password ID {pass_id} DELETED'}, 200  # OK
            else:
                return {'message': 'Password Not Found'}, 404  # Not Found
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error


class AdminUsers(Resource):
    def get(self):
        """Get all users by list."""
        try:
            users = session.query(UserModel).all()
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
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
            return {'error': str(err)}, 422  # Unprocessable Entity
        try:
            for user_id in users_ids:
                user = UserModel.filter_by_id(user_id, session)
                if bool(user):
                    passwords = session.query(PasswordModel).filter(PasswordModel.user_id == user_id).all()
                    for password in passwords:
                        session.delete(password)
                    session.delete(user)
            session.commit()
            return {'message': 'Users has been deleted successfully'}, 200
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500


class AdminUsersNumber(Resource):
    def get(self, user_id):
        """Get user by user_id."""
        try:
            user_data = UserModel.filter_by_id(user_id, session)
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        if user_data:
            return {'user': UserSchema().dump(user_data)}, 200  # OK
        else:
            return {'message': f'User ID {user_id} - Not Found'}, 404  # Not Found

    def delete(self, user_id):
        """Delete user by user_id."""
        try:
            if UserModel.filter_by_id(user_id, session):
                session.query(SessionObject).filter(SessionObject.user_id == user_id).delete()
                session.query(PasswordModel).filter(PasswordModel.user_id == user_id).delete()
                session.query(UserModel).filter(UserModel.id == user_id).delete()
                session.commit()
                return {'message': f'User ID:{user_id} has been DELETED.'}, 200  # OK
            else:
                return {'message': f'User ID {user_id} - Not Found'}, 404  # Not Found
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error


class AdminUsersSearch(Resource):
    def get(self, username):
        """Get user by user name"""
        try:
            user_data = UserModel.filter_by_username(username, session)
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        if user_data:
            return {'user': UserSchema().dump(user_data)}, 200  # OK
        else:
            return {'message': 'User not found'}, 404  # Not Found


class AdminUsersSearchList(Resource):
    """
    Search user by any data - username, email, first_name, last_name or phone
    """

    @api.expect(admin_users_search)
    def post(self):
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request
        # Validate and deserialize input
        try:
            user_data = (AdminUsersSearchData().load(json_data))['user_data']
        except ValidationError as err:
            return {'error': str(err)}, 422  # Unprocessable Entity
        # Search users
        try:
            users = session.query(UserModel).filter(
                or_(UserModel.username.like(f'%{user_data}%'), UserModel.email.like(f'%{user_data}%'),
                    UserModel.first_name.like(f'%{user_data}%'), UserModel.last_name.like(f'%{user_data}%'),
                    UserModel.phone.like(f'%{user_data}%')
                    )).all()
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        if users:
            return {'users': UserSchema(many=True).dump(users)}, 200  # OK
        else:
            return {'message': 'User not found'}, 404  # Not Found
