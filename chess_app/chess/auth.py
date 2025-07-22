from flask import Blueprint, current_app, flash, redirect, request, session, url_for
import dotenv

import secrets

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.post("/login")
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    if password != current_app["PASSWORD"]:
        flash("Incorrect password")
        return redirect(url_for("main.index"))

    session["name"] = request.form["username"]
    return redirect(url_for("main.index"), code=303)


@auth.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"), code=303)
