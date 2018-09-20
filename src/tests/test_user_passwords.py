import json

from src.app import app
from .requests.login_requests import client, resource
from .requests.basic_requests import BasicRequests
from .requests.user_requests import UserRequests
from .requests.user_passwords_requests import UserPasswords, PasswordResource


def test_register(client):
    """Make sure register works."""
    rv = BasicRequests.register(client, app.config['EMAIL'], app.config['USERNAME'], app.config['PASSWORD'],
                                app.config['FIRST_NAME'], app.config['LAST_NAME'], app.config['PHONE'])
    assert bytes(f'USER {app.config["USERNAME"]} ADDED', encoding='utf-8') in rv.data


def test_post_new_user_pass(client, resource):
    rv = UserPasswords.post_new_user_pass(client, app.config['URL'], app.config['TITLE'], app.config['LOGIN'],
                                          app.config['URL_PASS'],
                                          app.config['COMMENT'])
    assert bytes(f'PASSWORD with title {app.config["TITLE"]} ADDED', encoding='utf-8') in rv.data


def test_unprocessable_entity_post_new_user_pass(client, resource):
    rv = UserPasswords.post_new_user_pass(client, 111, 111, 111, 111, 111)
    assert '422 UNPROCESSABLE ENTITY' in rv.status


def test_get_all_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data


def test_get_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    key, value = password.popitem()
    pass_id = value[0].get('pass_id')
    rv = PasswordResource.get_particular_user_pass(client, pass_id)
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data


def test_not_found_pass_get_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    key, value = password.popitem()
    pass_id = value[0].get('pass_id') + 1000
    rv = PasswordResource.get_particular_user_pass(client, pass_id)
    assert bytes('Password Not Found', encoding='utf-8') in rv.data


def test_put_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    key, value = password.popitem()
    pass_id = value[0].get('pass_id')
    rv = PasswordResource.put_particular_user_pass(client, pass_id, app.config['URL'], title=app.config['TITLE_PUT'],
                                                   comment=app.config['COMMENT_PUT'])
    assert bytes(f'Data for {app.config["TITLE_PUT"]} has been updated successfully', encoding='utf-8') in rv.data

    rv = PasswordResource.get_particular_user_pass(client, pass_id)
    assert bytes(app.config['COMMENT_PUT'], encoding='utf-8') in rv.data


def test_not_found_put_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    key, value = password.popitem()
    pass_id = value[0].get('pass_id') + 1000
    rv = PasswordResource.put_particular_user_pass(client, pass_id, app.config['URL'], title=app.config['TITLE_PUT'],
                                                   comment=app.config['COMMENT_PUT'])
    assert bytes('Password Not Found', encoding='utf-8') in rv.data


def test_unprocessable_entity_put_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    key, value = password.popitem()
    pass_id = value[0].get('pass_id') + 1000
    rv = PasswordResource.put_particular_user_pass(client, pass_id, 111, 111, 111)
    assert '422 UNPROCESSABLE ENTITY' in rv.status


def test_search_pass_by_description(client, resource):
    condition = 'anothertest.com'
    rv = PasswordResource.search_pass_by_description(client, condition)

    assert bytes(f'{app.config["TITLE_PUT"]}', encoding='utf-8') in rv.data

    condition = 'another test password'
    rv = PasswordResource.search_pass_by_description(client, condition)

    assert bytes(f'{app.config["COMMENT_PUT"]}', encoding='utf-8') in rv.data


def test_unprocessable_entity_search_pass_by_description(client, resource):
    condition = 111
    rv = PasswordResource.search_pass_by_description(client, condition)

    assert '422 UNPROCESSABLE ENTITY' in rv.status


def test_no_matches_found_search_pass_by_description(client, resource):
    condition = 'nomatchesfound'
    rv = PasswordResource.search_pass_by_description(client, condition)

    assert bytes(f'No matches found for {condition}', encoding='utf-8') in rv.data


def test_not_found_delete_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    key, value = password.popitem()
    pass_id = value[0].get('pass_id') + 1000
    rv = PasswordResource.delete_particular_user_pass(client, pass_id)
    assert bytes('Password Not Found', encoding='utf-8') in rv.data


def test_delete_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    key, value = password.popitem()
    pass_id = value[0].get('pass_id')
    rv = PasswordResource.delete_particular_user_pass(client, pass_id)
    assert bytes(f'Password ID {pass_id} DELETED', encoding='utf-8') in rv.data


def test_delete_user(client, resource):
    """Try to delete user data for existant user"""
    rv = UserRequests.delete_username(client)
    assert bytes(f'User {app.config["USERNAME"]} DELETED', encoding='utf-8') in rv.data
