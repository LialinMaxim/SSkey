import os
import tempfile

from src.app import app
import pytest


@pytest.fixture
def client():
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config["TESTING"] = True
    client = app.test_client()

    # with app.app_context():
    #     app.init_db()

    yield client

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])


def test_smoke(client):
    rv = client.get("/smoke")
    assert b"Missing Authorization Header" in rv.data


def test_home_page(client):
    rv = client.get("/")
    assert b"Home Page" in rv.data


# def test_valid_login(client):
#     rv = client.post("/login", data=dict(email="vlad@gmail.com", password="vlad"))
#     assert rv.status_code == 200
#     assert b"Logged in as vlad@gmail.com" in rv.data
