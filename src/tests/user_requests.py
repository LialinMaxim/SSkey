class UserRequests:
    """ Contain methods to send requests on user routes"""

    @staticmethod
    def register(client, email, username, password, first_name, last_name, phone):
        return client.post("/register", data=dict(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        ), follow_redirects=True)

    @staticmethod
    def delete_user(client, user_id):
        return client.delete("/users/" + user_id)

    @staticmethod
    def put_user(client, email, username, first_name, last_name, phone, user_id):
        return client.put("/users/" + str(user_id), data=dict(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        ), follow_redirects=True)

    @staticmethod
    def get_user_by_username(client, username):
        return client.get("/users/" + username,
                          follow_redirects=True)
