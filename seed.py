"""Populate the database with demo data for manual testing.

Run with: python seed.py
Resets the database each time it runs.
"""
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User, Equipment


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(username="admin", password_hash=generate_password_hash("AdminPass123!"), role="admin")
        student = User(username="student1", password_hash=generate_password_hash("StudentPass123!"), role="student")
        db.session.add_all([admin, student])

        items = [
            Equipment(name="Canon EOS 90D", category="Camera", quantity=3, available_quantity=3, maintenance=False),
            Equipment(name="Dell Latitude Laptop", category="Laptop", quantity=5, available_quantity=5, maintenance=False),
            Equipment(name="Epson Projector", category="Projector", quantity=1, available_quantity=1, maintenance=True),
            Equipment(name="Shure SM58 Mic", category="Microphone", quantity=4, available_quantity=4, maintenance=False),
        ]
        db.session.add_all(items)
        db.session.commit()
        print(f"Seeded {len(items)} equipment items and 2 users (admin/student1).")


if __name__ == "__main__":
    seed()
