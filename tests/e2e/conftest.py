"""Shared fixtures for the Selenium E2E suite."""

import os
import sys
import socket
import threading
import time
import uuid
import urllib.request

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    ),
)


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait_for_server(base_url, timeout=10):
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"{base_url}/login",
                timeout=1,
            ) as response:
                if response.status == 200:
                    return
        except Exception:
            pass

        time.sleep(0.1)

    raise RuntimeError(
        f"Flask test server did not become ready: {base_url}"
    )


@pytest.fixture
def live_server(tmp_path):
    from app import create_app
    from app.extensions import db
    from app.models import User, Equipment
    from werkzeug.security import generate_password_hash

    # Every E2E test gets its own database.
    db_path = tmp_path / f"e2e_{uuid.uuid4().hex}.db"

    port = _free_port()

    app = create_app(
        {
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "TESTING": True,
            "SECRET_KEY": "e2e-test-secret-key",
            "SESSION_COOKIE_SECURE": False,
            "SESSION_COOKIE_SAMESITE": "Lax",
        }
    )

    with app.app_context():
        admin = User(
            username="e2e_admin",
            password_hash=generate_password_hash(
                "AdminPass123!"
            ),
            role="admin",
        )

        student = User(
            username="e2e_student",
            password_hash=generate_password_hash(
                "StudentPass123!"
            ),
            role="student",
        )

        camera = Equipment(
            id=1,
            name="Camera",
            category="Camera",
            quantity=2,
            available_quantity=2,
            maintenance=False,
        )

        maint = Equipment(
            id=2,
            name="Broken Projector",
            category="Projector",
            quantity=1,
            available_quantity=1,
            maintenance=True,
        )

        db.session.add_all(
            [
                admin,
                student,
                camera,
                maint,
            ]
        )

        db.session.commit()

    base_url = f"http://127.0.0.1:{port}"

    thread = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1",
            port=port,
            use_reloader=False,
        ),
        daemon=True,
    )

    thread.start()

    _wait_for_server(base_url)

    yield {
        "base_url": base_url,
        "app": app,
    }

    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    try:
        drv = webdriver.Chrome(options=options)
    except WebDriverException as exc:
        pytest.skip(
            f"No usable browser/driver in this environment: {exc}"
        )

    yield drv

    drv.quit()