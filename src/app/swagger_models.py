from flask_restplus import fields

from . import api

# Models used to generate swagger documentation
# imported and use in resources.py

user_post = api.model('Create New User', {
    'email': fields.String(example='admin@gmail.com'),
    'username': fields.String(example='admin'),
    'password': fields.String(example='admin'),
    'first_name': fields.String(example='Nicola'),
    'last_name': fields.String(example='Tesla'),
    'phone': fields.String(example='068-409-69-36'),
})

password_api_model = api.model('Create New Password', {
    'url': fields.Url(example='https://www.youtube.com'),
    'title': fields.String(example='youtube.com'),
    'login': fields.String(example='admin'),
    'password': fields.String(example='admin'),
    'comment': fields.String(example=''),
})

user_login = api.model('Logging in', {
    'email': fields.String(example='admin@gmail.com'),
    'password': fields.String(example='admin'),
})

user_put = api.model('Update User Data', {
    'email': fields.String(example='admin@gmail.com'),
    'username': fields.String(example='admin'),
    'first_name': fields.String(example='Nicola'),
    'last_name': fields.String(example='Tesla'),
    'phone': fields.String(example='068-409-69-36'),
})

search_password = api.model('Search for password', {
    'condition': fields.String(example='google.com')
})

search_password_url = api.model('Search for password\'s URL', {
    'url': fields.Url(example='https://www.youtube.com')
})
