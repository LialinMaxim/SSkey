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
    assert b'PASSWORD ADDED' in rv.data


def test_unprocessable_entity_post_new_user_pass(client, resource):
    rv = UserPasswords.post_new_user_pass(client, 111, 111, 111, 111, 111)
    assert '422 UNPROCESSABLE ENTITY' in rv.status


def test_get_all_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data


def test_post_search_password_by_valid_url(client, resource):
    """Test of searching password by valid URL

    HTTP Code: 200
    """
    rv = PasswordResource.post_search_password_url(client, app.config['URL'])
    assert bytes(app.config['URL'], encoding='utf-8') in rv.data
    assert bytes(app.config['TITLE'], encoding='utf-8') in rv.data
    assert bytes(app.config['LOGIN'], encoding='utf-8') in rv.data
    assert bytes(app.config['URL_PASS'], encoding='utf-8') in rv.data
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data


def test_post_search_password_by_invalid_url(client, resource):
    """Test of searching password by invalid URL

    HTTP Code: 422
    """
    rv = PasswordResource.post_search_password_url(client, 'invalid.url')
    assert b'Not a valid URL.' in rv.data


def test_post_search_password_by_nonexistent_url(client, resource):
    """Test of searching password by nonexistent URL

    HTTP Code: 200
    """
    rv = PasswordResource.post_search_password_url(client, 'https://nonexistent.url')
    assert b'No matches found' in rv.data


def test_get_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get(
        'pass_id')  # you get a dictionary that contains as a value list of dictionary
    rv = PasswordResource.get_particular_user_pass(client, pass_id)
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data


def test_not_found_pass_get_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id') + 1000
    rv = PasswordResource.get_particular_user_pass(client, pass_id)
    assert bytes('Password Not Found', encoding='utf-8') in rv.data


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


def test_not_found_put_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id') + 1000

    rv = PasswordResource.put_particular_user_pass(client, pass_id, app.config['URL'], title=app.config['TITLE_PUT'],
                                                   comment=app.config['COMMENT_PUT'])
    assert bytes('Password Not Found', encoding='utf-8') in rv.data


def test_unprocessable_entity_put_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id') + 1000
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

    assert b'No matches found' in rv.data


def test_not_found_delete_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id') + 1000

    rv = PasswordResource.delete_particular_user_pass(client, pass_id)
    assert bytes('Password Not Found', encoding='utf-8') in rv.data


def test_delete_particular_user_pass(client, resource):
    rv = UserPasswords.get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id')
    rv = PasswordResource.delete_particular_user_pass(client, pass_id)
    assert bytes(f'Password ID {pass_id} DELETED', encoding='utf-8') in rv.data


def test_delete_user(client, resource):
    """Try to delete user data for existant user"""
    rv = UserRequests.delete_username(client)
    assert bytes(f'User {app.config["USERNAME"]} DELETED', encoding='utf-8') in rv.data
