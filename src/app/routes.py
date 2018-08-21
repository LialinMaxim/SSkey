from flask import g

from . import api

from .resources import (Home, Smoke, UserResource, AdminUsersResource, PasswordResource,
                        AdminUsersListResource, PasswordListResource, Register, Login, Logout, UserSearch,
                        UserPasswordsResource, UserPasswordsNumberResource, UserPasswordsSearchResource)
from .admin.resources import AdminTest
from .base import Session



from .admin import routes

api.add_resource(Home, '/home')  # GET
api.add_resource(Smoke, '/smoke')  # GET
api.add_resource(Login, '/login')  # POST
api.add_resource(Logout, '/logout')  # GET
api.add_resource(Register, '/register')  # POST

api.add_resource(UserResource, '/<string:username>')  # GET, PUT, DELETE
api.add_resource(UserPasswordsResource, '/username/passwords')  # GET, POST
api.add_resource(UserPasswordsNumberResource, '/username/passwords/<int:pass_id>')  # GET, PUT, DELETE
api.add_resource(UserPasswordsSearchResource, '/username/passwords/search')  # POST

api.add_resource(AdminUsersListResource, '/admin/users')  # GET
api.add_resource(AdminUsersResource, '/admin/users/<int:user_id>')  # GET, PUT, DELETE
api.add_resource(PasswordListResource, '/users/<int:user_id>/passwords')  # POST, GET
api.add_resource(PasswordResource, '/users/<int:user_id>/passwords/<int:pass_id>')  # GET, PUT, DELETE
api.add_resource(UserSearch, '/users/<string:username>')  # GET


def get_session():
    session = getattr(g, Session, None)
    if session is None:
        session = g.Session()
    return session
