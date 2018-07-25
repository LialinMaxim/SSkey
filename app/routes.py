import json

from flask import url_for, flash, redirect, request, Response
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required

from app.models import User

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

@app.route("/")
@app.route("/home")
def hello():
    return "<h1>Home Page</h1>"


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You are now able to log in", "success")
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # next_page = request.args.get("next")
            # return redirect(next_page) if next_page else redirect(url_for("home"))
            return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please, check email and password", "")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    flash("Here will be your account")

