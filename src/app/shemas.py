from marshmallow import Schema, fields, ValidationError, pre_load
# from . import api


# TODO add validation on other pages: resources, models
# TODO import api.models to resources
class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True)
    username = fields.String(required=True)
    userpass = fields.String(required=True)
    first_name = fields.String()
    last_name = fields.String()
    phone = fields.Integer()
    # reg_date = fields.DateTime()
    # salt = fields.String()


# user_post = api.model('Crate New User', {
#     'email': fields.Email,
#     'username': fields.String,
#     'userpass': fields.String,
#     'first_name': fields.String,
#     'last_name': fields.String,
#     'phone': fields.Integer,
# })

class PasswordSchema(Schema):
    pass_id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    url = fields.Url(required=True)
    title = fields.String()
    login = fields.String(required=True)
    password = fields.String(required=True)
    comment = fields.String()


# password_post = api.model('Crate New Password', {
#     'url': fields.Url,
#     'title': fields.String,
#     'login': fields.String,
#     'password': fields.String,
#     'comment': fields.String,
# })