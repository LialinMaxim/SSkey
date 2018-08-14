import datetime

from abc import ABCMeta, abstractmethod
from flask import make_response, request, session as sess
from flask_restplus import Resource, reqparse
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from . import app, api
from .base import Session
from .models import User, Password
from .shemas import UserSchema
from .swagger_models import user_model, user_put_model, user_login, password_put_model

session = Session()
headers = {'Access-Control-Allow-Origin': '*'}


@app.before_request
def require_login():
    """
    Require login function will be run before each request

    The function will be called without any arguments. This function checks whether requested route is allowed to
    unregistered user or not in allowed routes. Also, checks if session isn't empty. Otherwise, it will return 403 error

    """
    allowed_routes = ["login", "register", "home", "doc", "restplus_doc.static", "specs"]
    if request.endpoint not in allowed_routes and "email" not in sess:
        return make_response("You are not allowed to use this resource without logging in!", 403)


@api.representation('/json')
class Home(Resource):
    def get(self):
        return 'Representation Home Page', 200, headers


@api.representation('/json')
class Smoke(Resource):
    def get(self):
        return 'OK', 200, headers


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


@api.representation('/json')
class UserListResource(Resource):
    def get(self):
        try:
            users = session.query(User).all()
        except SQLAlchemyError:
            return SQLAlchemyError, 500  # Internal Server Error
        return UserSchema(many=True).dump(users), 200  # OK


@api.representation('/json')
class UserResource(EntityResource):
    def get(self, user_id):
        try:
            user_data = session.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError:
            return SQLAlchemyError, 500  # Internal Server Error
        if user_data:
            return UserSchema().dump(user_data), 200  # OK
        else:
            return 'User not found', 404  # Not Found


    @api.expect(user_put_model)
    @api.representation('/json')
    def put(self, user_id):
        parser = reqparse.RequestParser()
        for arg in ['email', 'username', 'first_name', 'last_name', 'phone']:
            parser.add_argument(arg, type=str, help='')
        args = parser.parse_args()
        try:
            if not User.is_user_exists(user_id):
                return 'User not found', 404  # Not Found
            user = session.query(User).filter(User.id == user_id).first()
            for arg_key in args.keys():
                if arg_key != 'password':
                    user.__setattr__(arg_key, args[arg_key])
            session.add(user)
            session.commit()
            msg = f'User {user.username} with id {user_id} has been successfully updated.'
            return msg, 200  # OK
        except SQLAlchemyError as err:
            return err, 500  # Internal Server Error

    def delete(self, user_id):
        try:
            if session.query(User).filter(User.id == user_id).first():
                session.query(User).filter(User.id == user_id).delete()
                session.commit()
                msg = 'User ID:{0} has been DELETED.'.format(user_id)
                return msg, 200  # OK
            else:
                msg = 'User ID:{0} NOT EXISTS!'.format(user_id)
                return msg, 404  # Not Found
        except SQLAlchemyError as err:
            return err, 500  # Internal Server Error


@api.representation('/json')
class PasswordResource(EntityResource):
    def get(self, user_id, pass_id):
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return 'User not found', 404, headers
            passwords = session.query(Password).filter(Password.user_id == user_id).all()
            passwords_serialized = []
            for password in passwords:
                passwords_serialized.append(password.serialize)
        except SQLAlchemyError as err:
            return str(err), 500
        return passwords_serialized, 200

    @api.expect(password_put_model)
    @api.representation('/json')
    def put(self, user_id, pass_id):
        parser = reqparse.RequestParser()
        for arg in ['url', 'title', 'login', 'pass', 'comment']:
            parser.add_argument(arg, type=str, help='')
        args = parser.parse_args()
        try:
            if not User.is_user_exists(user_id):
                return 'User not found', 404
            if not Password.is_password_exists(pass_id):
                return 'Password not found', 404
            password = session.query(Password).filter(Password.pass_id == pass_id). first()

            for arg_key in args.keys():
                if arg_key != 'password':
                    password.__setattr__(arg_key, args[arg_key])
                else:
                    password.crypt_password(args[arg_key])
            session.add(password)
            session.commit()
            return f'Data of password with id{pass_id} has been updated successfully', 200
        except SQLAlchemyError as err:
            return str(err), 500



    def delete(self, user_id):
        pass


@api.representation('/json')
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
        return msg, status, headers


@api.representation('/json')
class Register(Resource):
    """
    Register resource.

    Parsing requested data, checks if username or email doesn't exit in DB, then create user in DB. 200 OK
    Otherwise, return 500 or 400 error
    """

    @api.expect(user_model)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='')
        parser.add_argument('username', type=str, help='')
        parser.add_argument('password', type=str, help='')
        parser.add_argument('first_name', type=str, help='')
        parser.add_argument('last_name', type=str, help='')
        parser.add_argument('phone', type=str, help='')
        args = parser.parse_args()
        # json_data = request.get_json()
        # if not json_data or not isinstance(json_data, dict):
        #     return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            # data = UserSchema().load(json_data)
            data = UserSchema().load(args)
        except ValidationError as err:
            return str(err), 422  # Unprocessable Entity

        # Check if a new user is not exist in data base
        if session.query(User).filter(User.username == data['username']).first():
            msg = "User with username: '{0}' is ALREADY EXISTS.".format(data['username'])
            return msg, 200  # OK
        elif session.query(User).filter(User.email == data['email']).first():
            msg = "User with email: '{0}' is ALREADY EXISTS".format(data['email'])
            return msg, 200  # OK
        else:
            # TODO optimization USER CLASS
            # user = User(data)
            user = User(data['username'], data['email'], data['password'],
                        data['first_name'], data['last_name'], data['phone'])

            # crate a new user
            try:
                session.add(user)
                session.commit()
                msg = "New user: '{0}' is SUCCESSFUL ADDED".format(user.username)
                return msg, 200  # OK
            except SQLAlchemyError:
                return SQLAlchemyError, 500  # Internal Server Error


@api.representation('/json')
class Login(Resource):
    """
    Login resource.

    Checks whether entered data is in DB. Create user session based on its id and then sets session lifetime.
    Otherwise, it will return 401 error
    """

    @api.expect(user_login)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='')
        parser.add_argument('password', type=str, help='')
        args = parser.parse_args()

        current_user = User.filter_by_email(args["email"], session)
        if current_user and current_user.compare_hash(args["password"]):
            sess["email"] = args["email"]
            sess.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=60)
            return "Logged in as {}".format(current_user.email)

        return "Could not verify your login!", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}


@api.representation('/json')
class Logout(Resource):
    """
    Logout resource

    Remove the username from the session
    """

    def get(self):
        sess.pop("email", None)
        return "Dropped!"
