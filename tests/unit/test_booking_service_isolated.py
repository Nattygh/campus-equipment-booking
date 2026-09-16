"""A genuinely DB-free unit test using a Mock test double for Booking.query.

Every other unit test in this suite runs against a real in-memory SQLite
DB (see conftest.py for why). This file demonstrates full isolation using
unittest.mock to stub the ORM collaborator directly, satisfying the
"at least one test double used to isolate a unit from a collaborator"
requirement with a genuine mock, on top of the `now=` injection seam
already used throughout test_booking_service.py.
"""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.services.booking_service import get_overlapping_bookings


class FakeBooking:
    """A lightweight stand-in for a Booking row, with just the fields
    get_overlapping_bookings' Python-side filtering actually reads."""

    def __init__(self, start_date, expected_return_date):
        self.start_date = start_date
        self.expected_return_date = expected_return_date


def test_ut_isolated_001_filters_using_mocked_query_no_database():
    now = datetime(2026, 9, 10, 12, 0, 0)

    overlapping = FakeBooking(now, now + timedelta(hours=2))
    non_overlapping = FakeBooking(now + timedelta(hours=5), now + timedelta(hours=6))

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = [overlapping, non_overlapping]

    with patch("app.services.booking_service.Booking") as MockBooking:
        MockBooking.query.filter.return_value = mock_query_result
        MockBooking.equipment_id = "equipment_id"
        MockBooking.status = MagicMock()
        MockBooking.status.in_ = MagicMock(return_value="status-filter")

        result = get_overlapping_bookings(
            equipment_id=1,
            start_date=now,
            expected_return_date=now + timedelta(hours=1),
        )

    # Only the truly overlapping fake booking should survive the
    # Python-side dates_overlap filtering, and no real database or app
    # context was touched anywhere in this test.
    assert result == [overlapping]
    MockBooking.query.filter.assert_called_once()
