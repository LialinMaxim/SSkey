class BasicRequests:
    """ Contain methods to send requests on basic routes - home and smoke"""

    @staticmethod
    def smoke(client):
        return client.get("/smoke", follow_redirects=True)

    @staticmethod
    def home_page(client):
        assert client.get("/home", follow_redirect=True)

    @staticmethod
    def register(client, email, username, password, first_name, last_name, phone):
        return client.post("/register", json=dict(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        ), follow_redirects=True)
