import json

from src.app import app

from .requests.login_requests import client, LoginRequests, resource
from .requests.admin_requests import AdminRequests
from .requests.basic_requests import BasicRequests


class TestAdminRoutes:
    """ Class contain tests for user routes CRUD functional """

    def test_register(self, client):
        """Make sure register works."""
        rv = BasicRequests.register(client, app.config["EMAIL"], app.config["USERNAME"], app.config["PASSWORD"],
                                    app.config["FIRST_NAME"], app.config["LAST_NAME"], app.config["PHONE"])
        assert b"USER testuser ADDED" in rv.data

    def test_admin_get_user_by_username(self, client, resource):
        rv = AdminRequests.get_user_by_username(client, app.config["USERNAME"])
        assert bytes(app.config["EMAIL"], encoding='utf-8') in rv.data
        assert bytes(app.config["FIRST_NAME"], encoding='utf-8') in rv.data

    def test_admin_delete_user(self, client, resource):
        """Try to delete user data for existant user"""

        rv = AdminRequests.get_user_by_username(client, app.config["USERNAME"])

        user = json.loads(str(rv.data, encoding='utf-8'))
        user_id = user['id']
        rv = AdminRequests.delete_user(client, str(user['id']))

        assert bytes(f'User ID:{user_id} has been DELETED.', encoding='utf-8') in rv.data
