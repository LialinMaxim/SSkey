from flask import g

from . import api, user_api, admin_api
from .base import Session

from .resources import Home, Smoke, Register, Login, Logout
from .resources import User, UserPasswords, UserPasswordsSearch, UserPasswordsNumber
from .resources import AdminUsers, AdminUsersNumber, AdminUsersSearch, AdminUsersSearchList

api.add_resource(Home, '/home')  # GET
api.add_resource(Smoke, '/smoke')  # GET
api.add_resource(Login, '/login')  # POST
api.add_resource(Logout, '/logout')  # GET
api.add_resource(Register, '/register')  # POST

user_api.add_resource(User, '/')  # GET, PUT, DELETE
user_api.add_resource(UserPasswords, '/passwords')  # GET, POST
user_api.add_resource(UserPasswordsSearch, '/passwords/search')  # POST
user_api.add_resource(UserPasswordsNumber, '/passwords/<int:pass_id>')  # GET, PUT, DELETE

admin_api.add_resource(AdminUsers, '/users')  # GET, #DELETE
admin_api.add_resource(AdminUsersNumber, '/users/<int:user_id>')  # GET, DELETE
admin_api.add_resource(AdminUsersSearch, '/users/<string:username>')  # GET
admin_api.add_resource(AdminUsersSearchList, '/users/search')  # POST


# def get_session():
#     session = getattr(g, Session, None)
#     if session is None:
#         session = g.Session()
#     return session
