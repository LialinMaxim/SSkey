# from flask import url_for, flash, redirect
# from app.forms import RegistrationForm, LoginForm
# from flask_login import login_user, logout_user, login_required
from flask_restful import Resource, reqparse
from abc import ABCMeta, abstractmethod
from app.models import User
from app import app, api

from base import Session

session = Session()


class HelloWorld(Resource):

    def get(self):
        return {'hello': 'world'}


class Smoke(Resource):
    def get(self):
        return {'message': 'OK'}, 200, {'Access-Control-Allow-Origin': '*'}


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


class UserResource(EntityResource):
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Rate to charge for this resource')
        parser.add_argument('username', type=str, help='Rate to charge for this resource')
        parser.add_argument('userpass', type=str, help='Rate to charge for this resource')
        parser.add_argument('first_name', type=str, help='Rate to charge for this resource')
        parser.add_argument('last_name', type=str, help='Rate to charge for this resource')
        parser.add_argument('phone', type=str, help='Rate to charge for this resource')
        args = parser.parse_args()

        if not User.validate_user_create_data(args):
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
        parser.add_argument('username', type=str, help='Rate to charge for this resource')
        parser.add_argument('email', type=str, help='Rate to charge for this resource')

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
        # users = list(map(lambda x: str(x), users))
        # users = jsonify(json_list=[user.serialize for user in users])
        users_resp = []
        for user in users:
            users_resp.append(user.serialize)
        return {'users': users_resp}, status, {'Access-Control-Allow-Origin': '*'}

    def put(self):
        pass

    def delete(self):
        pass


api.add_resource(UserResource, '/user')
api.add_resource(Smoke, '/smoke')
api.add_resource(HelloWorld, '/hello')


# @app.route("/")
# @app.route("/home")
# def hello():
#     return "<h1>Home Page</h1>"
#
#
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
#         user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()
#         flash(f"Your account has been created! You are now able to log in", "success")
#         return redirect(url_for("login"))
#
#
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user, remember=form.remember.data)
#             # next_page = request.args.get("next")
#             # return redirect(next_page) if next_page else redirect(url_for("home"))
#             return redirect(url_for("home"))
#         else:
#             flash("Login Unsuccessful. Please, check email and password", "")
#
#
# @app.route("/logout")
# def logout():
#     logout_user()
#     return redirect(url_for("home"))
#
#
# @app.route("/account")
# @login_required
# def account():
#     flash("Here will be your account")
