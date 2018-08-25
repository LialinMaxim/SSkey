from .. import admin_api
from .resources import AdminTest, AdminUsersResource, AdminUsersListResource

admin_api.add_resource(AdminTest, '/admin/test')  # GET
admin_api.add_resource(AdminUsersListResource, '/admin/users')  # GET
admin_api.add_resource(AdminUsersResource, '/admin/users/<int:user_id>')  # GET, PUT, DELETE
