import unittest
import manage
# import flaskapi

import requests


class TestFlaskApiUsingRequests(unittest.TestCase):
    def setUp(self):
        pass

    def test_hello_world(self):
        response = requests.get('http://localhost:5000/')
        self.assertEqual(response.json(), {'message': 'Home Page'})
        self.assertEqual(response.status_code, 200)

    def test_smoke(self):
        response = requests.get('http://localhost:5000/smoke')
        self.assertEqual(response.json(), {'message': 'OK'})
        self.assertEqual(response.status_code, 200)

    def test_create_user_valid(self):
        response = requests.post('http://localhost:5000/user', data={
            'username': 'Seriy', 'email': 'serg@mail.ru', 'userpass': 'password123',
            'first_name': 'Sergey', 'last_name': 'Petrov', 'phone': '555-66-777'
        })
        self.assertEqual(response.json(), {'message': 'USER Seriy REGISTRATION SUCCESSFUL'})
        self.assertEqual(response.status_code, 200)

    def test_get_user_valid(self):
        response = requests.get('http://localhost:5000/user?username=Seriy')
        requests.delete('http://localhost:5000/user', data={
            'username': 'Seriy'
        })
        self.assertEqual(response.json()['users'][0]['username'], 'Seriy')
        self.assertEqual(response.json()['users'][0]['email'], 'serg@mail.ru')
        self.assertEqual(response.json()['users'][0]['last_name'], 'Petrov')
        self.assertEqual(response.status_code, 200)

    def test_create_user_empty_required(self):
        response = requests.post('http://localhost:5000/user')
        self.assertEqual(response.json(), {'message': "REQUIRED DATA NOT VALID OR BLANK"})
        self.assertEqual(response.status_code, 400)

    def test_get_not_exist_user(self):
        response = requests.get('http://localhost:5000/user?username=vasiliy_petrovich7872')
        self.assertEqual(response.json()['users'], [])
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
