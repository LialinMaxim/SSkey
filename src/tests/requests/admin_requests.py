import pytest

from src.app import config
from src.app import app
from src.app.base import Session
from src.app.models import UserModel
from .login_requests import LoginRequests, client

session = Session()


@pytest.fixture
def create_admin(client):
    password = app.config["ADMIN_PASSWORD"]
    username = app.config['ADMIN_USERNAME']
    admin = UserModel(
        {'username': username, 'password': password, 'email': app.config['ADMIN_EMAIL'],
         'first_name': '', 'last_name': '', 'phone': ''})
    admin.is_admin = True
    session.add(admin)
    session.commit()


@pytest.yield_fixture
def login_logout_admin(client):
    LoginRequests.login(client, app.config["ADMIN_EMAIL"], app.config["ADMIN_PASSWORD"])
    yield
    LoginRequests.logout(client)


class AdminRequests:
    """ Contain methods to send requests on user routes"""

    @staticmethod
    def delete_user(client, user_id):
        return client.delete('admin/users/' + user_id)

    @staticmethod
    def put_user(client, email, username, first_name, last_name, phone, user_id):
        return client.put('admin/users/' + str(user_id), json=dict(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        ), follow_redirects=True)

    @staticmethod
    def get_user_by_username(client, username):
        return client.get('admin/users/' + username,
                          follow_redirects=True)

    @staticmethod
    def batch_users_delete(client, users_ids):
        return client.delete('admin/users', json=dict(
            users_ids=users_ids,
        ), follow_redirects=True)

    @staticmethod
    def search_users_by_any_field(client, user_data):
        return client.post('admin/users/search', json=dict(
            user_data=user_data,
        ), follow_redirects=True)
