class UserPasswords:
    """
    Contains all requests for user's passwords
    """

    @staticmethod
    def get_all_user_pass(client):
        return client.get('/username/passwords', follow_redirects=True)

    @staticmethod
    def post_new_user_pass(client, url, title, login, password, comment):
        return client.post('/username/passwords', json=dict(
            url=url,
            title=title,
            login=login,
            password=password,
            comment=comment
        ), follow_redirects=True)


class PasswordResource:
    """
    Contains all requests for dealing with particular user passwords
    """

    @staticmethod
    def get_particular_user_pass(client, pass_id):
        return client.get('/username/passwords/' + str(pass_id), follow_redirects=True)

    @staticmethod
    def put_particular_user_pass(client, pass_id, url, title='default', login='default', password='default',
                                 comment='default'):
        return client.put('/username/passwords/' + str(pass_id), json=dict(
            url=url,
            title=title,
            login=login,
            password=password,
            comment=comment
        ), follow_redirects=True)

    @staticmethod
    def delete_particular_user_pass(client, pass_id):
        return client.delete('/username/passwords/' + str(pass_id), follow_redirects=True)

    @staticmethod
    def search_pass_by_description(client, condition):
        return client.post('/username/passwords/search', json=dict(condition=condition), follow_redirects=True)
