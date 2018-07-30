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
        # self.assertEqual(response.json()[0], {'users': []})
        self.assertEqual(response.status_code, 200)

    def test_delete_user_valid(self):
        response = requests.delete('http://localhost:5000/user', data={
            'username': 'Seriy'
        })
        self.assertEqual(response.json(), {'message': 'User Seriy has been deleted successfully'})
        self.assertEqual(response.status_code, 200)


    # def test_create_user_not_valid(self):
    #     response = requests.post('http://localhost:5000/user', data={
    #         'username': 'Andrey', 'email': 'serg@mail.ru', 'password': 'password123'
    #     })
    #     self.assertEqual(response.json(), {'message': 'USER Seriy REGISTRATION SUCCESSFUL'})
    #     self.assertEqual(response.status_code, 200)


    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
