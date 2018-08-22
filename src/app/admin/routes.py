from .. import api
from .resources import AdminUsersResource, AdminUsersListResource
from .resources import AdminTest

api.add_resource(AdminTest, '/admin/test')  # GET
api.add_resource(AdminUsersListResource, '/admin/users')  # GET
api.add_resource(AdminUsersResource, '/admin/users/<int:user_id>')  # GET, PUT, DELETE
