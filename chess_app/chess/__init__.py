import dotenv
from flask import Flask

def create_app():
    inner_app = Flask(__name__)

    from chess.routes import main
    from chess.auth import auth

    inner_app.register_blueprint(main)
    inner_app.register_blueprint(auth)

    return inner_app