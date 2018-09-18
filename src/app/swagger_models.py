from flask_restplus import fields, reqparse

from . import api

# Models used to generate swagger documentation
# imported and use in resources

user_post = api.model('Create New User', {
    'length': fields.String(example='admin@gmail.com'),
    'number': fields.String(example='admin'),
    'password': fields.String(example='admin'),
    'first_name': fields.String(example='Nicola'),
    'last_name': fields.String(example='Tesla'),
    'phone': fields.String(example='068-409-69-36'),
})

# for password generator
generate_parser = reqparse.RequestParser()
generate_parser.add_argument('length', type=int, required=True, default=8, help='length')
generate_parser.add_argument('uppercase', type=str, default='NO', choices=['YES', 'NO'], help='Upper Case')
generate_parser.add_argument('digit', type=str, default='YES', choices=['YES', 'NO'], help='Digits')
generate_parser.add_argument('symbol', type=str, default='NO', choices=['YES', 'NO'], help='Symbols')

# for admin route with all user
admin_users_parser = reqparse.RequestParser()
admin_users_parser.add_argument('page', type=int, default=1, help='Page')
admin_users_parser.add_argument('elements', type=int, default=10,
                                choices=[1, 5, 10, 20, 50, 100], help='Elements on page')
admin_users_parser.add_argument('password_counter', type=str, default='NO',
                                choices=['YES', 'NO'], help='Count passwords')

# for user passwords list
user_passwords_parser = reqparse.RequestParser()
user_passwords_parser.add_argument('page', type=int, default=1, help='Page')
user_passwords_parser.add_argument('elements', type=int, default=10,
                                   choices=[1, 5, 10, 20, 50, 100], help='Elements on page')

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

users_ids_list = api.model('Delete users by id list', {
    'users_ids': fields.List(fields.Integer(), example=[1, 2, 3])
})
admin_users_search = api.model('Search users by any data', {
    'user_data': fields.String(example='Tesla')
})
