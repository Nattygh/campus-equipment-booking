from datetime import datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app.auth import admin_required
from app.extensions import db
from app.models import Booking, Equipment, User
from app.services.booking_service import (
    ACTIVE,
    APPROVED,
    LATE,
    REQUESTED,
    REJECTED,
    RETURNED,
    approve_booking as service_approve_booking,
    create_booking as service_create_booking,
    mark_late as service_mark_late,
    reject_booking as service_reject_booking,
    return_booking as service_return_booking,
    activate_booking as service_activate_booking,
    cancel_booking as service_cancel_booking,
)


main = Blueprint("main", __name__)


# =========================================================
# HOME
# =========================================================

@main.route("/")
def home():
    return render_template("home.html")


# =========================================================
# REGISTER
# =========================================================

@main.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        if not username:
            flash("Username is required.")
            return render_template("register.html")

        if len(password) < 8:
            flash(
                "Password must be at least 8 characters."
            )
            return render_template("register.html")

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("Username already exists.")
            return render_template("register.html")

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role="student",
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful. Please log in."
        )

        return redirect(url_for("main.login"))

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        user = User.query.filter_by(
            username=username
        ).first()

        if (
            user
            and check_password_hash(
                user.password_hash,
                password,
            )
        ):

            login_user(user)

            return redirect(
                url_for("main.dashboard")
            )

        flash("Invalid username or password.")

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@main.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("main.login")
    )


# =========================================================
# USER / ADMIN DASHBOARD
# =========================================================

@main.route("/dashboard")
@login_required
def dashboard():

    recent_bookings = (
        Booking.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .limit(5)
        .all()
    )

    booking_count = Booking.query.filter_by(
        user_id=current_user.id
    ).count()

    requested_count = Booking.query.filter_by(
        user_id=current_user.id,
        status=REQUESTED,
    ).count()

    user_active_count = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.status.in_([
            ACTIVE,
            LATE,
        ]),
    ).count()

    equipment_count = Equipment.query.count()

    available_equipment_count = Equipment.query.filter(
        Equipment.available_quantity > 0,
        Equipment.maintenance.is_(False),
    ).count()

    if current_user.role == "admin":

        pending_count = Booking.query.filter_by(
            status=REQUESTED
        ).count()

        active_count = Booking.query.filter(
            Booking.status.in_([
                ACTIVE,
                LATE,
            ])
        ).count()

        late_count = Booking.query.filter_by(
            status=LATE
        ).count()

    else:

        pending_count = 0

        active_count = user_active_count

        late_count = Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.status == LATE,
        ).count()

    return render_template(
        "dashboard.html",
        recent_bookings=recent_bookings,
        booking_count=booking_count,
        requested_count=requested_count,
        active_count=active_count,
        equipment_count=equipment_count,
        available_equipment_count=available_equipment_count,
        pending_count=pending_count,
        late_count=late_count,
    )


# =========================================================
# ADMIN TEST
# =========================================================

@main.route("/admin-test")
@admin_required
def admin_test():

    return "<h1>Admin access granted</h1>"


# =========================================================
# EQUIPMENT LIST
# =========================================================

@main.route("/equipment")
@login_required
def equipment_list():

    equipment = (
        Equipment.query
        .order_by(Equipment.name)
        .all()
    )

    return render_template(
        "equipment.html",
        equipment=equipment,
    )


# =========================================================
# ADD EQUIPMENT
# =========================================================

