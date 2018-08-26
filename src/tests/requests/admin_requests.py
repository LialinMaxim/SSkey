class AdminRequests:
    """ Contain methods to send requests on user routes"""

    @staticmethod
    def delete_user(client, user_id):
        return client.delete('admin/users/' + user_id)

    @staticmethod
    def put_user(client, email, username, first_name, last_name, phone, user_id):
        return client.put('admin/users/' + str(user_id), json=dict(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        ), follow_redirects=True)

    @staticmethod
    def get_user_by_username(client, username):
        return client.get('admin/users/' + username,
                          follow_redirects=True)

    @staticmethod
    def batch_users_delete(client, users_ids):
        return client.delete('admin/users', json=dict(
            users_ids=users_ids,
        ), follow_redirects=True)

    @staticmethod
    def search_users_by_any_field(client, user_data):
        return client.post('admin/users/search', json=dict(
            user_data=user_data,
        ), follow_redirects=True)
