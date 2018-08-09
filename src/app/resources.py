import datetime

from abc import ABCMeta, abstractmethod
from flask_restful import Resource, reqparse
from flask import request, make_response, session as sess
from sqlalchemy.exc import SQLAlchemyError

from . import app
from . import User
from . import Password
from . import Session

session = Session()


@app.before_request
def require_login():
    """
    Require login function will be run before each request

    The function will be called without any arguments. This function checks whether requested route is allowed to
    unregistered user or not in allowed routes. Also, checks if session isn't empty. Otherwise, it will return 403 error

    """
    allowed_routes = ["login", "/", "register", "home"]
    print(sess)
    if request.endpoint not in allowed_routes and "email" not in sess:
        return make_response("You are not allowed to use this resource without logging in!", 403)


class Home(Resource):
    def get(self):
        return {'message': 'Home Page'}, 200, {
            'Access-Control-Allow-Origin': '*'}


class Smoke(Resource):
    # @auth_required
    def get(self):
        return {'message': 'OK'}, 200, {'Access-Control-Allow-Origin': '*'}


class EntityListResource(Resource):
    """
    Abstract class of Entity list contain method POST and GET work with routs type /entities
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self):
        raise NotImplementedError

    @abstractmethod
    def post(self):
        raise NotImplementedError


class EntityResource(Resource):
    """
    Abstract class of Entity contain method  GET PUT delete work with routs type /entities/<int:entity_id>
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def put(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError


class UserListResource(Resource):

    def get(self):
        headers = {'Access-Control-Allow-Origin': '*'}
        try:
            users = session.query(User).all()
        except SQLAlchemyError as e:
            return {'msg': e}, 500, headers
        users_serialized = []
        for user in users:
            users_serialized.append(user.serialize)
        return {'users': users_serialized}, 200, headers


class UserResource(EntityResource):

    def get(self, user_id):
        headers = {'Access-Control-Allow-Origin': '*'}
        try:
            user = session.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            return {'msg': e}, 500, headers
        if user:
            return {'user': user.serialize}, 200, headers
        else:
            return {'msg': 'User not found'}, 404, headers

    def put(self, user_id):
        pass

    def delete(self, user_id):
        try:
            if session.query(User).filter(User.id == user_id).first():
                session.query(User).filter(User.id == user_id).delete()
                session.commit()
                status = 204
                msg = 'User with id = {0} has been deleted successfully'.format(user_id)
            else:
                msg = 'User with id = {0} not exists!'.format(user_id)
                status = 404
        except SQLAlchemyError as e:
            msg = e
            status = 500
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}


class PasswordResource(EntityResource):
    def get(self, user_id, pass_id):
        headers = {'Access-Control-Allow-Origin': '*'}
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {'msg': 'User not found'}, 404, headers
            passwords = session.query(Password).filter(Password.user_id == user_id).all()
            passwords_serialized = []
            for password in passwords:
                passwords_serialized.append(password.serialize)
        except SQLAlchemyError as e:
            return {'msg': e}, 500, headers
        return {'passwords': passwords_serialized}, 200, headers

    def put(self, user_id):
        pass

    def delete(self, user_id):
        pass


class PasswordListResource(EntityListResource):
    def get(self):
        pass

    def post(self):
        pass

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='')
        args = parser.parse_args()
        if args['username']:
            try:
                session.query(User).filter(
                    User.username == args['username']).delete()
                session.commit()
                status = 200
                msg = 'User {0} has been deleted successfully'.format(
                    args['username'])
            except Exception as e:
                msg = str(e)
                status = 500
        else:
            msg = "USERNAME not given!"
            status = 400
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}


class Register(Resource):
    """
    Register resource.

    Parsing requested data, checks if username or email doesn't exit in DB, then create user in DB. 200 OK
    Otherwise, return 500 or 400 error
    """

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='')
        parser.add_argument('username', type=str, help='')
        parser.add_argument('userpass', type=str, help='')
        parser.add_argument('first_name', type=str, help='')
        parser.add_argument('last_name', type=str, help='')
        parser.add_argument('phone', type=str, help='')
        args = parser.parse_args()

        if not User.validate_user(args):
            msg = "REQUIRED DATA NOT VALID OR BLANK"
            status = 400
        elif session.query(User).filter(User.username == args['username']).first():
            msg = "User with username = {0} already exists".format(args['username'])
            status = 200
        elif session.query(User).filter(User.email == args['email']).first():
            msg = "Useer with email = {0} already exists".format(args['email'])
            status = 200
        else:
            user = User(args['username'], args['email'], args['userpass'],
                        args['first_name'], args['last_name'], args['phone'])
            status = 200
            msg = "USER {0} REGISTRATION SUCCESSFUL".format(user.username)
            try:
                session.add(user)
                session.commit()
            except SQLAlchemyError as e:
                msg = e
                status = 500
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}


class Login(Resource):
    """
    Login resource.

    Checks whether entered data is in DB. Create user session based on its id and then sets session lifetime.
    Otherwise, it will return 401 error
    """

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='')
        parser.add_argument('password', type=str, help='')
        args = parser.parse_args()

        current_user = User.filter_by_email(args["email"])
        if current_user and current_user.compare_hash(args["password"]):
            sess["email"] = args["email"]
            sess.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=15)
            return make_response("Logged in as {}".format(current_user.email))

        return make_response("Could not verify your login!", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})


class Logout(Resource):
    """
    Logout resource

    Remove the username from the session
    """

    def get(self):
        sess.pop("email", None)
        return "Dropped!"
