import json

from flask import request, Response

from manage import app
from app.models import User

@app.route('/user', methods=['GET'])
def get_all_users():
    # users = User.query.all()
    # users = list(map(lambda x: str(x), users))
    # resp = Response(json.dumps(users), status=200)
    resp = Response(json.dumps("USERS"), status=200)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/user', methods=['POST'])
def create_user():

    req_args = request.args

    if User.validate_user_create_data(req_args):
        first_name = req_args['first_name'] if ('first_name' in req_args) else ""
        last_name = req_args['last_name'] if ('last_name' in req_args) else ""
        phone = req_args['phone'] if ('phone' in req_args) else ""

        user = User(req_args['login'], req_args['email'], req_args['password'], first_name, last_name, phone)
        msg = "USER {0} REGISTRATION SUCCESSFUL".format(user.login)
        # try:
        #     db.session.add(user)
        #     db.session.commit()
        # except Exception as e:
        #     msg = str(e)
        resp = Response(json.dumps(msg), status=200)
    else:
        msg = "REQUIRED DATA NOT VALID"
        resp = Response(json.dumps(msg), status=400)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/smoke', methods=['GET'])
def smoke():
    resp = Response(json.dumps("OK"), status=200)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Content-Type'] = 'application/json'
    return resp