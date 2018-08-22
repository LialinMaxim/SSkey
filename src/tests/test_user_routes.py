from src.app import app
from .requests.login_requests import client, resource
from .requests.user_requests import UserRequests
from .requests.basic_requests import BasicRequests


class TestUserRoutes:

    def test_register(self, client):
        """Make sure register works."""
        rv = BasicRequests.register(client, app.config["EMAIL"], app.config["USERNAME"], app.config["PASSWORD"],
                                    app.config["FIRST_NAME"], app.config["LAST_NAME"], app.config["PHONE"])
        assert bytes(f'USER {app.config["USERNAME"]} ADDED', encoding='utf-8') in rv.data

    def test_get_username(self, client, resource):
        """Test of incoming <username>'s data"""
        rv = UserRequests.get_username(client)
        assert bytes(app.config['EMAIL'], encoding='utf-8') in rv.data
        assert bytes(app.config['USERNAME'], encoding='utf-8') in rv.data
        assert bytes(app.config['FIRST_NAME'], encoding='utf-8') in rv.data
        assert bytes(app.config['LAST_NAME'], encoding='utf-8') in rv.data
        assert bytes(app.config['PHONE'], encoding='utf-8') in rv.data

    def test_put_username(self, client, resource):
        """Test of updating <username>'s data"""
        rv = UserRequests.put_username(client, app.config['EMAIL'], app.config['USERNAME'], 'Bill', 'Gates', '0123456789')
        assert bytes(f'User {app.config["USERNAME"]} UPDATED', encoding='utf-8') in rv.data

    def test_delete_username(self, client, resource):
        """Test of deleting <username> with data"""
        rv = UserRequests.delete_username(client)
        assert bytes(f'User {app.config["USERNAME"]} DELETED', encoding='utf-8') in rv.data
