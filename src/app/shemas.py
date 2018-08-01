from marshmallow import Schema, fields, ValidationError, pre_load


# TODO add validation on other pages: resources, models
class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    userpass = fields.String(required=True)
    salt = fields.String()
    reg_date = fields.DateTime()
    first_name = fields.String()
    last_name = fields.String()
    phone = fields.Integer()


class PasswordSchema(Schema):
    pass_id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    url = fields.Url(required=True)
    title = fields.String()
    login = fields.String(required=True)
    password = fields.String(required=True)
    comment = fields.String()
