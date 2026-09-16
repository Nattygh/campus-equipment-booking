"""Unit tests (UT-xxx) for app/services/booking_service.py business logic.

Runs against an in-memory SQLite DB (see conftest.py for why every
function here needs an app context). Time-dependent behaviour is isolated
using the `now=` parameter the service functions already expose as a
test-double seam.
"""
from datetime import timedelta

import pytest

from app.services import (
    REQUESTED, APPROVED, ACTIVE, LATE, RETURNED, CANCELLED,
    check_availability, create_booking, approve_booking, reject_booking,
    activate_booking, mark_late, return_booking, cancel_booking,
    calculate_reserved_quantity,
)
from tests.unit.conftest import make_booking, make_equipment


# ---------------------------------------------------------------------------
# check_availability / calculate_reserved_quantity
# ---------------------------------------------------------------------------

def test_ut001_no_bookings_full_quantity_available(app, equipment, now):
    reserved = calculate_reserved_quantity(equipment.id, now, now + timedelta(hours=1))
    assert reserved == 0


def test_ut002_overlapping_booking_increases_reserved_quantity(app, student, equipment, now):
    make_booking(app, student, equipment, now, now + timedelta(hours=2), quantity=2, status=REQUESTED)
    reserved = calculate_reserved_quantity(equipment.id, now + timedelta(minutes=30), now + timedelta(hours=1))
    assert reserved == 2


def test_ut003_non_overlapping_booking_does_not_count(app, student, equipment, now):
    make_booking(app, student, equipment, now, now + timedelta(hours=1), quantity=2, status=REQUESTED)
    reserved = calculate_reserved_quantity(equipment.id, now + timedelta(hours=1), now + timedelta(hours=2))
    assert reserved == 0  # half-open interval: touching, not overlapping


def test_ut004_cancelled_booking_does_not_reserve_stock(app, student, equipment, now):
    make_booking(app, student, equipment, now, now + timedelta(hours=1), quantity=2, status=CANCELLED)
    reserved = calculate_reserved_quantity(equipment.id, now, now + timedelta(hours=1))
    assert reserved == 0


def test_ut005_rejected_booking_does_not_reserve_stock(app, student, equipment, now):
    make_booking(app, student, equipment, now, now + timedelta(hours=1), quantity=2, status="REJECTED")
    reserved = calculate_reserved_quantity(equipment.id, now, now + timedelta(hours=1))
    assert reserved == 0


def test_ut006_check_availability_true_when_stock_sufficient(app, equipment, now):
    assert check_availability(equipment, 3, now, now + timedelta(hours=1)) is True


def test_ut007_check_availability_raises_when_quantity_exceeds_stock(app, equipment, now):
    with pytest.raises(ValueError, match="exceeds total"):
        check_availability(equipment, 4, now, now + timedelta(hours=1))


def test_ut008_check_availability_raises_under_maintenance(app, now):
    eq = make_equipment(app, maintenance=True)
    with pytest.raises(ValueError, match="maintenance"):
        check_availability(eq, 1, now, now + timedelta(hours=1))


def test_ut009_check_availability_raises_when_reserved_by_others(app, student, equipment, now):
    make_booking(app, student, equipment, now, now + timedelta(hours=1), quantity=3, status=REQUESTED)
    with pytest.raises(ValueError, match="not available"):
        check_availability(equipment, 1, now, now + timedelta(hours=1))


# ---------------------------------------------------------------------------
# create_booking
# ---------------------------------------------------------------------------

def test_ut010_create_booking_succeeds_and_persists(app, student, equipment, now):
    booking = create_booking(
        user_id=student.id, equipment_id=equipment.id, quantity=1,
        start_date=now + timedelta(hours=1), expected_return_date=now + timedelta(hours=2),
    )
    assert booking.id is not None
    assert booking.status == REQUESTED


def test_ut011_create_booking_raises_for_unknown_equipment(app, student, now):
    with pytest.raises(ValueError, match="Equipment not found"):
        create_booking(
            user_id=student.id, equipment_id=99999, quantity=1,
            start_date=now + timedelta(hours=1), expected_return_date=now + timedelta(hours=2),
        )


def test_ut012_create_booking_raises_when_over_capacity(app, student, equipment, now):
    with pytest.raises(ValueError):
        create_booking(
            user_id=student.id, equipment_id=equipment.id, quantity=10,
            start_date=now + timedelta(hours=1), expected_return_date=now + timedelta(hours=2),
        )


# ---------------------------------------------------------------------------
# approve_booking / reject_booking
# ---------------------------------------------------------------------------

def test_ut013_approve_requested_booking_succeeds(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now + timedelta(hours=1), now + timedelta(hours=2))
    approve_booking(booking)
    assert booking.status == APPROVED


def test_ut014_approve_non_requested_booking_raises(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now + timedelta(hours=1), now + timedelta(hours=2), status=APPROVED)
    with pytest.raises(ValueError, match="Only requested bookings"):
        approve_booking(booking)


def test_ut015_approve_rechecks_availability_and_rejects_conflict(app, student, other_student, equipment, now):
    # first booking already approved, consuming all 3 units
    make_booking(app, other_student, equipment, now, now + timedelta(hours=1), quantity=3, status=APPROVED)
    pending = make_booking(app, student, equipment, now, now + timedelta(hours=1), quantity=1, status=REQUESTED)
    with pytest.raises(ValueError, match="not available"):
        approve_booking(pending)


def test_ut016_reject_requested_booking_succeeds(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now, now + timedelta(hours=1))
    reject_booking(booking)
    assert booking.status == "REJECTED"


