import datetime

from flask import make_response, request, session as sess
from flask_restplus import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from .. import app, api
from ..base import Session
from ..models import User, Password
from ..marshmallow_schemes import UserSchema, PasswordSchema, SearchSchema, SearchPasswordUrlSchema
from ..swagger_models import user_post, password_api_model, user_login, user_put, search_password, search_password_url

session = Session()


@app.before_request
def require_login():
    """
    Require login function will be run before each request.

    The function will be called without any arguments. This function checks whether requested route is allowed to
    unregistered user or not in allowed routes. Also, checks if session isn't empty. Otherwise, it will return 403 error
    """
    allowed_routes = ['login', 'register', 'home', 'doc', 'restplus_doc.static', 'specs']
    if request.endpoint not in allowed_routes and 'email' not in sess:
        return make_response('You are not allowed to use this resource without logging in!', 403)


@api.representation('/json')
class Home(Resource):
    def get(self):
        """Simple test that works without authorization."""
        return 'This is a Home Page', 200  # OK


@api.representation('/json')
class Smoke(Resource):
    def get(self):
        """Simple test that requires authorization."""
        return 'OK', 200  # OK


@api.representation('/json')
class Login(Resource):
    @api.expect(user_login)
    def post(self):
        """
        Login resource.

        Checks whether entered data is in DB. Create user session based on its id and then sets session lifetime.
        Otherwise, it will return 401 error.
        """
        data = request.get_json()
        user = User.filter_by_email(data['email'], session)
        if user and user.compare_hash(data['password']):
            sess['email'] = data['email']
            sess.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=60)
            return f'You are LOGGED IN as {user.email}'
        return 'Could not verify your login!', 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}


@api.representation('/json')
class Logout(Resource):
    def get(self):
        """
        Logout resource.

        Remove the username from the session.
        """
        sess.pop('email', None)
        return 'Dropped!', 200  # OK


@api.representation('/json')
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
            return 'No input data provided', 400  # Bad Request
        print(json_data)

        # Validate and deserialize input
        try:
            data = UserSchema().load(json_data)
        except ValidationError as err:
            return str(err), 422  # Unprocessable Entity
        print(data)
        # TODO One function for all
        # Check if a new user is not exist in data base
        if session.query(User).filter(User.username == data['username']).first():
            return f"User with username: {data['username']} is ALREADY EXISTS.", 200  # OK
        elif session.query(User).filter(User.email == data['email']).first():
            return f"User with email: {data['email']} is ALREADY EXISTS.", 200  # OK
        else:
            # crate a new user
            try:
                session.add(User(data))
                session.commit()
                return f"USER {data['username']} ADDED", 200  # OK
            except SQLAlchemyError as err:
                return str(err), 500  # Internal Server Error
