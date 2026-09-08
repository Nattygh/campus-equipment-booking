from .booking_service import (
    REQUESTED,
    APPROVED,
    REJECTED,
    ACTIVE,
    LATE,
    RETURNED,
    VALID_TRANSITIONS,
    validate_dates,
    validate_quantity,
    dates_overlap,
    get_overlapping_bookings,
    calculate_reserved_quantity,
    check_availability,
    create_booking,
    transition_booking,
    approve_booking,
    reject_booking,
    activate_booking,
    mark_late,
    return_booking,
)


def validate_booking(
    equipment,
    quantity,
    start_date,
    expected_return_date,
):
    """
    Backward-compatible validation function used by the
    existing Flask routes.

    It validates the booking request and checks equipment
    availability without creating the booking.
    """

    return check_availability(
        equipment,
        quantity,
        start_date,
        expected_return_date,
    )


def has_booking_conflict(
    equipment,
    start_date,
    expected_return_date,
    quantity,
):
    """
    Check whether the requested booking conflicts with
    existing reservations.

    Returns True when the requested quantity cannot be
    accommodated during the requested period.
    """

    if equipment.maintenance:
        return True

    validate_quantity(quantity)

    validate_dates(
        start_date,
        expected_return_date,
    )

    if quantity > equipment.quantity:
        return True

    reserved_quantity = calculate_reserved_quantity(
        equipment.id,
        start_date,
        expected_return_date,
    )

    available_quantity = (
        equipment.quantity
        - reserved_quantity
    )

    return quantity > available_quantity