@main.route(
    "/equipment/add",
    methods=["GET", "POST"],
)
@admin_required
def add_equipment():

    if request.method == "POST":

        name = request.form.get(
            "name",
            "",
        ).strip()

        category = request.form.get(
            "category",
            "",
        ).strip()

        try:

            quantity = int(
                request.form.get(
                    "quantity",
                    "0",
                )
            )

        except ValueError:

            flash(
                "Quantity must be a valid number."
            )

            return render_template(
                "equipment_form.html",
                title="Add Equipment",
                equipment=None,
            )

        maintenance = (
            request.form.get("maintenance")
            == "on"
        )

        if not name:

            flash(
                "Equipment name is required."
            )

            return render_template(
                "equipment_form.html",
                title="Add Equipment",
                equipment=None,
            )

        if not category:

            flash(
                "Equipment category is required."
            )

            return render_template(
                "equipment_form.html",
                title="Add Equipment",
                equipment=None,
            )

        if quantity < 1:

            flash(
                "Quantity must be at least 1."
            )

            return render_template(
                "equipment_form.html",
                title="Add Equipment",
                equipment=None,
            )

        item = Equipment(
            name=name,
            category=category,
            quantity=quantity,
            available_quantity=quantity,
            maintenance=maintenance,
        )

        db.session.add(item)
        db.session.commit()

        flash(
            "Equipment added successfully."
        )

        return redirect(
            url_for("main.equipment_list")
        )

    return render_template(
        "equipment_form.html",
        title="Add Equipment",
        equipment=None,
    )


# =========================================================
# EDIT EQUIPMENT
# =========================================================

