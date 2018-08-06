import os
import tempfile

from src.app import app
import pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()

    # with app.app_context():
    #     app.init_db()

    yield client


def test_smoke(client):
    rv = client.get("/smoke")
    assert b"Unauthorized Access" in rv.data


def test_home_page(client):
    rv = client.get("/")
    assert b"Home Page" in rv.data

# def test_valid_login(client):
#     rv = client.post("/login", data=dict(email="vlad@gmail.com", password="vlad"))
#     assert rv.status_code == 200
#     assert b"Logged in as vlad@gmail.com" in rv.data
