import json

from src.app import app

from .requests.login_requests import client, resource
from .requests.admin_requests import AdminRequests
from .requests.basic_requests import BasicRequests


class TestAdminRoutes:
    """ Class contain tests for user routes CRUD functional """

    def test_register(self, client):
        """Make sure register works."""
        rv = BasicRequests.register(client, app.config["EMAIL"], app.config["USERNAME"], app.config["PASSWORD"],
                                    app.config["FIRST_NAME"], app.config["LAST_NAME"], app.config["PHONE"])
        assert b"USER testuser ADDED" in rv.data

    def test_admin_get_user_by_username_ok(self, client, resource):
        """Test for get user by username. If user exists in db"""
        rv = AdminRequests.get_user_by_username(client, app.config['USERNAME'])
        assert bytes(app.config['EMAIL'], encoding='utf-8') in rv.data
        assert bytes(app.config['FIRST_NAME'], encoding='utf-8') in rv.data

    def test_admin_get_user_by_username(self, client, resource):
        """Test for get user by username. If user not exists in db"""
        rv = AdminRequests.get_user_by_username(client, 'abrakadabra5768')
        assert bytes('User not found', encoding='utf-8') in rv.data

    def test_search_404(self, client, resource):
        """Test for admin search. Case when it cant find any user"""
        rv = AdminRequests.search_users_by_any_field(client, 'abrakadabra987')
        assert bytes('User not found', encoding='utf-8') in rv.data

    def test_search_user_200(self, client, resource):
        """Test for admin search. Case when it can find user"""
        rv = AdminRequests.search_users_by_any_field(client, app.config['PHONE'])
        assert bytes(app.config['EMAIL'], encoding='utf-8') in rv.data
        assert bytes(app.config['FIRST_NAME'], encoding='utf-8') in rv.data

    def test_batch_users_delete(self, client, resource):
        user_ids = []
        for user in app.config['USER_BATCH']:
            BasicRequests.register(client, *user)
        rv = AdminRequests.search_users_by_any_field(client, app.config['USER_BATCH'][0][5])
        data = json.loads(str(rv.data, encoding='utf-8'))
        for user, _ in enumerate(data):
            user_ids.append(data['users'][user]['id'])
        rv = AdminRequests.batch_users_delete(client, user_ids)

        assert bytes('Users has been deleted successfully', encoding='utf-8') in rv.data

    def test_admin_delete_user(self, client, resource):
        """Try to delete user data for existant user"""

        rv = AdminRequests.get_user_by_username(client, app.config["USERNAME"])

        data = json.loads(str(rv.data, encoding='utf-8'))
        user_id = data['user']['id']
        rv = AdminRequests.delete_user(client, str(user_id))

        assert bytes(f'User ID:{user_id} has been DELETED.', encoding='utf-8') in rv.data
