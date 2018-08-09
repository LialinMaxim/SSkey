from flask import g

from . import api, Session
from . import Home, Smoke, UserResource, PasswordResource, UserListResource, PasswordListResource, Login, Logout, \
    Register

api.add_resource(Home, '/', "/home")
api.add_resource(Smoke, '/smoke')
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(PasswordListResource, '/users/<int:user_id>/passwords')
api.add_resource(PasswordResource, '/users/<int:user_id>/passwords/<int:pass_id>')
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')


def get_session():
    session = getattr(g, Session, None)
    if session is None:
        session = g.Session()

    return session
