import os
import tempfile
import json
import pytest

from ..app.models import Password
from src.app import app
from src.app import config
from src.app.base import Base, engine


@pytest.fixture  # (scope='class')
def client():
    # app.config["TESTING"] = True
    app.config.from_object(config['testing'])
    client = app.test_client()

    Base.metadata.create_all(engine)

    yield client


def test_password_encode_decode():
    password = Password('vasya', 'vasya777', 1, "", "", "")
    assert password.password != 'vasya777'
    assert password.decrypt_password() == 'vasya777'


def register(client, email, username, password, first_name, last_name, phone):
    return client.post("/register", data=dict(
        email=email,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone=phone
    ), follow_redirects=True)


def delete_user(client, user_id):
    return client.delete("/users/" + user_id)


def put_user(client, email, username, first_name, last_name, phone, user_id):
    return client.put("/users/" + str(user_id), data=dict(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        phone=phone
    ), follow_redirects=True)


def get_user_by_username(client, username):
    return client.get("/users/" + username,
                      follow_redirects=True)


def smoke(client):
    return client.get("/smoke", follow_redirects=True)


def logout(client):
    return client.get("/logout", follow_redirects=True)


def login(client, email, password):
    return client.post("/login", data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def login_logout_dec(test_func):
    """
    Decorator to login as app.config["USERNAME"] make test and logout after test finish
    :param test_func:
    :return:
    """

    def wrapper(client):
        # before test
        login(client, app.config["EMAIL"], app.config["PASSWORD"])
        rv = get_user_by_username(client, app.config["USERNAME"])

        test_func(client, rv)

        # after test
        logout(client)

    return wrapper


def test_home_page(client):
    rv = client.get("/home")
    assert b"Home Page" in rv.data


def test_smoke_page(client):
    rv = smoke(client)
    assert b"You are not allowed to use this resource without logging in!" in rv.data


def test_register(client):
    """Make sure register works."""
    rv = register(client, app.config["EMAIL"], app.config["USERNAME"], app.config["PASSWORD"], app.config["FIRST_NAME"],
                  app.config["LAST_NAME"], app.config["PHONE"])
    assert b"New user: 'testuser' is SUCCESSFUL ADDED" in rv.data


@pytest.yield_fixture
def resource(client):
    print("setup")
    login(client, app.config["EMAIL"], app.config["PASSWORD"])

    yield
    print("teardown")
    logout(client)


class TestUsersRoutesWithLogin:

    # def setup(self):
    #     login(client, app.config["EMAIL"], app.config["PASSWORD"])
    #     logout(client)

    #
    # def teardown(self):

    def test_get_user_by_username(self, client, resource):
        rv = get_user_by_username(client, app.config["USERNAME"])
        assert bytes(app.config["EMAIL"], encoding='utf-8') in rv.data
        assert bytes(app.config["FIRST_NAME"], encoding='utf-8') in rv.data

    def test_login(self, client):
        """Make sure login and logout works."""

        rv = login(client, app.config["EMAIL"], app.config["PASSWORD"])

        assert b"Logged in as testuser@gmail.com" in rv.data

        rv = smoke(client)
        assert b"OK" in rv.data

        rv = logout(client)
        assert b"Dropped" in rv.data

        rv = smoke(client)
        assert b"You are not allowed to use this resource without logging in!" in rv.data

        rv = login(client, app.config["EMAIL"] + "x", app.config["PASSWORD"])
        assert b"Could not verify your login!" in rv.data

        rv = login(client, app.config["EMAIL"], app.config["PASSWORD"] + "x")
        assert b"Could not verify your login!" in rv.data

    def test_put_user(self, client, resource):
        """Try to update user data for existant user"""

        rv = get_user_by_username(client, app.config["USERNAME"])
        user = json.loads(str(rv.data, encoding='utf-8'))
        username = user['username']
        user_id = user['id']
        rv = put_user(client, user['email'], username, 'Ali', 'Alhazred', '666-666-666', user_id)
        assert bytes(f'User {username} with id {user_id} has been successfully updated.', encoding='utf-8') in rv.data

    def test_delete_user(self, client, resource):
        """Try to delete user data for existant user"""

        rv = get_user_by_username(client, app.config["USERNAME"])

        user = json.loads(str(rv.data, encoding='utf-8'))
        user_id = user['id']
        rv = delete_user(client, str(user['id']))

        assert bytes(f'User ID:{user_id} has been DELETED.', encoding='utf-8') in rv.data
