class UserRequests:
    @staticmethod
    def get_username(client):
        return client.get('/user')

    @staticmethod
    def put_username(client, email, username, first_name, last_name, phone):
        return client.put('/user', json=dict(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        ))

    @staticmethod
    def delete_username(client):
        return client.delete('/user')
