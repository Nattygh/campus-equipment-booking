from datetime import datetime

from app import db
from app.models import Booking, Equipment


# =========================================================
# BOOKING STATES
# =========================================================

REQUESTED = "REQUESTED"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
ACTIVE = "ACTIVE"
LATE = "LATE"
RETURNED = "RETURNED"
CANCELLED = "CANCELLED"


# =========================================================
# VALID STATE TRANSITIONS
# =========================================================

VALID_TRANSITIONS = {

    REQUESTED: {
        APPROVED,
        REJECTED,
        CANCELLED,
    },

    APPROVED: {
        ACTIVE,
        CANCELLED,
    },

    ACTIVE: {
        LATE,
        RETURNED,
    },

    LATE: {
        RETURNED,
    },

    REJECTED: set(),

    RETURNED: set(),

    CANCELLED: set(),
}


# =========================================================
# VALIDATE BOOKING DATES
# =========================================================

def validate_dates(start_date, expected_return_date):
    """
    Validate the requested booking period.

    A booking must have:
        start_date < expected_return_date
    """

    if not start_date or not expected_return_date:
        raise ValueError("Start and return dates are required.")

    if start_date >= expected_return_date:
        raise ValueError(
            "Expected return date must be after the start date."
        )


# =========================================================
# VALIDATE QUANTITY
# =========================================================

def validate_quantity(quantity):
    """
    Validate the requested equipment quantity.
    """

    if quantity is None:
        raise ValueError("Quantity is required.")

    if quantity <= 0:
        raise ValueError(
            "Booking quantity must be greater than zero."
        )


# =========================================================
# CHECK DATE OVERLAP
# =========================================================

def dates_overlap(
    start_a,
    end_a,
    start_b,
    end_b,
):
    """
    Return True when two booking periods overlap.

    Two periods overlap when:

        start_a < end_b
        AND
        end_a > start_b
    """

    return (
        start_a < end_b
        and end_a > start_b
    )


# =========================================================
# FIND OVERLAPPING BOOKINGS
# =========================================================

def get_overlapping_bookings(
    equipment_id,
    start_date,
    expected_return_date,
    exclude_booking_id=None,
):
    """
    Return bookings for the same equipment whose
    booking periods overlap the requested period.

    Rejected and returned bookings do not consume
    equipment capacity. `exclude_booking_id` lets a caller
    re-checking availability for an existing booking (e.g.
    at approval time) exclude that booking from its own
    reserved-quantity count.
    """

    query = Booking.query.filter(
        Booking.equipment_id == equipment_id,
        Booking.status.in_([
            REQUESTED,
            APPROVED,
            ACTIVE,
            LATE,
        ]),
    )

    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)

    bookings = query.all()

    return [
        booking
        for booking in bookings
        if dates_overlap(
            start_date,
            expected_return_date,
            booking.start_date,
            booking.expected_return_date,
        )
    ]


# =========================================================
# CALCULATE RESERVED QUANTITY
# =========================================================

def calculate_reserved_quantity(
    equipment_id,
    start_date,
    expected_return_date,
    exclude_booking_id=None,
):
    """
    Calculate how many units are already reserved
    during the requested period.
    """

    overlapping_bookings = get_overlapping_bookings(
        equipment_id,
        start_date,
        expected_return_date,
        exclude_booking_id=exclude_booking_id,
    )

    return sum(
        booking.quantity
        for booking in overlapping_bookings
    )


# =========================================================
# CHECK EQUIPMENT AVAILABILITY
# =========================================================

def check_availability(
    equipment,
    quantity,
    start_date,
    expected_return_date,
    exclude_booking_id=None,
):
    """
    Determine whether the requested equipment quantity
    is available during the requested period.
    """

    validate_quantity(quantity)

    validate_dates(
        start_date,
        expected_return_date,
    )

    if equipment.maintenance:
        raise ValueError(
            "This equipment is currently under maintenance."
        )

    if quantity > equipment.quantity:
        raise ValueError(
            "Requested quantity exceeds total equipment quantity."
        )

    reserved_quantity = calculate_reserved_quantity(
        equipment.id,
        start_date,
        expected_return_date,
        exclude_booking_id=exclude_booking_id,
    )

    available_quantity = (
        equipment.quantity
        - reserved_quantity
    )

    if quantity > available_quantity:
        raise ValueError(
            "The requested quantity is not available "
            "for the selected period."
        )

    return True


# =========================================================
# CREATE BOOKING
# =========================================================

