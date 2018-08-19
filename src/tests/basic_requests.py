class BasicRequests:
    """ Contain methods to send requests on basic routes - home and smoke"""

    @staticmethod
    def smoke(client):
        return client.get("/smoke", follow_redirects=True)

    @staticmethod
    def test_home_page(client):
        rv = client.get("/home")
        assert b"Home Page" in rv.data
