from src.app import app
from .login_requests import client
from .basic_requests import BasicRequests


class TestBasicRoutes:

    def test_smoke(self, client):
        rv = client.get('/smoke')

    def test_home_page(self, client):
        rv = client.get('/home')
        assert b"This is a Home Page" in rv.data

    def test_register(self, client):
        """Make sure register works."""
        rv = BasicRequests.register(client, app.config["EMAIL"], app.config["USERNAME"], app.config["PASSWORD"],
                                    app.config["FIRST_NAME"], app.config["LAST_NAME"], app.config["PHONE"])
        assert bytes(f'USER {app.config["USERNAME"]} ADDED', encoding='utf-8') in rv.data