def create_booking(
    user_id,
    equipment_id,
    quantity,
    start_date,
    expected_return_date,
):
    """
    Create a new booking request.

    New bookings always start in REQUESTED state.
    """

    equipment = db.session.get(
        Equipment,
        equipment_id,
    )

    if equipment is None:
        raise ValueError(
            "Equipment not found."
        )

    check_availability(
        equipment,
        quantity,
        start_date,
        expected_return_date,
    )

    booking = Booking(
        user_id=user_id,
        equipment_id=equipment_id,
        quantity=quantity,
        start_date=start_date,
        expected_return_date=expected_return_date,
        status=REQUESTED,
    )

    db.session.add(booking)

    db.session.commit()

    return booking


# =========================================================
# CHANGE BOOKING STATE
# =========================================================

def transition_booking(
    booking,
    new_status,
):
    """
    Safely transition a booking to a new state.
    """

    current_status = booking.status

    allowed_states = VALID_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed_states:
        raise ValueError(
            f"Invalid booking transition: "
            f"{current_status} -> {new_status}"
        )

    booking.status = new_status

    db.session.commit()

    return booking


# =========================================================
# APPROVE BOOKING
# =========================================================

def approve_booking(booking):
    """
    Approve a requested booking after rechecking
    date-range availability.
    """

    if booking.status != REQUESTED:
        raise ValueError(
            "Only requested bookings can be approved."
        )

    check_availability(
        booking.equipment,
        booking.quantity,
        booking.start_date,
        booking.expected_return_date,
        exclude_booking_id=booking.id,
    )

    booking.status = APPROVED

    db.session.commit()

    return booking


# =========================================================
# REJECT BOOKING
# =========================================================

def reject_booking(booking):
    """
    Reject a requested booking.
    """

    return transition_booking(
        booking,
        REJECTED,
    )


# =========================================================
# ACTIVATE BOOKING
# =========================================================

def activate_booking(booking):
    """
    Activate an approved booking and reduce the
    currently available physical inventory.
    """

    if booking.status != APPROVED:
        raise ValueError(
            "Only approved bookings can be activated."
        )

    equipment = booking.equipment

    if equipment.maintenance:
        raise ValueError(
            "Cannot activate equipment that is under maintenance."
        )

    if booking.quantity > equipment.available_quantity:
        raise ValueError(
            "Not enough physical equipment is currently available."
        )

    equipment.available_quantity -= booking.quantity

    booking.status = ACTIVE

    db.session.commit()

    return booking

# =========================================================
# MARK BOOKING LATE
# =========================================================

def mark_late(
    booking,
    now=None,
):
    """
    Mark an active booking as LATE when its expected
    return date has passed.

    `now` can be supplied by tests as a test double.
    """

    if now is None:
        now = datetime.utcnow()

    if booking.status != ACTIVE:
        raise ValueError(
            "Only active bookings can become late."
        )

    if now <= booking.expected_return_date:
        raise ValueError(
            "Booking is not late yet."
        )

    return transition_booking(
        booking,
        LATE,
    )


# =========================================================
# CANCEL BOOKING
# =========================================================

def cancel_booking(
    booking,
    actor,
    now=None,
):
    """
    Cancel a REQUESTED or APPROVED booking.

    Only the booking's owner or an admin may cancel it, and only
    before the booking's start date (the cancellation deadline).
    `now` can be supplied by tests as a test double.
    """

    if now is None:
        now = datetime.utcnow()

    if not (
        getattr(actor, "is_admin", False)
        or actor.id == booking.user_id
    ):
        raise PermissionError(
            "Only the booking owner or an admin may cancel this booking."
        )

    if now >= booking.start_date:
        raise ValueError(
            "This booking can no longer be cancelled; "
            "the cancellation deadline (the start date) has passed."
        )

    return transition_booking(
        booking,
        CANCELLED,
    )


# =========================================================
# RETURN BOOKING
# =========================================================

def return_booking(
    booking,
    actual_return_date=None,
):
    """
    Return an active or late booking and restore
    physical equipment availability.
    """

    if booking.status not in {
        ACTIVE,
        LATE,
    }:
        raise ValueError(
            "Only active or late bookings can be returned."
        )

    if actual_return_date is None:
        actual_return_date = datetime.utcnow()

    booking.actual_return_date = actual_return_date

    booking.status = RETURNED

    equipment = booking.equipment

    equipment.available_quantity += booking.quantity

    if (
        equipment.available_quantity
        > equipment.quantity
    ):
        equipment.available_quantity = equipment.quantity

    db.session.commit()

    return booking
