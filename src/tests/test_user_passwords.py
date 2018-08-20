import json

from src.app import app
from .requests.user_requests import UserRequests
from .requests.basic_requests import BasicRequests
from .requests.admin_requests import AdminRequests
from .requests.login_requests import client, LoginRequests, resource
from src.tests.user_passwords_requests import UserPasswords, PasswordResource


def test_register(client):
    """Make sure register works."""
    rv = BasicRequests.register(client, app.config["EMAIL"], app.config["USERNAME"], app.config["PASSWORD"],
                                app.config["FIRST_NAME"],
                                app.config["LAST_NAME"], app.config["PHONE"])
    assert b"USER testuser ADDED" in rv.data


def test_post_new_user_pass(client, resource):
    rv = UserPasswords.post_new_user_pass(client, app.config['URL'], app.config['TITLE'], app.config['LOGIN'],
                                          app.config['URL_PASS'],
                                          app.config['COMMENT'])
    assert b'PASSWORD ADDED' in rv.data


def test_unprocess_entity_post_new_user_pass(client, resource):
    rv = UserPasswords.post_new_user_pass(client, 111, 111, 111, 111, 111)
    assert '422 UNPROCESSABLE ENTITY' in rv.status


def test_get_all_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data


def test_get_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get(
        'pass_id')  # you get a dictionary that contains as a value list of dictionary
    rv = PasswordResource.get_particular_user_pass(client, pass_id)
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data


def test_put_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)

    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id')
    previous_pass = password.get('Your passwords')[0].get('title')

    rv = PasswordResource.put_particular_user_pass(client, pass_id, app.config['URL'], title=app.config['TITLE_PUT'],
                                                   comment=app.config['COMMENT_PUT'])
    assert bytes(f'Data for {previous_pass} has been updated successfully', encoding='utf-8') in rv.data

    rv = PasswordResource.get_particular_user_pass(client, pass_id)
    assert bytes(app.config['COMMENT_PUT'], encoding='utf-8') in rv.data


def test_search_pass_by_description(client, resource):
    condition = 'test password'
    rv = PasswordResource.search_pass_by_description(client, condition)

    assert bytes(f'{app.config["TITLE_PUT"]}', encoding='utf-8') in rv.data


def test_delete_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id')
    rv = PasswordResource.delete_particular_user_pass(client, pass_id)
    assert bytes(f'Password ID {pass_id} DELETED', encoding='utf-8') in rv.data


def test_delete_user(client, resource):
    """Try to delete user data for existant user"""

    rv = AdminRequests.get_user_by_username(client, app.config["USERNAME"])

    user = json.loads(str(rv.data, encoding='utf-8'))
    user_id = user['id']
    rv = AdminRequests.delete_user(client, str(user['id']))

    assert bytes(f'User ID:{user_id} has been DELETED.', encoding='utf-8') in rv.data
