import os
import tempfile

import pytest

from app import app


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
    assert b"OK" in rv.data


def test_home_page(client):
    rv = client.get("/")
    assert b"Home Page" in rv.data
#     # def test_create_user_valid(self):
#     #     response = requests.post('http://localhost:5000/users', data={
#     #         'username': 'Seriy', 'email': 'serg@mail.ru', 'userpass': 'password123',
#     #         'first_name': 'Sergey', 'last_name': 'Petrov', 'phone': '555-66-777'
#     #     })
#     #     self.assertEqual(response.json(), {'message': 'USER Seriy REGISTRATION SUCCESSFUL'})
#     #     self.assertEqual(response.status_code, 200)
#     #
#     # def test_get_user_valid(self):
#     #     response = requests.get('/users?username=Seriy')
#     #     requests.delete('http://localhost:5000/user', data={
#     #         'username': 'Seriy'
#     #     })
#     #     self.assertEqual(response.json()['users'][0]['username'], 'Seriy')
#     #     self.assertEqual(response.json()['users'][0]['email'], 'serg@mail.ru')
#     #     self.assertEqual(response.json()['users'][0]['last_name'], 'Petrov')
#     #     self.assertEqual(response.status_code, 200)
#     #
#     # def test_create_user_empty_required(self):
#     #     response = requests.post('/users')
#     #     self.assertEqual(response.json(), {'message': "REQUIRED DATA NOT VALID OR BLANK"})
#     #     self.assertEqual(response.status_code, 400)
#     #
#     # def test_get_not_exist_user(self):
#     #     response = requests.get('/users?username=vasiliy_petrovich7872')
#     #     self.assertEqual(response.json()['users'], [])
#     #     self.assertEqual(response.status_code, 200)
#
#     def tearDown(self):
#         pass
