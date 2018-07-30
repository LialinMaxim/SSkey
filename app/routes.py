from abc import ABCMeta, abstractmethod

from flask import g, jsonify, request, abort
from flask_restful import Resource, reqparse

from app import app, api, basic_auth
from app.models import User
from base import Session

session = Session()


# Token endpoint
@app.route('/token', methods=['GET'])  # test route
@basic_auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('utf-8')})

# curl -u test:test -i -X GET http://127.0.0.1:5000/token
# curl -u test:test -i -X GET http://127.0.0.1:5000/user


@basic_auth.verify_password
def verify_password(username_or_token, password):
    # First try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        print('Cannot verify the token')
        # Try to authenticate with username/password
        print('Looking for a user...')
        user = session.query(User).filter(User.username == username_or_token).first()
        print(user)
        if not user or not user.verify_password(password):
            print("User wasn't found and/or password wasn't verified")
            return False
    # Creates user after verification
    print('User was found and password was verified')
    g.user = user
    return True


# User registration
# curl -i -X POST -H "Content-Type: application/json" -d '{"username":"artur","password":"password","email":"artur@email","first_name":"Artur","last_name":"Manukian", "phone":"0123456789"}' http://127.0.0.1:5000/users
@app.route('/users', methods=['POST'])  # test rout
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    phone = request.json.get('phone')
    if username is None or password is None:
        abort(400)  # missing arguments
    if session.query(User).filter(User.username == username).first() is not None:
        abort(400)  # existing user
    user = User(username=username, email=email, first_name=first_name,
                last_name=last_name, phone=phone)
    user.hash_password(password)
    try:
        session.add(user)
        session.commit()
    except Exception as e:
        msg = str(e)
        status = 500
        return jsonify({'message': msg}, status, {'Access-Control-Allow-Origin': '*'})
    return jsonify({'username': user.username}), 201


# @basic_auth.verify_password
# def verify_password(username, password):
#     """Password verification
#
#     Flask-HTTPAuth invokes this callback function whenever it needs
#     to validate a username and password pair.
#
#     :param username: Received username
#     :param password: Received password
#     :return:
#     """
#     user = session.query(User).filter(User.username == username).first()
#     if not user or not user.verify_password(password):
#         return False
#     # Creates user after verification
#     g.user = user
#     return True


# @token_auth.verify_token
# def verify_token(token):
#     """Token verification
#
#     Verifies token based on username
#
#     :param token: token from /login POST method
#     :return: False or True if token exist
#     """
#     g.user = None
#
#     try:
#         data = token_serializer.loads(token)
#     except:
#         return False
#
#     if 'username' in data:
#         g.user = data['username']
#         return True
#
#     return False


class EntityResource(Resource):
    __metaclass__ = ABCMeta

    @abstractmethod
    def post(self):
        raise NotImplementedError

    @abstractmethod
    def get(self):
        raise NotImplementedError

    @abstractmethod
    def put(self):
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError


class Home(EntityResource):
    method_decorators = {'get': [basic_auth.login_required]}

    # curl -i -X GET http://127.0.0.1:5000/home
    # 'Unauthorized Access' without login and password
    def get(self):
        return {'message': 'Home Page'}, 200, {'Access-Control-Allow-Origin': '*'}


class Smoke(EntityResource):

    def get(self):
        return {'message': 'OK'}, 200, {'Access-Control-Allow-Origin': '*'}


class Login(EntityResource):
    # method_decorators = {'post': [basic_auth.verify_password]}

    def post(self):
        """Login POST method

        Creates token

        :return: token
        """
        # Authentication

        # May be replaced with decorator.
        # Finds user from DB query.
        # g.user = session.query(User).filter(User.username == basic_auth.username).first()
        # if not g.user:
        #     msg = 'Could not verify. Invalid user.'
        #     status = 401
        #     return {'message': msg}, status, {'WWW-Authenticate': 'Basic realm="Login required."'}

        # token = token_serializer.dumps({'username': g.user}).decode('utf-8')

        # return {'user': g.user, 'Authorization': token}

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


class UserResource(EntityResource):
    """Decorator gets and checks token, return response
    'Unauthorized Access' if token is invalid or does not exist.

    """
    # method_decorators = {'get': [basic_auth.login_required]}

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
        else:
            user = User(args['username'], args['email'], args['userpass'], args['first_name'],
                        args['last_name'], args['phone'])
            status = 200
            msg = "USER {0} REGISTRATION SUCCESSFUL".format(user.username)
            try:
                session.add(user)
                session.commit()
            except Exception as e:
                msg = str(e)
                status = 500
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='')
        parser.add_argument('email', type=str, help='')

        args = parser.parse_args()
        try:
            if args['username']:
                users = session.query(User).filter(User.username == args['username']).all()
            elif args['email']:
                users = session.query(User).filter(User.email == args['email']).all()
            else:
                users = session.query(User).all()
        except Exception as e:
            msg = str(e)
            status = 500
            return {'msg': msg}, status, {'Access-Control-Allow-Origin': '*'}
        status = 200
        users_resp = []
        for user in users:
            users_resp.append(user.serialize)
        return {'users': users_resp}, status, {'Access-Control-Allow-Origin': '*'}

    def put(self):
        pass

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='')
        args = parser.parse_args()
        if args['username']:
            try:
                session.query(User).filter(User.username == args['username']).delete()
                session.commit()
                status = 200
                msg = 'User {0} has been deleted successfully'.format(args['username'])
            except Exception as e:
                msg = str(e)
                status = 500
        else:
            msg = "USERNAME not given!"
            status = 400
        return {'message': msg}, status, {'Access-Control-Allow-Origin': '*'}


api.add_resource(Home, '/', "/home")
api.add_resource(Smoke, '/smoke')
api.add_resource(Login, '/login')
api.add_resource(UserResource, '/user')
