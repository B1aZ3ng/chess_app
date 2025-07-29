#!/usr/bin/env python3
"""
College navigator authentication routes

@author: Roman Yasinovskyy
@version: 2025.7
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session,
)
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from chess_app import db, login_manager
from chess_app.forms import LoginForm, SignupForm
from chess_app.models import User

auth = Blueprint("auth", __name__, url_prefix="/")

user = User()


@auth.route("/signup", methods=["GET", "POST"])
def signup():
  
    form = SignupForm()
    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        passwordAgain = request.form.get("passwordAgain")
        if password == passwordAgain:
            user = User.query.filter_by(username=username).first()
            if user:
                flash("User already exists")
                return redirect(url_for("auth.signup"))
            new_user = User(
                username=username,
                password=generate_password_hash(password),
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("auth.login"))
    return render_template("signup.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Please check your login details and try again.")
            return redirect(url_for("auth.login"))
        else:
            login_user(user)
            session['username'] = user.username
            flash(f"Welcome, {user.username}")
            return redirect(url_for("main.index"))
    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()
