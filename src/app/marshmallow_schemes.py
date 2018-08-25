from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Integer()
    email = fields.Email(required=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    first_name = fields.String()
    last_name = fields.String()
    phone = fields.String()
    is_admin = fields.Bool(load_only=True)


class PasswordSchema(Schema):
    pass_id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    url = fields.Url(required=True)
    title = fields.String()
    login = fields.String()
    password = fields.String()
    comment = fields.String()


class SearchSchema(Schema):
    condition = fields.String(required=True)


class SearchPasswordUrlSchema(Schema):
    url = fields.Url(required=True)


class UserIdsListSchema(Schema):
    users_ids = fields.List(fields.Integer(), required=True)


class AdminUsersSearchData(Schema):
    user_data = fields.String(required=True)
