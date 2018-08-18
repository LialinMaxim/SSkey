import json

from src.app import app

from src.tests.login_requests import client, LoginRequests, resource
from src.tests.user_requests import UserRequests


class TestUsersRoutes:
    """ Class contain tests for user routes CRUD functional """

    def test_register(self, client):
        """Make sure register works."""
        rv = UserRequests.register(client, app.config["EMAIL"], app.config["USERNAME"], app.config["PASSWORD"],
                                   app.config["FIRST_NAME"],
                                   app.config["LAST_NAME"], app.config["PHONE"])
        assert b"New user: 'testuser' is SUCCESSFUL ADDED" in rv.data

    def test_get_user_by_username(self, client, resource):
        rv = UserRequests.get_user_by_username(client, app.config["USERNAME"])
        assert bytes(app.config["EMAIL"], encoding='utf-8') in rv.data
        assert bytes(app.config["FIRST_NAME"], encoding='utf-8') in rv.data

    def test_put_user(self, client, resource):
        """Try to update user data for existant user"""

        rv = UserRequests.get_user_by_username(client, app.config["USERNAME"])
        user = json.loads(str(rv.data, encoding='utf-8'))
        username = user['username']
        user_id = user['id']
        rv = UserRequests.put_user(client, user['email'], username, 'Ali', 'Alhazred', '666-666-666', user_id)
        assert bytes(f'User {username} with id {user_id} has been successfully updated.', encoding='utf-8') in rv.data

    def test_delete_user(self, client, resource):
        """Try to delete user data for existant user"""

        rv = UserRequests.get_user_by_username(client, app.config["USERNAME"])

        user = json.loads(str(rv.data, encoding='utf-8'))
        user_id = user['id']
        rv = UserRequests.delete_user(client, str(user['id']))

        assert bytes(f'User ID:{user_id} has been DELETED.', encoding='utf-8') in rv.data
