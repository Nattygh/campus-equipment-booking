from getpass import getpass

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()

with app.app_context():
    username = input("Admin username: ").strip()
    password = getpass("Admin password: ")

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        print("A user with that username already exists.")
    else:
        admin = User(
            username=username,
            password_hash=generate_password_hash(password),
            role="admin",
        )

        db.session.add(admin)
        db.session.commit()

        print(f"Admin '{username}' created successfully.")