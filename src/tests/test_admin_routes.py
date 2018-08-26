import json

from ..app import app
from .requests.login_requests import client, resource
from .requests.admin_requests import AdminRequests, login_logout_admin, create_admin
from .requests.basic_requests import BasicRequests


class TestAdminRoutes:
    """ Class contain tests for user routes CRUD functional """

    def test_register(self, client, create_admin):
        """Make sure register works."""
        rv = BasicRequests.register(client, app.config['EMAIL'], app.config['USERNAME'], app.config['PASSWORD'],
                                    app.config['FIRST_NAME'], app.config['LAST_NAME'], app.config['PHONE'])
        assert b"USER testuser ADDED" in rv.data

    def test_admin_get_user_by_username_200(self, client, login_logout_admin):
        """Test for get user by username. If user exists in db"""
        rv = AdminRequests.get_user_by_username(client, app.config['USERNAME'])
        assert bytes(app.config['EMAIL'], encoding='utf-8') in rv.data
        assert bytes(app.config['FIRST_NAME'], encoding='utf-8') in rv.data

    def test_admin_get_user_by_username_404(self, client, login_logout_admin):
        """Test for get user by username. If user not exists in db"""
        rv = AdminRequests.get_user_by_username(client, 'abrakadabra5768')
        assert bytes('User not found', encoding='utf-8') in rv.data

    def test_search_404(self, client, login_logout_admin):
        """Test for admin search. Case when it cant find any user"""
        rv = AdminRequests.search_users_by_any_field(client, 'abrakadabra987')
        assert bytes('User not found', encoding='utf-8') in rv.data

    def test_search_user_200(self, client, login_logout_admin):
        """Test for admin search. Case when it can find user"""
        rv = AdminRequests.search_users_by_any_field(client, app.config['PHONE'])
        assert bytes(app.config['EMAIL'], encoding='utf-8') in rv.data
        assert bytes(app.config['FIRST_NAME'], encoding='utf-8') in rv.data

    def test_batch_users_delete(self, client, login_logout_admin):
        """Test for batch delete users. Get list of users ids"""
        user_ids = []
        for user in app.config['USER_BATCH']:
            BasicRequests.register(client, *user)
        rv = AdminRequests.search_users_by_any_field(client, app.config['USER_BATCH'][0][5])
        data = json.loads(str(rv.data, encoding='utf-8'))
        for user, _ in enumerate(data):
            user_ids.append(data['users'][user]['id'])
        rv = AdminRequests.batch_users_delete(client, user_ids)

        assert bytes('Users has been deleted successfully', encoding='utf-8') in rv.data

    def test_admin_delete_user_404(self, client, login_logout_admin):
        """Try to delete user data for non existant user"""

        user_id = 190786663
        rv = AdminRequests.delete_user(client, str(user_id))

        assert bytes(f'User ID {user_id} - Not Found', encoding='utf-8') in rv.data

    def test_admin_delete_user_200(self, client, login_logout_admin):
        """Try to delete user data for existant user"""

        rv = AdminRequests.get_user_by_username(client, app.config['USERNAME'])

        user = json.loads(str(rv.data, encoding='utf-8'))
        user_id = user['id']
        rv = AdminRequests.delete_user(client, str(user['id']))

        assert bytes(f'User ID:{user_id} has been DELETED.', encoding='utf-8') in rv.data

    def test_admin_delete_admin_200(self, client, login_logout_admin):
        """Try to delete user data for existant user"""

        rv = AdminRequests.get_user_by_username(client, app.config['ADMIN_USERNAME'])

        data = json.loads(str(rv.data, encoding='utf-8'))
        user_id = data['user']['id']
        rv = AdminRequests.delete_user(client, str(user_id))

        assert bytes(f'User ID:{user_id} has been DELETED.', encoding='utf-8') in rv.data
