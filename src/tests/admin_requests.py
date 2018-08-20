class AdminRequests:
    """ Contain methods to send requests on user routes"""

    @staticmethod
    def delete_user(client, user_id):
        return client.delete("admin/users/" + user_id)

    @staticmethod
    def put_user(client, email, username, first_name, last_name, phone, user_id):
        return client.put("admin/users/" + str(user_id), json=dict(
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
