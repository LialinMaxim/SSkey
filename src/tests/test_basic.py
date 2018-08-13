import os
import tempfile
from ..app.models import Password

from src.app import app
import pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()

    # with app.app_context():
    #     app.init_db()

    yield client
#


def test_password_encode_decode():
    password = Password('vasya', 'vasya777', 1, "", "", "")
    assert password.password != 'vasya777'
    assert password.decrypt_password() == 'vasya777'


def test_smoke(client):
    rv = client.get("/smoke")
    assert b"OK" in rv.data


def test_home_page(client):
    rv = client.get("/home")
    assert b"Home Page" in rv.data

def test_register(client):
    rv = client.post("/register", json={
                                        "username": "vasily11",
                                        "userpass": "vasily11",
                                        "email": "vasily345@vc.vc",
                                        "first_name": "vasya",
                                        "last_name": "petrov",
                                        "phone": "123321"
                                        })
    assert b"SUCCESSFUL ADDED" in rv.data

# def test_de(client):
#     rv = client.post("/register", json={
#                                         "username": "vasily11",
#                                         "userpass": "vasily11",
#                                         "email": "vasily345@vc.vc"
#                                         })
#     assert b"SUCCESSFUL ADDED" in rv.data

# def test_valid_login(client):
#     rv = client.post("/login", data=dict(email="vlad@gmail.com", password="vlad"))
#     assert rv.status_code == 200
#     assert b"Logged in as vlad@gmail.com" in rv.data
