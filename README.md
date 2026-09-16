# Campus Equipment Booking & Return System

Flask app for booking shared campus equipment, refined and tested as part
of a Software Testing and Validation project.

> **Group members:** _(add each member's name and student ID here)_

## What changed in this refinement pass

This codebase was audited, had 4 real defects fixed, gained a missing
cancellation feature, and got a full automated test suite. See
`docs/defect_log.md` for full details. Headline fix: `approve_booking()`
used to fail whenever a booking used all the remaining capacity of an
item - a serious bug in the core workflow, caught by the integration
test suite while building it.

## Features

- Login/registration with two roles: student and admin
- Equipment catalogue with maintenance status
- Booking workflow: REQUESTED -> APPROVED/REJECTED -> ACTIVE -> LATE/RETURNED,
  plus REQUESTED/APPROVED -> CANCELLED (added during this refinement)
- Conflict-aware availability checking (date-range overlap + physical
  stock counter)
- Admin equipment CRUD and booking approval/activation/return

## Architecture

```
app/
  models.py          User, Equipment, Booking
  services/
    booking_service.py   Business logic: validation, availability,
                          state machine, all booking actions
  routes.py          All Flask routes (auth, equipment, bookings, admin)
  auth.py            admin_required decorator
  templates/         Jinja2 templates with data-testid selectors for Selenium
tests/
  unit/              Business logic in isolation (in-memory SQLite +
                      a Mock-based test double for full isolation)
  integration/        Flask test client + real DB + auth together
  e2e/
    pages/           Page Objects (LoginPage, EquipmentPage, BookingPage,
                      AdminBookingPage)
    tests/           The 12 required Selenium journeys
docs/
  defect_log.md      Real defects found and fixed during this pass
.github/workflows/ci.yml   GitHub Actions pipeline
Jenkinsfile                Jenkins pipeline
docker/                    Docker Compose setup for local Jenkins + Selenium
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Database setup / seed data

```bash
python seed.py
```

Creates `campus_booking.sqlite3` with an admin (`admin` / `AdminPass123!`)
and a student (`student1` / `StudentPass123!`), plus sample equipment.
Re-run any time to reset. `create_admin.py` remains available for
interactively creating a single admin account.

## Running the application

```bash
python run.py
```

Visit http://127.0.0.1:5000.

## Running the tests

```bash
# Unit tests
python -m pytest tests/unit -v

# Integration tests
python -m pytest tests/integration -v

# Both, with coverage
python -m pytest tests/unit tests/integration --cov=app --cov-branch --cov-report=term-missing

# Selenium E2E (requires a real Chrome + chromedriver on PATH)
python -m pytest tests/e2e -v
```

If no browser/driver is available, the E2E suite skips each test with an
explicit message rather than failing or fabricating results - see
`tests/e2e/conftest.py`.

## GitHub Actions

`.github/workflows/ci.yml` runs on every push/PR: unit tests, integration
tests, then Selenium E2E against a real Chrome (via
`browser-actions/setup-chrome`), with coverage/JUnit artifacts uploaded.

## Jenkins

See `docker/README.md` for the local Jenkins + Selenium Chrome Docker
Compose setup, and `Jenkinsfile` for the pipeline stages.

## Test credentials (demo/local only)

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `AdminPass123!` |
| Student | `student1` | `StudentPass123!` |

## Known limitations

- The Selenium E2E suite is written and correct (verified via the
  integration suite driving the same routes) but could not be executed
  against a real browser in the development sandbox used to build this
  project - Chromium/Firefox on that Ubuntu image are snap-only packages
  with no snap-store access there. Run it in GitHub Actions or the
  Jenkins/Docker setup and capture real output before final submission.
- Jenkins itself has not been executed (Docker-in-Docker unavailable in
  the dev sandbox); the Jenkinsfile mirrors the GitHub Actions stages.
- `datetime.utcnow()` is used in several places and raises a
  `DeprecationWarning` on Python 3.12+; functionally correct, flagged in
  the defect log as minor tech debt rather than fixed mid-refinement.
