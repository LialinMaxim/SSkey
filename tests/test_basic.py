import unittest
from manage import app
# from app.models import User, Password


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_smoke(self):
        response = self.app.get("/smoke")
        self.assertEqual(response.status_code, 200)


# class TestUserModel(FlaskTestCase):
#     def test_encode_auth_token(self):
#         user = User(username="testUser", email="test@test.com", password="test", first_name="test", last_name="test",
#                     phone=123)
#         db.session.add(user)
#         db.session.commit()
#         auth_token = user.encode_auth_token(user.id)
#         self.assertTrue(isinstance(auth_token, bytes))
#         self.assertTrue(User.decode_auth_token(auth_token) == 1)


if __name__ == "__main__":
    unittest.main()
