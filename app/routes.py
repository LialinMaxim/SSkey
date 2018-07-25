"""
All routes are kept here
"""
from flask import url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import login_user, logout_user, login_required


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