# ---------------------------------------------------------------------------
# activate_booking
# ---------------------------------------------------------------------------

def test_ut017_activate_approved_booking_reduces_available_quantity(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now, now + timedelta(hours=1), quantity=2, status=APPROVED)
    activate_booking(booking)
    assert booking.status == ACTIVE
    assert equipment.available_quantity == 1  # started at 3, minus 2


def test_ut018_activate_non_approved_booking_raises(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now, now + timedelta(hours=1), status=REQUESTED)
    with pytest.raises(ValueError, match="Only approved bookings"):
        activate_booking(booking)


def test_ut019_activate_raises_when_equipment_under_maintenance(app, student, now):
    eq = make_equipment(app, maintenance=False)  # created bookable...
    booking = make_booking(app, student, eq, now, now + timedelta(hours=1), status=APPROVED)
    eq.maintenance = True  # ...then put under maintenance before hand-over
    with pytest.raises(ValueError, match="maintenance"):
        activate_booking(booking)


def test_ut020_activate_raises_when_physical_stock_insufficient(app, student, equipment, now):
    equipment.available_quantity = 0  # already all checked out physically
    booking = make_booking(app, student, equipment, now, now + timedelta(hours=1), quantity=1, status=APPROVED)
    with pytest.raises(ValueError, match="Not enough physical equipment"):
        activate_booking(booking)


# ---------------------------------------------------------------------------
# mark_late (test double: `now` is injected, never reads the real clock)
# ---------------------------------------------------------------------------

def test_ut021_mark_late_transitions_active_past_due_booking(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now - timedelta(hours=2), now - timedelta(hours=1), status=ACTIVE)
    mark_late(booking, now=now)
    assert booking.status == LATE


def test_ut022_mark_late_raises_when_not_yet_due(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now, now + timedelta(hours=1), status=ACTIVE)
    with pytest.raises(ValueError, match="not late yet"):
        mark_late(booking, now=now)


def test_ut023_mark_late_raises_for_non_active_booking(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now - timedelta(hours=2), now - timedelta(hours=1), status=REQUESTED)
    with pytest.raises(ValueError, match="Only active bookings"):
        mark_late(booking, now=now)


# ---------------------------------------------------------------------------
# return_booking
# ---------------------------------------------------------------------------

def test_ut024_return_active_booking_restores_available_quantity(app, student, equipment, now):
    equipment.available_quantity = 1  # 2 currently checked out
    booking = make_booking(app, student, equipment, now - timedelta(hours=2), now - timedelta(hours=1), quantity=2, status=ACTIVE)
    return_booking(booking, actual_return_date=now)
    assert booking.status == RETURNED
    assert equipment.available_quantity == 3  # capped back at total


def test_ut025_return_late_booking_succeeds(app, student, equipment, now):
    equipment.available_quantity = 2
    booking = make_booking(app, student, equipment, now - timedelta(hours=3), now - timedelta(hours=1), quantity=1, status=LATE)
    return_booking(booking, actual_return_date=now)
    assert booking.status == RETURNED


def test_ut026_return_non_active_non_late_booking_raises(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now, now + timedelta(hours=1), status=REQUESTED)
    with pytest.raises(ValueError, match="Only active or late"):
        return_booking(booking)


def test_ut027_return_never_pushes_available_quantity_above_total(app, student, equipment, now):
    """Regression guard: available_quantity must be capped at equipment.quantity."""
    equipment.available_quantity = equipment.quantity  # nothing was ever decremented (edge case)
    booking = make_booking(app, student, equipment, now - timedelta(hours=2), now - timedelta(hours=1), quantity=1, status=ACTIVE)
    return_booking(booking, actual_return_date=now)
    assert equipment.available_quantity == equipment.quantity


# ---------------------------------------------------------------------------
# cancel_booking (new feature added during this refinement pass)
# ---------------------------------------------------------------------------

def test_ut028_owner_can_cancel_before_start(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now + timedelta(hours=2), now + timedelta(hours=3))
    cancel_booking(booking, student, now=now)
    assert booking.status == CANCELLED


def test_ut029_admin_can_cancel_someone_elses_booking(app, student, admin, equipment, now):
    booking = make_booking(app, student, equipment, now + timedelta(hours=2), now + timedelta(hours=3))
    cancel_booking(booking, admin, now=now)
    assert booking.status == CANCELLED


def test_ut030_other_student_cannot_cancel(app, student, other_student, equipment, now):
    booking = make_booking(app, student, equipment, now + timedelta(hours=2), now + timedelta(hours=3))
    with pytest.raises(PermissionError):
        cancel_booking(booking, other_student, now=now)
    assert booking.status == REQUESTED  # unchanged


def test_ut031_cannot_cancel_after_start_time(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now - timedelta(minutes=1), now + timedelta(hours=1), status=APPROVED)
    with pytest.raises(ValueError, match="cancellation deadline"):
        cancel_booking(booking, student, now=now)


def test_ut032_cancel_approved_booking_also_allowed(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now + timedelta(hours=1), now + timedelta(hours=2), status=APPROVED)
    cancel_booking(booking, student, now=now)
    assert booking.status == CANCELLED


def test_ut033_cannot_cancel_an_active_booking(app, student, equipment, now):
    booking = make_booking(app, student, equipment, now - timedelta(hours=1), now + timedelta(hours=1), status=ACTIVE)
    with pytest.raises(ValueError):
        cancel_booking(booking, student, now=now)
