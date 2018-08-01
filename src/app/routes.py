from . import api
from . import Home, Smoke, UserResource

api.add_resource(Home, '/', "/home")
api.add_resource(Smoke, '/smoke')
api.add_resource(UserResource, '/users')
