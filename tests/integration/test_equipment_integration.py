"""IT-2xx: equipment add/edit integration tests (routes + real DB)."""
from app import db
from app.models import Equipment
from tests.integration.conftest import login


def test_it201_admin_can_add_equipment(client, seeded):
    login(client, "admin1", "AdminPass123!")
    resp = client.post(
        "/equipment/add",
        data={"name": "Projector", "category": "AV", "quantity": "4"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    item = db.session.query(Equipment).filter_by(name="Projector").first()
    assert item is not None
    assert item.quantity == 4
    assert item.available_quantity == 4  # server computes this; form field was removed


def test_it202_student_cannot_add_equipment(client, seeded):
    login(client, "student1", "StudentPass123!")
    resp = client.get("/equipment/add")
    assert resp.status_code == 403


def test_it203_add_equipment_rejects_missing_name(client, seeded):
    login(client, "admin1", "AdminPass123!")
    resp = client.post(
        "/equipment/add",
        data={"name": "", "category": "AV", "quantity": "2"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"name is required" in resp.data


def test_it204_add_equipment_rejects_quantity_below_one(client, seeded):
    login(client, "admin1", "AdminPass123!")
    resp = client.post(
        "/equipment/add",
        data={"name": "Tripod", "category": "Support", "quantity": "0"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert db.session.query(Equipment).filter_by(name="Tripod").first() is None


def test_it205_edit_equipment_preserves_checked_out_count(client, seeded):
    """Editing total quantity should keep (checked-out count) consistent:
    available_quantity = new_quantity - currently_checked_out."""
    camera = seeded["camera"]
    camera.available_quantity = 0  # the 1 unit is currently checked out
    db.session.commit()

    login(client, "admin1", "AdminPass123!")
    resp = client.post(
        f"/equipment/{camera.id}/edit",
        data={"name": "Camera", "category": "Camera", "quantity": "3"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    reloaded = db.session.get(Equipment, camera.id)
    assert reloaded.quantity == 3
    assert reloaded.available_quantity == 2  # 3 total - 1 still checked out


def test_it206_edit_equipment_rejects_quantity_below_checked_out_count(client, seeded):
    camera = seeded["camera"]
    camera.quantity = 5
    camera.available_quantity = 0  # all 5 checked out
    db.session.commit()

    login(client, "admin1", "AdminPass123!")
    resp = client.post(
        f"/equipment/{camera.id}/edit",
        data={"name": "Camera", "category": "Camera", "quantity": "2"},  # below 5 on loan
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"currently on loan" in resp.data
    assert db.session.get(Equipment, camera.id).quantity == 5  # unchanged
