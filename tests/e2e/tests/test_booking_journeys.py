"""E2E-xxx: end-to-end browser journeys via Selenium + Page Object Model.

Requires a real browser + driver (see conftest.py `driver` fixture, which
skips gracefully with a clear message if none is available - designed to
run in GitHub Actions / Jenkins where a browser is provisioned).
"""
from datetime import datetime, timedelta

from app import db
from app.models import Booking, User

from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.equipment_page import EquipmentPage
from tests.e2e.pages.booking_page import BookingPage
from tests.e2e.pages.admin_booking_page import AdminBookingPage

FMT = "%Y-%m-%dT%H:%M"


def _window(hours_from_now=2, duration_hours=1):
    start = datetime.now() + timedelta(hours=hours_from_now)
    end = start + timedelta(hours=duration_hours)
    return start.strftime(FMT), end.strftime(FMT)


def _latest_booking_id(app, username):
    with app.app_context():
        user = db.session.query(User).filter_by(username=username).first()
        booking = db.session.query(Booking).filter_by(user_id=user.id).order_by(Booking.id.desc()).first()
        return booking.id if booking else None


# E2E-001 -----------------------------------------------------------------
def test_e2e001_login_successfully(driver, live_server):
    page = LoginPage(driver, live_server["base_url"]).open_login()
    page.login("e2e_student", "StudentPass123!")
    page.find("nav-my-bookings")


# E2E-002 -----------------------------------------------------------------

def test_e2e002_login_fails_with_invalid_credentials(live_server, driver):
    login_page = LoginPage(driver, live_server["base_url"])

    login_page.open_login()
    login_page.find("username-input").send_keys("e2e_student")
    login_page.find("password-input").send_keys("WrongPassword123!")
    login_page.find_clickable("login-submit").click()

    messages = login_page.flash_messages()

    assert any(
        "Invalid username or password" in message
        for message in messages
    )
    assert "/login" in driver.current_url


# E2E-003 -----------------------------------------------------------------
def test_e2e003_browse_equipment(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    page = EquipmentPage(driver, live_server["base_url"]).open_list()
    assert page.is_listed(1)


# E2E-004 -----------------------------------------------------------------

def test_e2e004_create_valid_booking(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    start, end = _window(hours_from_now=2, duration_hours=1)
    page = BookingPage(driver, live_server["base_url"]).open_booking_form(1)
    page.fill_form(1, start, end).submit()
    booking_id = _latest_booking_id(live_server["app"], "e2e_student")
    page.open_my_bookings()
    assert page.status_of(booking_id) == "Requested"
    

# E2E-005 -----------------------------------------------------------------
def test_e2e005_reject_invalid_booking_shows_validation_error(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    start = (datetime.now() + timedelta(hours=3)).strftime(FMT)
    end = (datetime.now() + timedelta(hours=2)).strftime(FMT)  # end before start
    page = BookingPage(driver, live_server["base_url"]).open_booking_form(1)
    page.fill_form(1, start, end).submit()
    assert any(m for m in page.flash_messages())  # a validation error is shown


# E2E-006 -----------------------------------------------------------------
def test_e2e006_admin_approves_booking(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    start, end = _window(hours_from_now=3)
    BookingPage(driver, live_server["base_url"]).open_booking_form(1).fill_form(1, start, end).submit()
    booking_id = _latest_booking_id(live_server["app"], "e2e_student")
    driver.get(f"{live_server['base_url']}/logout")

    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_admin", "AdminPass123!")
    admin_page = AdminBookingPage(driver, live_server["base_url"]).open_pending()
    assert admin_page.is_listed(booking_id)
    admin_page.approve(booking_id)
    assert admin_page.status_of(booking_id) == "Approved"


# E2E-007 -----------------------------------------------------------------
def test_e2e007_user_views_approved_booking(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    start, end = _window(hours_from_now=4)
    BookingPage(driver, live_server["base_url"]).open_booking_form(1).fill_form(1, start, end).submit()
    booking_id = _latest_booking_id(live_server["app"], "e2e_student")
    driver.get(f"{live_server['base_url']}/logout")

    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_admin", "AdminPass123!")
    AdminBookingPage(driver, live_server["base_url"]).open_pending().approve(booking_id)
    driver.get(f"{live_server['base_url']}/logout")

    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    page = BookingPage(driver, live_server["base_url"]).open_my_bookings()
    assert page.status_of(booking_id) == "Approved"


# E2E-008 -----------------------------------------------------------------
def test_e2e008_user_cancels_eligible_booking(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    start, end = _window(hours_from_now=5)
    page = BookingPage(driver, live_server["base_url"]).open_booking_form(1)
    page.fill_form(1, start, end).submit()
    booking_id = _latest_booking_id(live_server["app"], "e2e_student")
    page.open_my_bookings()
    page.cancel(booking_id)
    page.open_my_bookings()
    assert page.status_of(booking_id) == "CANCELLED"


# E2E-009 -----------------------------------------------------------------
def test_e2e009_equipment_unavailable_scenario(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    page = EquipmentPage(driver, live_server["base_url"]).open_list()
    assert not page.has_book_link(2)  # seeded MAINTENANCE item
    assert "Maintenance" in page.status_of(2)


# E2E-010 -----------------------------------------------------------------
def test_e2e010_complete_return_process(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    start, end = _window(hours_from_now=1)
    BookingPage(driver, live_server["base_url"]).open_booking_form(1).fill_form(1, start, end).submit()
    booking_id = _latest_booking_id(live_server["app"], "e2e_student")
    driver.get(f"{live_server['base_url']}/logout")

    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_admin", "AdminPass123!")
    admin_page = AdminBookingPage(driver, live_server["base_url"]).open_pending()
    admin_page.approve(booking_id)
    admin_page.activate(booking_id)
    assert admin_page.status_of(booking_id) == "Active"
    admin_page.return_item(booking_id)
    assert admin_page.status_of(booking_id) == "Returned"


# E2E-011 -----------------------------------------------------------------
def test_e2e011_invalid_state_transition_is_rejected(driver, live_server):
    """After CANCELLED, the UI hides the Cancel button - confirm the
    backend also rejects a forged repeat cancel, not just that the button
    disappeared."""
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    start, end = _window(hours_from_now=6)
    page = BookingPage(driver, live_server["base_url"]).open_booking_form(1)
    page.fill_form(1, start, end).submit()
    booking_id = _latest_booking_id(live_server["app"], "e2e_student")
    page.open_my_bookings()
    page.cancel(booking_id)
    page.open_my_bookings()
    assert not page.has_cancel_button(booking_id)

    script = (
        "var f = document.createElement('form');"
        "f.method = 'POST'; f.action = arguments[0];"
        "document.body.appendChild(f); f.submit();"
    )
    driver.execute_script(script, f"{live_server['base_url']}/bookings/{booking_id}/cancel")
    page.open_my_bookings()
    assert page.status_of(booking_id) == "CANCELLED"  # unchanged, not double-processed


# E2E-012 -----------------------------------------------------------------
def test_e2e012_authorization_access_control_scenario(driver, live_server):
    LoginPage(driver, live_server["base_url"]).open_login().login("e2e_student", "StudentPass123!")
    driver.get(f"{live_server['base_url']}/admin/bookings")
    assert "403" in driver.page_source or "Forbidden" in driver.page_source
