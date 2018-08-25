from flask import g

from . import api, user_api, admin_api
from .base import Session
from .resources.general import Home, Smoke, Register, Login, Logout
from .resources.user import (UserResource, UserPasswordsResource, UserPasswordsSearchResource,
                             UserPasswordsSearchUrlResource, UserPasswordsNumberResource)
from .resources.admin import (AdminUsersListResource, AdminUsersResource, PasswordResource,
                              PasswordListResource, UserSearch)

api.add_resource(Home, '/home')  # GET
api.add_resource(Smoke, '/smoke')  # GET
api.add_resource(Login, '/login')  # POST
api.add_resource(Logout, '/logout')  # GET
api.add_resource(Register, '/register')  # POST

user_api.add_resource(UserResource, '/username')  # GET, PUT, DELETE
user_api.add_resource(UserPasswordsResource, '/username/passwords')  # GET, POST
user_api.add_resource(UserPasswordsSearchResource, '/username/passwords/search')  # POST
user_api.add_resource(UserPasswordsSearchUrlResource, '/username/passwords/url')  # POST
user_api.add_resource(UserPasswordsNumberResource, '/username/passwords/<int:pass_id>')  # GET, PUT, DELETE

admin_api.add_resource(AdminUsersListResource, '/admin/users')  # GET
admin_api.add_resource(AdminUsersResource, '/admin/users/<int:user_id>')  # GET, PUT, DELETE
admin_api.add_resource(PasswordListResource, '/users/<int:user_id>/passwords')  # POST, GET
admin_api.add_resource(PasswordResource, '/users/<int:user_id>/passwords/<int:pass_id>')  # GET, PUT, DELETE
admin_api.add_resource(UserSearch, '/users/<string:username>')  # GET


def get_session():
    session = getattr(g, Session, None)
    if session is None:
        session = g.Session()
    return session
