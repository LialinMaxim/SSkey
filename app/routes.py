from app.resources import Home, Smoke, UserResource
from app import api

api.add_resource(Home, '/', "/home")
api.add_resource(Smoke, '/smoke')
api.add_resource(UserResource, '/users')
