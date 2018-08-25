from flask import g

from . import api
from .resources import (Home, Smoke, UserResource, PasswordResource,
                        PasswordListResource, Register, Login, Logout, UserSearch,
                        UserPasswordsResource, UserPasswordsNumberResource, UserPasswordsSearchResource,
                        UserPasswordsSearchUrlResource)
from . import api, user_api, admin_api
from .base import Session
from .resources import AdminUsersResource, AdminUsersListResource, AdminTest
from .resources.general import Home, Smoke, Register, Login, Logout
from .resources.user import (UserResource, UserPasswordsResource, UserPasswordsSearchResource,
                             UserPasswordsSearchUrlResource, UserPasswordsNumberResource)
from .resources.admin import AdminUsersListResource, AdminUsersResource, UserSearch

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
admin_api.add_resource(UserSearch, '/users/<string:username>')  # GET

api.add_resource(AdminTest, '/admin/test')  # GET
api.add_resource(AdminUsersListResource, '/admin/users')  # GET
api.add_resource(AdminUsersResource, '/admin/users/<int:user_id>')  # GET, PUT, DELETE


def get_session():
    session = getattr(g, Session, None)
    if session is None:
        session = g.Session()
    return session
