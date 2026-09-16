"""Unit tests for the pure (DB-free) parts of booking_service.

validate_dates, validate_quantity, and dates_overlap take plain values
and raise/return plain results - no Flask app context, no database.
"""
from datetime import timedelta

import pytest

from app.services import validate_dates, validate_quantity, dates_overlap


# ---------------------------------------------------------------------------
# validate_dates (REQ-BOOK-DATES)
# ---------------------------------------------------------------------------

def test_ep001_missing_start_date_raises(now):
    with pytest.raises(ValueError, match="required"):
        validate_dates(None, now)


def test_ep002_missing_end_date_raises(now):
    with pytest.raises(ValueError, match="required"):
        validate_dates(now, None)


def test_ep003_start_equal_to_end_raises(now):
    with pytest.raises(ValueError, match="after the start date"):
        validate_dates(now, now)


def test_ep004_start_after_end_raises(now):
    with pytest.raises(ValueError, match="after the start date"):
        validate_dates(now + timedelta(hours=2), now + timedelta(hours=1))


def test_ep005_end_after_start_is_accepted(now):
    validate_dates(now, now + timedelta(hours=1))  # no raise


# ---------------------------------------------------------------------------
# validate_quantity (REQ-BOOK-QTY)
# ---------------------------------------------------------------------------

def test_ep006_none_quantity_raises():
    with pytest.raises(ValueError, match="required"):
        validate_quantity(None)


def test_ep007_zero_quantity_raises():
    with pytest.raises(ValueError, match="greater than zero"):
        validate_quantity(0)


def test_ep008_negative_quantity_raises():
    with pytest.raises(ValueError, match="greater than zero"):
        validate_quantity(-1)


def test_bva001_quantity_of_one_is_accepted():
    validate_quantity(1)  # no raise


def test_ep009_positive_quantity_is_accepted():
    validate_quantity(5)  # no raise


# ---------------------------------------------------------------------------
# dates_overlap
# ---------------------------------------------------------------------------

def test_st001_identical_windows_overlap(now):
    assert dates_overlap(now, now + timedelta(hours=1), now, now + timedelta(hours=1)) is True


def test_st002_disjoint_windows_do_not_overlap(now):
    assert dates_overlap(
        now, now + timedelta(hours=1),
        now + timedelta(hours=2), now + timedelta(hours=3),
    ) is False


def test_st003_adjacent_windows_do_not_overlap(now):
    # b starts exactly when a ends -> half-open interval, no overlap
    assert dates_overlap(
        now, now + timedelta(hours=1),
        now + timedelta(hours=1), now + timedelta(hours=2),
    ) is False


def test_st004_partial_overlap_is_detected(now):
    assert dates_overlap(
        now, now + timedelta(hours=2),
        now + timedelta(hours=1), now + timedelta(hours=3),
    ) is True


def test_st005_fully_contained_window_overlaps(now):
    assert dates_overlap(
        now, now + timedelta(hours=5),
        now + timedelta(hours=1), now + timedelta(hours=2),
    ) is True
