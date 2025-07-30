from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from sqlalchemy.orm import DeclarativeBase
import dotenv
import pathlib
from flask_apscheduler import APScheduler
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

scheduler = APScheduler()
# ---- Extensions (Globally Initialized) ----
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
socketio = SocketIO()

# ---- App Factory ----
def create_app():
    app = Flask(__name__)

    # Load environment variables
    dotenv.load_dotenv(".flaskenv")
    app.config.from_prefixed_env()

    # Set database URI
    db_name = app.config.get("DB_NAME", "default")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}.sqlite3"

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    # Register blueprints
    from chess_app.main import main
    from chess_app.auth import auth
    from chess_app.chessGame import game

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(game)

    # Create DB if missing
    db_path = pathlib.Path(f"{db_name}.sqlite3")
    if not db_path.exists():
        with app.app_context():
            db.create_all()

    return app