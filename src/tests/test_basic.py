import unittest

from src.app import app


class TestFlaskApiUsingRequests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_hello_world(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    def test_smoke(self):
        response = self.app.get("/smoke")
        self.assertEqual(response.status_code, 200)

    # def test_create_user_valid(self):
    #     response = requests.post('http://localhost:5000/users', data={
    #         'username': 'Seriy', 'email': 'serg@mail.ru', 'userpass': 'password123',
    #         'first_name': 'Sergey', 'last_name': 'Petrov', 'phone': '555-66-777'
    #     })
    #     self.assertEqual(response.json(), {'message': 'USER Seriy REGISTRATION SUCCESSFUL'})
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_get_user_valid(self):
    #     response = requests.get('/users?username=Seriy')
    #     requests.delete('http://localhost:5000/user', data={
    #         'username': 'Seriy'
    #     })
    #     self.assertEqual(response.json()['users'][0]['username'], 'Seriy')
    #     self.assertEqual(response.json()['users'][0]['email'], 'serg@mail.ru')
    #     self.assertEqual(response.json()['users'][0]['last_name'], 'Petrov')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_create_user_empty_required(self):
    #     response = requests.post('/users')
    #     self.assertEqual(response.json(), {'message': "REQUIRED DATA NOT VALID OR BLANK"})
    #     self.assertEqual(response.status_code, 400)
    #
    # def test_get_not_exist_user(self):
    #     response = requests.get('/users?username=vasiliy_petrovich7872')
    #     self.assertEqual(response.json()['users'], [])
    #     self.assertEqual(response.status_code, 200)

    def tearDown(self):
        pass

    # def test_unique_username(self):
    #     user = User(username="test", email="test@gmail.com")
    #     db.session.add(user)
    #     db.session.commit()
    #
    #
    # def test_encode_auth_token(self):
    #     user = User(username="testUser", email="test@test.com", password="test", first_name="test", last_name="test",
    #                 phone=123)
    #     db.session.add(user)
    #     db.session.commit()
    #     auth_token = user.encode_auth_token(user.id)
    #     self.assertTrue(isinstance(auth_token, bytes))
    #     self.assertTrue(User.decode_auth_token(auth_token) == 1)


if __name__ == "__main__":
    unittest.main()
