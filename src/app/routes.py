from . import api
from . import Smoke, UserResource, PasswordResource, UserListResource, PasswordListResource  # Home,

# api.add_resource(Home, '/', "/home")
api.add_resource(Smoke, '/smoke')
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(PasswordListResource, '/users/<int:user_id>/passwords')
api.add_resource(PasswordResource, '/users/<int:user_id>/passwords/<int:pass_id>')
