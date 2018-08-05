from . import api
from . import Home, Smoke, UserResource, PasswordResource, UserListResource, PasswordListResource
from . import Home, Smoke, UserResource, Login, LogoutRefresh, TokenRefresh, Logout

api.add_resource(Home, '/', "/home")
api.add_resource(Smoke, '/smoke')
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(PasswordListResource, '/users/<int:user_id>/passwords')
api.add_resource(PasswordResource, '/users/<int:user_id>/passwords/<int:pass_id>')
api.add_resource(UserResource, '/users')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(LogoutRefresh, '/logout/refresh')
api.add_resource(TokenRefresh, '/token/refresh')
