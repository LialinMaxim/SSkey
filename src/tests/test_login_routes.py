import json

from src.app import app

from src.tests.login_requests import client, LoginRequests, resource
from src.tests.user_requests import UserRequests
from src.tests.basic_requests import BasicRequests


class TestLoginRoutes:
    """ Class contain tests for login routes """

    def test_register(self, client):
        """Make sure register works."""
        rv = UserRequests.register(client, app.config["EMAIL"], app.config["USERNAME"], app.config["PASSWORD"],
                                   app.config["FIRST_NAME"],
                                   app.config["LAST_NAME"], app.config["PHONE"])
        assert b"New user: 'testuser' is SUCCESSFUL ADDED" in rv.data

    def test_login(self, client):
        """Make sure login and logout works."""

        rv = LoginRequests.login(client, app.config["EMAIL"], app.config["PASSWORD"])

        assert b"Logged in as testuser@gmail.com" in rv.data

        rv = BasicRequests.smoke(client)
        assert b"OK" in rv.data

        rv = LoginRequests.logout(client)
        assert b"Dropped" in rv.data

        rv = BasicRequests.smoke(client)
        assert b"You are not allowed to use this resource without logging in!" in rv.data

        rv = LoginRequests.login(client, app.config["EMAIL"] + "x", app.config["PASSWORD"])
        assert b"Could not verify your login!" in rv.data

        rv = LoginRequests.login(client, app.config["EMAIL"], app.config["PASSWORD"] + "x")
        assert b"Could not verify your login!" in rv.data

    def test_delete_user(self, client, resource):
        """Try to delete user data for existant user"""

        rv = UserRequests.get_user_by_username(client, app.config["USERNAME"])

        user = json.loads(str(rv.data, encoding='utf-8'))
        user_id = user['id']
        rv = UserRequests.delete_user(client, str(user['id']))

        assert bytes(f'User ID:{user_id} has been DELETED.', encoding='utf-8') in rv.data
