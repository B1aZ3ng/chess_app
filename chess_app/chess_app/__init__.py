import dotenv
from flask import Flask

def create_app():
    inner_app = Flask(__name__)

    from chess_app.routes import main
    from chess_app.auth import auth
    from chess_app.chessGame import game

    inner_app.register_blueprint(main)
    inner_app.register_blueprint(auth)
    inner_app.register_blueprint(game)

    return inner_app