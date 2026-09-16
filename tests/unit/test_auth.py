"""Unit tests for app/auth.py's admin_required decorator.

Uses a real Flask request/app context (Flask-Login's current_user is a
context-local proxy) but no database — current_user is monkeypatched
directly rather than logged in through a real session.
"""
from unittest.mock import patch, MagicMock

import pytest
from flask import Flask
from werkzeug.exceptions import Forbidden, Unauthorized

from app.auth import admin_required


@pytest.fixture
def minimal_app():
    app = Flask(__name__)

    @app.route("/protected")
    @admin_required
    def protected():
        return "ok"

    return app


def test_auth001_unauthenticated_user_gets_401(minimal_app):
    fake_user = MagicMock(is_authenticated=False)
    with patch("app.auth.current_user", fake_user):
        client = minimal_app.test_client()
        resp = client.get("/protected")
        assert resp.status_code == 401


def test_auth002_authenticated_non_admin_gets_403(minimal_app):
    fake_user = MagicMock(is_authenticated=True, role="student")
    with patch("app.auth.current_user", fake_user):
        client = minimal_app.test_client()
        resp = client.get("/protected")
        assert resp.status_code == 403


def test_auth003_authenticated_admin_is_allowed_through(minimal_app):
    fake_user = MagicMock(is_authenticated=True, role="admin")
    with patch("app.auth.current_user", fake_user):
        client = minimal_app.test_client()
        resp = client.get("/protected")
        assert resp.status_code == 200
        assert resp.data == b"ok"
