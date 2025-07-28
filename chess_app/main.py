#!/usr/bin/env python3

from flask import Blueprint, abort, current_app, render_template, request, session, redirect,url_for
from flask_login import login_required
main = Blueprint("main", __name__, url_prefix="/")


@main.get("/")
def index():
    session ['board'] = session.get('board', None)
    return render_template("startGame.html")
    

@main.post("/startGame")
def startGame():
    return "hi"


@main.get("/profile")
@login_required
def profile():
    return render_template("index.html")