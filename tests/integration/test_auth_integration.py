"""IT-1xx: registration, authentication, and authorization integration tests."""
from app import db
from app.models import User
from tests.integration.conftest import login


def test_it101_register_creates_user_with_student_role(client, seeded):
    resp = client.post(
        "/register",
        data={"username": "newstudent", "password": "SomePass123!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    user = db.session.query(User).filter_by(username="newstudent").first()
    assert user is not None
    assert user.role == "student"


def test_it102_register_rejects_short_password(client, seeded):
    resp = client.post(
        "/register",
        data={"username": "shortpw", "password": "short"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert db.session.query(User).filter_by(username="shortpw").first() is None
    assert b"at least 8 characters" in resp.data


def test_it103_register_rejects_duplicate_username(client, seeded):
    resp = client.post(
        "/register",
        data={"username": "student1", "password": "SomePass123!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"already exists" in resp.data


def test_it104_login_succeeds_with_valid_credentials(client, seeded):
    resp = login(client, "student1", "StudentPass123!")
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data or b"CampusEquip" in resp.data


def test_it105_login_fails_with_wrong_password(client, seeded):
    resp = client.post("/login", data={"username": "student1", "password": "wrong"})
    assert resp.status_code == 200
    assert b"Invalid username or password" in resp.data


def test_it106_protected_route_redirects_when_not_logged_in(client, seeded):
    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code == 302


def test_it107_admin_only_route_forbidden_for_student(client, seeded):
    login(client, "student1", "StudentPass123!")
    resp = client.get("/admin/bookings")
    assert resp.status_code == 403


def test_it108_admin_only_route_accessible_for_admin(client, seeded):
    login(client, "admin1", "AdminPass123!")
    resp = client.get("/admin/bookings")
    assert resp.status_code == 200


def test_it109_admin_sidebar_link_visible_for_admin(client, seeded):
    """Regression check for the is_admin bug fixed during this refinement:
    the sidebar must actually show admin links to an admin user."""
    login(client, "admin1", "AdminPass123!")
    resp = client.get("/dashboard")
    assert b'data-testid="nav-admin-bookings"' in resp.data
    assert b'data-testid="nav-add-equipment"' in resp.data


def test_it110_admin_sidebar_link_hidden_for_student(client, seeded):
    login(client, "student1", "StudentPass123!")
    resp = client.get("/dashboard")
    assert b'data-testid="nav-admin-bookings"' not in resp.data


def test_it111_logout_ends_session(client, seeded):
    login(client, "student1", "StudentPass123!")
    client.get("/logout")
    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code == 302
