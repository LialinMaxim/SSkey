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


    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
