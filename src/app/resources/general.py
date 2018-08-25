from flask import make_response, request
from flask_restplus import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from .. import app, api
from ..base import Session
from ..models import User, SessionObject
from ..marshmallow_schemes import UserSchema
from ..swagger_models import user_post, user_login

session = Session()


@app.before_request
def require_login():
    """
    Require login function will be run before each request.
    The function will be called without any arguments. This function checks whether requested route is allowed to
    unregistered user or not in allowed routes. Also, checks if session isn't empty. Otherwise, it will return 403 error
    """
    if request.endpoint != 'login':
        allowed_routes = ['login', 'register', 'home', 'doc', 'restplus_doc.static', 'specs']
        token_from_cookie = request.cookies.get('token')
        user_session = session.query(SessionObject).filter(SessionObject.user_id == token_from_cookie).first()
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
            session.query(SessionObject).filter(SessionObject.user_id == token).delete()
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


@api.representation('/json')
class Home(Resource):
    """Simple test that works without authorization."""
    def get(self):
        return 'This is a Home Page', 200  # OK


@api.representation('/json')
class Smoke(Resource):
    """Simple test that requires authorization."""
    def get(self):
        return 'OK', 200  # OK


@api.representation('/json')
class Login(Resource):
    """
    Login resource.

    Checks whether entered data is in DB. Create user session based on its id and then sets session lifetime.
    Otherwise, it will return 401 error.
    """

    @api.expect(user_login)
    def post(self):
        data = request.get_json()
        user = User.filter_by_email(data['email'], session)
        if user and user.compare_hash(data['password']):
            user_session = SessionObject(user.id)
            session.add(user_session)
            session.commit()
            return f'You are LOGGED IN as {user.email}', 200, {"Set-Cookie": f'token="{user_session.user_id}"'}
        return 'Could not verify your login!', 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}


@api.representation('/json')
class Logout(Resource):
    """
    Logout resource.

    Remove the username from the session.
    """

    def get(self):
        token = request.cookies.get('token')
        session.query(SessionObject).filter(SessionObject.user_id == token).delete()
        session.commit()
        return 'Dropped!', 200  # OK


@api.representation('/json')
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
            return str(err), 422  # Unprocessable Entity
        # Check if a new user is not exist in data base
        if User.filter_by_username(data['username'], session):
            return f'User with username: {data["username"]} is ALREADY EXISTS.', 200  # OK
        elif User.filter_by_email(data['email'], session):
            return f'User with email: {data["email"]} is ALREADY EXISTS.', 200  # OK
        else:
            # create a new user
            try:
                session.add(User(data))
                session.commit()
                return f"USER {data['username']} ADDED", 200  # OK
            except SQLAlchemyError as err:
                return str(err), 500  # Internal Server Error
