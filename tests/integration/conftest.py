import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import create_app
from app.extensions import db
from app.models import User, Equipment
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    application = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    with application.app_context():
        yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded(app):
    admin = User(username="admin1", password_hash=generate_password_hash("AdminPass123!"), role="admin")
    student = User(username="student1", password_hash=generate_password_hash("StudentPass123!"), role="student")
    student2 = User(username="student2", password_hash=generate_password_hash("StudentPass123!"), role="student")

    camera = Equipment(name="Camera", category="Camera", quantity=1, available_quantity=1, maintenance=False)
    laptop_maint = Equipment(name="Old Laptop", category="Laptop", quantity=2, available_quantity=2, maintenance=True)

    db.session.add_all([admin, student, student2, camera, laptop_maint])
    db.session.commit()

    return {
        "admin": admin,
        "student": student,
        "student2": student2,
        "camera": camera,
        "laptop_maint": laptop_maint,
    }


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)
