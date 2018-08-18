import pytest

from src.app import app
from src.app.base import Base, engine
from src.app import config


@pytest.fixture  # (scope='class')
def client():
    """Create and return client to make requests"""
    # app.config["TESTING"] = True
    app.config.from_object(config['testing'])
    client = app.test_client()

    Base.metadata.create_all(engine)

    yield client


class LoginRequests:
    """ Contain methods to send requests on login logout routes"""

    @staticmethod
    def logout(client):
        return client.get("/logout", follow_redirects=True)

    @staticmethod
    def login(client, email, password):
        return client.post("/login", data=dict(
            email=email,
            password=password
        ), follow_redirects=True)


@pytest.yield_fixture
def resource(client):
    """ Set up and Tear Down in fixture - do login make some tests and logout after"""
    print("setup")
    LoginRequests.login(client, app.config["EMAIL"], app.config["PASSWORD"])

    yield
    print("teardown")
    LoginRequests.logout(client)
