import os

from dotenv import load_dotenv
from flask import Flask

from app.extensions import db, login_manager

def create_app(config_overrides: dict | None = None):
    load_dotenv()
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "unsafe-development-key",
)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///campus_booking.sqlite3"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    from app.models import User, Equipment, Booking

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app