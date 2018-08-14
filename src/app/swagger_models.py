from flask_restplus import fields

from . import api

# Models used to generate swagger documentation
# imported and use in resources.py

user_model = api.model('Create New User', {
    'email': fields.String,
    'username': fields.String,
    'password': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'phone': fields.Integer,
})

user__put_model = api.model('Update User Data', {
    'email': fields.String,
    'username': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'phone': fields.Integer,
})

user_login = api.model('Logging in', {
    'email': fields.String,
    'password': fields.String
})