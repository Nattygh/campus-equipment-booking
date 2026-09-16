import sys
import os
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import create_app
from app.extensions import db
from app.models import User, Equipment, Booking


@pytest.fixture
def app():
    """A Flask app bound to an in-memory SQLite DB for each test.

    Every app/services/booking_service.py function ends with
    db.session.commit(), so even "unit" tests here need an active app
    context — that's a property of this codebase's design, not something
    we're working around. What we DO isolate explicitly: the clock
    (`now=` parameters throughout booking_service.py are exactly the
    test-double seam the original code already provides) and, in
    test_booking_service_isolated.py, Booking.query itself via
    unittest.mock, so at least one test genuinely never touches a
    database at all.
    """
    application = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
    })
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()


@pytest.fixture
def now():
    return datetime(2026, 9, 10, 12, 0, 0)


def make_user(app, username="student1", role="student", user_id=None):
    u = User(username=username, password_hash="x", role=role)
    if user_id is not None:
        u.id = user_id
    db.session.add(u)
    db.session.commit()
    return u


def make_equipment(app, name="Camera", quantity=3, available_quantity=None, maintenance=False):
    e = Equipment(
        name=name, category="Camera", quantity=quantity,
        available_quantity=available_quantity if available_quantity is not None else quantity,
        maintenance=maintenance,
    )
    db.session.add(e)
    db.session.commit()
    return e


def make_booking(app, user, equipment, start, end, quantity=1, status="REQUESTED"):
    b = Booking(
        user_id=user.id, equipment_id=equipment.id,
        start_date=start, expected_return_date=end,
        quantity=quantity, status=status,
    )
    db.session.add(b)
    db.session.commit()
    return b


@pytest.fixture
def student(app):
    return make_user(app, "student1", "student")


@pytest.fixture
def other_student(app):
    return make_user(app, "student2", "student")


@pytest.fixture
def admin(app):
    return make_user(app, "admin1", "admin")


@pytest.fixture
def equipment(app):
    return make_equipment(app, "Camera", quantity=3)