@main.route(
    "/equipment/<int:equipment_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def edit_equipment(equipment_id):

    equipment = db.session.get(
        Equipment,
        equipment_id,
    )

    if equipment is None:
        return "Equipment not found", 404

    if request.method == "POST":

        name = request.form.get(
            "name",
            "",
        ).strip()

        category = request.form.get(
            "category",
            "",
        ).strip()

        try:

            quantity = int(
                request.form.get(
                    "quantity",
                    "0",
                )
            )

        except ValueError:

            flash(
                "Quantity must be a valid number."
            )

            return render_template(
                "equipment_form.html",
                title="Edit Equipment",
                equipment=equipment,
            )

        maintenance = (
            request.form.get("maintenance")
            == "on"
        )

        if not name:

            flash(
                "Equipment name is required."
            )

            return render_template(
                "equipment_form.html",
                title="Edit Equipment",
                equipment=equipment,
            )

        if not category:

            flash(
                "Equipment category is required."
            )

            return render_template(
                "equipment_form.html",
                title="Edit Equipment",
                equipment=equipment,
            )

        if quantity < 1:

            flash(
                "Quantity must be at least 1."
            )

            return render_template(
                "equipment_form.html",
                title="Edit Equipment",
                equipment=equipment,
            )

        if quantity < equipment.quantity - equipment.available_quantity:

            flash(
                "Quantity cannot be lower than equipment currently on loan."
            )

            return render_template(
                "equipment_form.html",
                title="Edit Equipment",
                equipment=equipment,
            )

        checked_out = (
            equipment.quantity
            - equipment.available_quantity
        )

        equipment.name = name
        equipment.category = category
        equipment.quantity = quantity
        equipment.available_quantity = (
            quantity - checked_out
        )
        equipment.maintenance = maintenance

        db.session.commit()

        flash(
            "Equipment updated successfully."
        )

        return redirect(
            url_for("main.equipment_list")
        )

    return render_template(
        "equipment_form.html",
        title="Edit Equipment",
        equipment=equipment,
    )


# =========================================================
# CREATE BOOKING
# =========================================================

@main.route(
    "/equipment/<int:equipment_id>/book",
    methods=["GET", "POST"],
)
@login_required
def create_booking(equipment_id):

    equipment = db.session.get(
        Equipment,
        equipment_id,
    )

    if equipment is None:
        return "Equipment not found", 404

    if request.method == "POST":

        try:

            quantity = int(
                request.form.get(
                    "quantity",
                    "0",
                )
            )

            start_date = datetime.fromisoformat(
                request.form.get(
                    "start_date",
                    "",
                )
            )

            expected_return_date = datetime.fromisoformat(
                request.form.get(
                    "expected_return_date",
                    "",
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            flash(
                "Please provide valid booking information."
            )

            return render_template(
                "booking_form.html",
                equipment=equipment,
            )

        try:

            service_create_booking(
                user_id=current_user.id,
                equipment_id=equipment.id,
                quantity=quantity,
                start_date=start_date,
                expected_return_date=expected_return_date,
            )

        except ValueError as error:

            flash(str(error))

            return render_template(
                "booking_form.html",
                equipment=equipment,
            )

        flash(
            "Booking request submitted successfully."
        )

        return redirect(
            url_for("main.my_bookings")
        )

    return render_template(
        "booking_form.html",
        equipment=equipment,
    )


# =========================================================
# MY BOOKINGS
# =========================================================

@main.route("/bookings")
@login_required
def my_bookings():

    bookings = (
        Booking.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )

    now = datetime.utcnow()

    for booking in bookings:

        if (
            booking.status == ACTIVE
            and now > booking.expected_return_date
        ):
            try:
                service_mark_late(
                    booking,
                    now=now,
                )
            except ValueError:
                pass

    return render_template(
        "bookings.html",
        bookings=bookings,
    )


# =========================================================
# CANCEL BOOKING (owner or admin)
# =========================================================

@main.route(
    "/bookings/<int:booking_id>/cancel",
    methods=["POST"],
)
@login_required
def cancel_booking(booking_id):

    booking = db.session.get(
        Booking,
        booking_id,
    )

    if booking is None:
        return "Booking not found", 404

    try:

        service_cancel_booking(
            booking,
            current_user,
        )

    except (PermissionError, ValueError) as error:

        flash(str(error))

        return redirect(
            url_for("main.my_bookings")
        )

    flash(
        "Booking cancelled."
    )

    return redirect(
        url_for("main.my_bookings")
    )

# =========================================================
# ADMIN BOOKINGS
# =========================================================

@main.route("/admin/bookings")
@admin_required
def admin_bookings():

    bookings = (
        Booking.query
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )

    return render_template(
        "admin_bookings.html",
        bookings=bookings,
    )


# =========================================================
# APPROVE BOOKING
# =========================================================

@main.route(
    "/admin/bookings/<int:booking_id>/approve",
    methods=["POST"],
)
@admin_required
def approve_booking(booking_id):

    booking = db.session.get(
        Booking,
        booking_id,
    )

    if booking is None:
        return "Booking not found", 404

    try:

        service_approve_booking(
            booking
        )

    except ValueError as error:

        flash(str(error))

        return redirect(
            url_for("main.admin_bookings")
        )

    flash(
        "Booking approved successfully."
    )

    return redirect(
        url_for("main.admin_bookings")
    )


# =========================================================
# REJECT BOOKING
# =========================================================

@main.route(
    "/admin/bookings/<int:booking_id>/reject",
    methods=["POST"],
)
@admin_required
def reject_booking(booking_id):

    booking = db.session.get(
        Booking,
        booking_id,
    )

    if booking is None:
        return "Booking not found", 404

    try:

        service_reject_booking(
            booking
        )

    except ValueError as error:

        flash(str(error))

        return redirect(
            url_for("main.admin_bookings")
        )

    flash(
        "Booking rejected."
    )

    return redirect(
        url_for("main.admin_bookings")
    )


# =========================================================
# ACTIVATE BOOKING
# =========================================================

@main.route(
    "/admin/bookings/<int:booking_id>/activate",
    methods=["POST"],
)
@admin_required
def activate_booking(booking_id):

    booking = db.session.get(
        Booking,
        booking_id,
    )

    if booking is None:
        return "Booking not found", 404

    try:

        service_activate_booking(
            booking
        )

    except ValueError as error:

        flash(str(error))

        return redirect(
            url_for("main.admin_bookings")
        )

    flash(
        "Booking activated successfully."
    )

    return redirect(
        url_for("main.admin_bookings")
    )


# =========================================================
# RETURN BOOKING
# =========================================================

@main.route(
    "/admin/bookings/<int:booking_id>/return",
    methods=["POST"],
)
@admin_required
def return_booking(booking_id):

    booking = db.session.get(
        Booking,
        booking_id,
    )

    if booking is None:
        return "Booking not found", 404

    try:

        service_return_booking(
            booking
        )

    except ValueError as error:

        flash(str(error))

        return redirect(
            url_for("main.admin_bookings")
        )

    flash(
        "Equipment returned successfully."
    )

    return redirect(
        url_for("main.admin_bookings")
    )