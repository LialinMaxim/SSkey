from .. import app, api
from .resources import AdminTest

# api.add_resource(AdminTest, '/home')  # GET
api.add_resource(AdminTest, '/admin/test')  # GET