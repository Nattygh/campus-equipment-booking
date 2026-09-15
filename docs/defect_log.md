# Defect Log

Defects found and fixed while adding the test suite to this codebase.
All were found by actually running the app/tests, not invented.

## DEF-001

| Field | Value |
|---|---|
| Title | Admin sidebar navigation links never render, even for admin users |
| Description | `base.html` checked `current_user.is_admin`, but `User` never defined that attribute (only `role`). `dashboard.html`'s own quick-actions panel correctly checked `role == "admin"`, so the two templates were inconsistent - admins saw their dashboard quick-actions but never the sidebar links. |
| Severity | Medium (UI-only; routes were still protected by `admin_required`, so no security impact, but admins effectively couldn't navigate to admin screens from the sidebar) |
| Priority | High |
| Status | Closed |
| Detected by | Manual reproduction (curl as admin, grepped rendered HTML for expected nav text); regression-tested by `test_it109_admin_sidebar_link_visible_for_admin` |
| Root cause | `app/models.py`: `User` had no `is_admin` property |
| Fix | Added `is_admin` property to `User` (`role == "admin"`) |
| Retest | Pass - IT-109/IT-110 confirm the sidebar now shows/hides correctly for admin/student |

## DEF-002

| Field | Value |
|---|---|
| Title | `approve_booking` always fails when a booking uses all remaining capacity |
| Description | The availability re-check inside `approve_booking` calls `calculate_reserved_quantity`, which counted *all* REQUESTED/APPROVED/ACTIVE/LATE bookings overlapping the period - including the very booking being approved, since it is still REQUESTED at that point. This double-counts the booking against itself, so approval fails whenever the booking's own quantity equals the remaining stock (the single most common case for low-quantity items). |
| Severity | High - this breaks the core approval workflow for any equipment item close to its capacity |
| Priority | High |
| Status | Closed |
| Detected by | `test_it305_full_lifecycle_approve_activate_return` (integration test) - first run failed at the approve step with a real, reproducible `ValueError` |
| Root cause | `get_overlapping_bookings` / `calculate_reserved_quantity` / `check_availability` had no way to exclude a specific booking ID from the reserved-quantity count |
| Fix | Added an `exclude_booking_id` parameter threaded through `get_overlapping_bookings` -> `calculate_reserved_quantity` -> `check_availability`, and `approve_booking` now passes `exclude_booking_id=booking.id` |
| Retest | Pass - full suite (115/115) including the conflict test (`test_ut015_approve_rechecks_availability_and_rejects_conflict`), which still correctly rejects genuine conflicts from other bookings |

## DEF-003

| Field | Value |
|---|---|
| Title | Dead `app/services.py` module conflicting with `app/services/` package |
| Description | Both a `services.py` file and a `services/` package existed in `app/`. Routes only ever imported from the package; the loose file was orphaned dead code and a latent import-ambiguity risk. |
| Severity | Low |
| Priority | Medium |
| Status | Closed |
| Fix | Removed `app/services.py` and the unused legacy compatibility shims in `services/__init__.py` after confirming (via grep) nothing referenced them |

## DEF-004

| Field | Value |
|---|---|
| Title | Equipment form exposed a non-functional "Available Quantity" field |
| Description | `equipment_form.html` let an admin type a value into an "Available Quantity" input, but `add_equipment`/`edit_equipment` never read that field from the submitted form - the server always computed it itself. The field was misleading UI with no effect. |
| Severity | Low |
| Priority | Low |
| Status | Closed |
| Fix | Removed the field from the template; confirmed via `test_it201_admin_can_add_equipment` that available_quantity is still computed correctly server-side |

## Missing feature (not a defect - closed as an enhancement)

The brief requires `REQUESTED->CANCELLED` and `APPROVED->CANCELLED` as
valid state transitions with a cancellation deadline. This codebase had no
cancellation feature at all - no route, no service function, `CANCELLED`
absent from the transition table. Added: `cancel_booking()` (owner-or-admin
permission check, deadline enforcement), the `/bookings/<id>/cancel`
route, and a Cancel button in the UI. Covered by UT-028 through UT-033,
IT-307 through IT-309, and E2E-008/E2E-011.

## Summary

| Status | Count |
|---|---|
| Closed | 4 defects + 1 missing feature added |
| Open | 0 |

| Severity | Count |
|---|---|
| High | 1 (DEF-002) |
| Medium | 1 (DEF-001) |
| Low | 2 (DEF-003, DEF-004) |

## Known tech debt (not fixed, flagged for transparency)

`datetime.utcnow()` is used throughout `routes.py` and `booking_service.py`;
functionally correct on Python 3.12 but raises a `DeprecationWarning`
(scheduled for removal in a future Python version). Not fixed here since
it doesn't affect any test result or business behavior.
