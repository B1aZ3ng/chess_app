from chess_app import socketio, db
from chess_app.models import ChessGame
from flask import Blueprint, render_template
from flask_login import login_required, current_user


def pastGames(username):
    games = ChessGame.query.filter(
        (ChessGame.playerW == username) | (ChessGame.playerB == username)
    ).all()
    return games