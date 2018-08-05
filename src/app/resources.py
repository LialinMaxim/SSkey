from abc import ABCMeta, abstractmethod
from sqlalchemy.exc import SQLAlchemyError

from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

from . import Session
from . import User
from . import Password
from . import RevokedTokenModel

session = Session()


class Home(Resource):
    def get(self):
        return {'message': 'Home Page'}, 200, {
            'Access-Control-Allow-Origin': '*'}


class Smoke(Resource):
    @jwt_required
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
                access_token = create_access_token(identity=args["email"])
                refresh_token = create_refresh_token(identity=args["email"])
            except Exception as e:
                msg = str(e)
            except SQLAlchemyError as e:
                msg = e
                status = 500
        return {'message': msg, "access token": access_token, "refresh token": refresh_token}, status, {
            'Access-Control-Allow-Origin': '*'}


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


class Login(Resource):
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help="This field cannot be blank")
        parser.add_argument('password', type=str, help="This field cannot be blank")
        data = parser.parse_args()

        if session.query(User).filter(User.email == data["email"]).first():
            access_token = create_access_token(identity=data["email"])
            refresh_token = create_refresh_token(identity=data["email"])
            return {"message": "Logged in as {}".format(data["email"]), "access token": access_token,
                    "refresh_token": refresh_token}
        # if User.compare_hash(current_user, data["password"]):
        #     access_token = create_access_token(identity=data["email"])
        #     refresh_token = create_refresh_token(identity=data["email"])
        else:
            return "Wrong credentials"


class Logout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {"message": "Access token has been revoked"}
        except Exception as err:
            return {"message": "Something went wrong"}, 500, err


class LogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {"message": "Refresh token has been revoked"}
        except Exception as err:
            return {"message": "Something went wrong"}, 500, err


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_refresh_token(identity=current_user)
        return {"access token": access_token}
