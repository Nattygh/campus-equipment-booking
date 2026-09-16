"""IT-3xx: booking creation, admin workflow, and cancellation via routes."""
from datetime import datetime, timedelta

from app import db
from app.models import Booking
from tests.integration.conftest import login

FMT = "%Y-%m-%dT%H:%M"


def _fmt(dt):
    return dt.strftime(FMT)


def test_it301_submit_booking_creates_row(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    resp = client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=1)),
            "expected_return_date": _fmt(now + timedelta(hours=2)),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    booking = db.session.query(Booking).filter_by(equipment_id=seeded["camera"].id).first()
    assert booking is not None
    assert booking.status == "REQUESTED"


def test_it302_booking_maintenance_equipment_rejected(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    resp = client.post(
        f"/equipment/{seeded['laptop_maint'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=1)),
            "expected_return_date": _fmt(now + timedelta(hours=2)),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"maintenance" in resp.data
    assert db.session.query(Booking).count() == 0


def test_it303_booking_invalid_dates_rejected(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    resp = client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=2)),
            "expected_return_date": _fmt(now + timedelta(hours=1)),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert db.session.query(Booking).count() == 0


def test_it304_second_conflicting_booking_rejected(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=1)),
            "expected_return_date": _fmt(now + timedelta(hours=2)),
        },
    )
    client.get("/logout")
    login(client, "student2", "StudentPass123!")
    resp = client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=1, minutes=30)),
            "expected_return_date": _fmt(now + timedelta(hours=2, minutes=30)),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert db.session.query(Booking).count() == 1


def test_it305_full_lifecycle_approve_activate_return(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=1)),
            "expected_return_date": _fmt(now + timedelta(hours=2)),
        },
    )
    booking = db.session.query(Booking).first()
    client.get("/logout")

    login(client, "admin1", "AdminPass123!")
    client.post(f"/admin/bookings/{booking.id}/approve")
    assert db.session.get(Booking, booking.id).status == "APPROVED"

    client.post(f"/admin/bookings/{booking.id}/activate")
    reloaded = db.session.get(Booking, booking.id)
    assert reloaded.status == "ACTIVE"
    assert db.session.get(type(seeded["camera"]), seeded["camera"].id).available_quantity == 0

    client.post(f"/admin/bookings/{booking.id}/return")
    final = db.session.get(Booking, booking.id)
    assert final.status == "RETURNED"
    assert db.session.get(type(seeded["camera"]), seeded["camera"].id).available_quantity == 1


def test_it306_admin_can_reject_booking(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=1)),
            "expected_return_date": _fmt(now + timedelta(hours=2)),
        },
    )
    booking = db.session.query(Booking).first()
    client.get("/logout")

    login(client, "admin1", "AdminPass123!")
    resp = client.post(f"/admin/bookings/{booking.id}/reject", follow_redirects=True)
    assert resp.status_code == 200
    assert db.session.get(Booking, booking.id).status == "REJECTED"


# ---------------------------------------------------------------------------
# Cancellation (the feature added during this refinement pass)
# ---------------------------------------------------------------------------

def test_it307_owner_can_cancel_own_booking(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=2)),
            "expected_return_date": _fmt(now + timedelta(hours=3)),
        },
    )
    booking = db.session.query(Booking).first()

    resp = client.post(f"/bookings/{booking.id}/cancel", follow_redirects=True)
    assert resp.status_code == 200
    assert db.session.get(Booking, booking.id).status == "CANCELLED"


def test_it308_other_student_cannot_cancel_someone_elses_booking(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=2)),
            "expected_return_date": _fmt(now + timedelta(hours=3)),
        },
    )
    booking = db.session.query(Booking).first()
    client.get("/logout")

    login(client, "student2", "StudentPass123!")
    resp = client.post(f"/bookings/{booking.id}/cancel", follow_redirects=True)
    assert resp.status_code == 200
    assert db.session.get(Booking, booking.id).status == "REQUESTED"


def test_it309_admin_can_cancel_a_students_booking(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=2)),
            "expected_return_date": _fmt(now + timedelta(hours=3)),
        },
    )
    booking = db.session.query(Booking).first()
    client.get("/logout")

    login(client, "admin1", "AdminPass123!")
    resp = client.post(f"/bookings/{booking.id}/cancel", follow_redirects=True)
    assert resp.status_code == 200
    assert db.session.get(Booking, booking.id).status == "CANCELLED"


def test_it310_my_bookings_auto_flags_late(client, seeded):
    login(client, "student1", "StudentPass123!")
    now = datetime.utcnow() + timedelta(minutes=5)
    client.post(
        f"/equipment/{seeded['camera'].id}/book",
        data={
            "quantity": "1",
            "start_date": _fmt(now + timedelta(hours=1)),
            "expected_return_date": _fmt(now + timedelta(hours=2)),
        },
    )
    booking = db.session.query(Booking).first()
    client.get("/logout")

    login(client, "admin1", "AdminPass123!")
    client.post(f"/admin/bookings/{booking.id}/approve")
    client.post(f"/admin/bookings/{booking.id}/activate")

    b = db.session.get(Booking, booking.id)
    b.start_date = now - timedelta(hours=5)
    b.expected_return_date = now - timedelta(hours=1)
    db.session.commit()

    client.get("/logout")
    login(client, "student1", "StudentPass123!")
    resp = client.get("/bookings")
    assert resp.status_code == 200
    assert db.session.get(Booking, booking.id).status == "LATE"
