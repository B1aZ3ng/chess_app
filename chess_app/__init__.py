import pathlib
import sqlite3

import dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
login_manager = LoginManager()
login_manager.login_view = "auth.login"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
def create_app():
    app = Flask(__name__)

    from chess_app.main import main
    from chess_app.auth import auth
    from chess_app.chessGame import game

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(game)

    from chess_app.auth import auth
    #from chess_app.routes import main

    dotenv.load_dotenv(".flaskenv")
    app.config.from_prefixed_env()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.config.get('DB_NAME')}.sqlite3"
    login_manager.init_app(app)
    db.init_app(app)

    if not pathlib.Path(app.config.get("SQLALCHEMY_DATABASE_URI")).exists():
        with app.app_context():
            db.create_all()
        
    return app