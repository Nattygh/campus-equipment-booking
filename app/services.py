from datetime import datetime

from app.models import Booking, Equipment


VALID_BOOKING_STATUSES = {
    "REQUESTED",
    "APPROVED",
    "ACTIVE",
    "LATE",
    "RETURNED",
    "REJECTED",
    "CANCELLED",
}


def validate_booking(
    equipment: Equipment,
    quantity: int,
    start_date: datetime,
    expected_return_date: datetime,
) -> tuple[bool, str]:
    """Validate the basic rules for a booking request."""

    if quantity < 1:
        return False, "Quantity must be at least 1."

    if quantity > equipment.quantity:
        return False, "Requested quantity exceeds total equipment quantity."

    if equipment.maintenance:
        return False, "Equipment is currently under maintenance."

    if start_date >= expected_return_date:
        return False, "Return date must be after the start date."

    if quantity > equipment.available_quantity:
        return False, "Requested quantity is not currently available."

    return True, ""


def has_booking_conflict(
    equipment_id: int,
    start_date: datetime,
    expected_return_date: datetime,
    exclude_booking_id: int | None = None,
) -> bool:
    """Return True when another non-finalized booking overlaps the dates."""

    query = Booking.query.filter(
        Booking.equipment_id == equipment_id,
        Booking.status.in_(["REQUESTED", "APPROVED", "ACTIVE", "LATE"]),
        Booking.start_date < expected_return_date,
        Booking.expected_return_date > start_date,
    )

    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)

    return query.first() is not None


def can_transition_booking(
    current_status: str,
    new_status: str,
) -> bool:
    """Check whether a booking state transition is allowed."""

    transitions = {
        "REQUESTED": {"APPROVED", "REJECTED", "CANCELLED"},
        "APPROVED": {"ACTIVE", "CANCELLED"},
        "ACTIVE": {"LATE", "RETURNED"},
        "LATE": {"RETURNED"},
        "RETURNED": set(),
        "REJECTED": set(),
        "CANCELLED": set(),
    }

    if current_status not in VALID_BOOKING_STATUSES:
        return False

    if new_status not in VALID_BOOKING_STATUSES:
        return False

    return new_status in transitions[current_status]