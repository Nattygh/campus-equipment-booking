"""State transition tests (ST-1xx) for app/services/booking_service.py.

The state model lives in VALID_TRANSITIONS and is enforced by
transition_booking; both the table itself and the enforcing function are
tested here.
"""
from datetime import timedelta

import pytest

from app.services import (
    REQUESTED, APPROVED, REJECTED, ACTIVE, LATE, RETURNED, CANCELLED,
    VALID_TRANSITIONS, transition_booking,
)
from tests.unit.conftest import make_booking

VALID = [
    (REQUESTED, APPROVED),
    (REQUESTED, REJECTED),
    (REQUESTED, CANCELLED),
    (APPROVED, ACTIVE),
    (APPROVED, CANCELLED),
    (ACTIVE, LATE),
    (ACTIVE, RETURNED),
    (LATE, RETURNED),
]

INVALID = [
    (RETURNED, APPROVED),
    (REJECTED, ACTIVE),
    (CANCELLED, APPROVED),
    (RETURNED, CANCELLED),
    (REQUESTED, ACTIVE),      # cannot skip approval
    (REQUESTED, RETURNED),
    (CANCELLED, ACTIVE),
    (LATE, APPROVED),
    (APPROVED, REQUESTED),    # no going backwards
    (ACTIVE, APPROVED),
]


@pytest.mark.parametrize("current,target", VALID)
def test_st1xx_valid_transition_in_table(current, target):
    assert target in VALID_TRANSITIONS[current]


@pytest.mark.parametrize("current,target", INVALID)
def test_st1xx_invalid_transition_not_in_table(current, target):
    assert target not in VALID_TRANSITIONS.get(current, set())


@pytest.mark.parametrize("current,target", VALID)
def test_st2xx_transition_booking_applies_valid_transition(app, student, equipment, now, current, target):
    booking = make_booking(app, student, equipment, now, now + timedelta(hours=1), status=current)
    transition_booking(booking, target)
    assert booking.status == target


@pytest.mark.parametrize("current,target", INVALID)
def test_st3xx_transition_booking_rejects_invalid_transition(app, student, equipment, now, current, target):
    booking = make_booking(app, student, equipment, now, now + timedelta(hours=1), status=current)
    with pytest.raises(ValueError, match="Invalid booking transition"):
        transition_booking(booking, target)
    assert booking.status == current  # unchanged
