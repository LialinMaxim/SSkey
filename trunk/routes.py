"""
All routes are kept here
"""

from flask import render_template, url_for, flash, redirect
from trunk import app
from trunk.models import User


# @app.route("/register", methods=["POST"])
# def register():
#     form = RegistrationForm()
#     if form.valide_onsubmit():
#         flash(f"Account created for {form.username.data}!", "success")
#         return redirect(url_for("home"))
#     return ?
