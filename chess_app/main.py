#!/usr/bin/env python3
# asd.khlasdjkhflasjkhdfaljhflaskdjfhalkdfjhalh
from flask import Blueprint, abort, current_app, render_template, request, session, redirect,url_for
from flask_login import login_required,current_user
from chess_app.logic import pastGames
from flask_socketio import emit
main = Blueprint("main", __name__, url_prefix="/")


@main.get("/")
def index():
    session ['board'] = session.get('board', None)
    return render_template("startGame.html")
    






                                                    
@main.get("/profile")
@login_required
def profile():
    username = current_user.username
    games = pastGames(username)
    print("Games:", games)
    return render_template("profile.html",games=games)


