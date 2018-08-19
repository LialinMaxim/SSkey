import json
import pytest

from src.app import app
from src.app import config
from src.app.base import Base, engine
from src.tests.test_basic import login, logout


@pytest.fixture
def client():
    app.config.from_object(config['testing'])
    client = app.test_client()

    Base.metadata.create_all(engine)

    yield client


def get_all_user_pass(client):
    return client.get('/username/passwords', follow_redirects=True)


def post_new_user_pass(client, url, title, login, password, comment):
    return client.post('/username/passwords', json=dict(
        url=url,
        title=title,
        login=login,
        password=password,
        comment=comment
    ), follow_redirects=True)


def get_particular_user_pass(client, pass_id):
    return client.get('/username/passwords/' + str(pass_id), follow_redirects=True)


def put_particular_user_pass(client, pass_id, url, title='default', login='default', password='default',
                             comment='default'):
    return client.put('/username/passwords/' + str(pass_id), json=dict(
        url=url,
        title=title,
        login=login,
        password=password,
        comment=comment
    ), follow_redirects=True)


def delete_particular_user_pass(client, pass_id):
    return client.delete('/username/passwords/' + str(pass_id), follow_redirects=True)


def search_pass_by_description(client, condition):
    return client.post('/username/passwords/search', json=dict(condition=condition), follow_redirects=True)


def test_post_new_user_pass(client):
    login(client, app.config['EMAIL'], app.config['PASSWORD'])
    rv = post_new_user_pass(client, app.config['URL'], app.config['TITLE'], app.config['LOGIN'], app.config['URL_PASS'],
                            app.config['COMMENT'])
    assert b'PASSWORD ADDED' in rv.data
    logout(client)


def test_get_all_user_pass(client):
    login(client, app.config['EMAIL'], app.config['PASSWORD'])
    rv = get_all_user_pass(client)
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data
    logout(client)


def test_get_particular_user_pass(client):
    login(client, app.config['EMAIL'], app.config['PASSWORD'])
    rv = get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id')
    rv = get_particular_user_pass(client, pass_id)
    assert bytes(app.config['COMMENT'], encoding='utf-8') in rv.data
    logout(client)


def test_put_particular_user_pass(client):
    login(client, app.config['EMAIL'], app.config['PASSWORD'])
    rv = get_all_user_pass(client)

    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id')
    previous_pass = password.get('Your passwords')[0].get('title')

    rv = put_particular_user_pass(client, pass_id, app.config['URL'], title=app.config['TITLE_PUT'],
                                  comment=app.config['COMMENT_PUT'])
    assert bytes(f'Data for {previous_pass} has been updated successfully', encoding='utf-8') in rv.data

    rv = get_particular_user_pass(client, pass_id)
    assert bytes(app.config['COMMENT_PUT'], encoding='utf-8') in rv.data
    logout(client)


def test_search_pass_by_description(client):
    login(client, app.config['EMAIL'], app.config['PASSWORD'])
    condition = 'test password'
    rv = search_pass_by_description(client, condition)

    assert bytes(f'{app.config["TITLE_PUT"]}', encoding='utf-8') in rv.data

    logout(client)


def test_delete_particular_user_pass(client):
    login(client, app.config['EMAIL'], app.config['PASSWORD'])
    rv = get_all_user_pass(client)
    password = json.loads(str(rv.data, encoding='utf-8'))
    pass_id = password.get('Your passwords')[0].get('pass_id')
    rv = delete_particular_user_pass(client, pass_id)
    assert bytes(f'Password ID {pass_id} DELETED', encoding='utf-8') in rv.data
    logout(client)
