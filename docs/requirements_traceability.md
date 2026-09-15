# Requirements Traceability Matrix (RTM)
## Campus Equipment Booking & Return System

**Author:** Mihiret Girum — REQUIREMENTS & TEST PLANNING  
**Course:** Software Testing and Validation - Addis Ababa University  
**Project:** Campus Equipment Booking & Return System Refinement  

---

## 1. Overview & Verification Summary

This document establishes bidirectional traceability between the functional requirements specified in `docs/requirements.md` and the automated test suite in `tests/`. 

Every test listed corresponds to a concrete, implemented test function in the repository. Statuses reflect **actual test execution results** executed via `pytest`:
- **Unit & Integration Suite (115 tests)**: **100% Executed & Passed** (88 Unit Tests + 27 Integration Tests).
- **End-to-End Suite (12 tests)**: **Blocked / Pending CI Environment** (tests are fully implemented using the Page Object Model, ready to execute in GitHub Actions / Docker with headless Chrome; local environment lacks Chrome/Chromium binaries).

---

## 2. Requirements Traceability Matrix

| Requirement ID | Requirement Description | Test ID | Test Level | Test Method / File | Expected Result | Execution Status |
|---|---|---|---|---|---|---|
| **REQ-001** | User Registration: unique username, password >= 8 chars, default role student | IT-101 | Integration | `test_it101_register_creates_user_with_student_role`<br>`tests/integration/test_auth_integration.py` | Valid registration creates user in DB with role 'student' and redirects to login | **PASSED** |
| **REQ-001** | User Registration: password validation | IT-102 | Integration | `test_it102_register_rejects_short_password`<br>`tests/integration/test_auth_integration.py` | Password shorter than 8 chars rejected with flash error message | **PASSED** |
| **REQ-001** | User Registration: duplicate username prevention | IT-103 | Integration | `test_it103_register_rejects_duplicate_username`<br>`tests/integration/test_auth_integration.py` | Duplicate username registration rejected with flash error message | **PASSED** |
| **REQ-002** | User Login: valid credentials authentication | IT-104 | Integration | `test_it104_login_succeeds_with_valid_credentials`<br>`tests/integration/test_auth_integration.py` | Valid username/password logs user in and redirects to dashboard | **PASSED** |
| **REQ-002** | User Login: invalid credentials rejection | IT-105 | Integration | `test_it105_login_fails_with_wrong_password`<br>`tests/integration/test_auth_integration.py` | Incorrect password rejected with flash error message; remains unauthenticated | **PASSED** |
| **REQ-002** | User Login: browser login journey | E2E-001 | E2E (System) | `test_e2e001_login_successfully`<br>`tests/e2e/tests/test_booking_journeys.py` | User logs in via UI form and navigates to dashboard | **BLOCKED** *(Pending CI)* |
| **REQ-002** | User Login: browser invalid login error | E2E-002 | E2E (System) | `test_e2e002_login_fails_with_invalid_credentials`<br>`tests/e2e/tests/test_booking_journeys.py` | Form submission with invalid password displays UI error alert | **BLOCKED** *(Pending CI)* |
| **REQ-003** | User Logout: session termination | IT-111 | Integration | `test_it111_logout_ends_session`<br>`tests/integration/test_auth_integration.py` | Accessing /logout terminates session and redirects to login | **PASSED** |
| **REQ-004** | Role Authorization: unauthenticated access protected route | AUTH-001 | Unit | `test_auth001_unauthenticated_user_gets_401`<br>`tests/unit/test_auth.py` | Unauthenticated user accessing @admin_required route receives 401 | **PASSED** |
| **REQ-004** | Role Authorization: student accessing admin route | AUTH-002 | Unit | `test_auth002_authenticated_non_admin_gets_403`<br>`tests/unit/test_auth.py` | Authenticated student accessing @admin_required route receives 403 | **PASSED** |
| **REQ-004** | Role Authorization: admin accessing admin route | AUTH-003 | Unit | `test_auth003_authenticated_admin_is_allowed_through`<br>`tests/unit/test_auth.py` | Authenticated admin accessing @admin_required route receives 200 OK | **PASSED** |
| **REQ-004** | Role Authorization: unauthenticated redirect | IT-106 | Integration | `test_it106_protected_route_redirects_when_not_logged_in`<br>`tests/integration/test_auth_integration.py` | Anonymous request to protected route redirects to login | **PASSED** |
| **REQ-004** | Role Authorization: student forbidden from admin endpoints | IT-107 | Integration | `test_it107_admin_only_route_forbidden_for_student`<br>`tests/integration/test_auth_integration.py` | Student accessing admin route receives 403 Forbidden | **PASSED** |
| **REQ-004** | Role Authorization: admin allowed access | IT-108 | Integration | `test_it108_admin_only_route_accessible_for_admin`<br>`tests/integration/test_auth_integration.py` | Admin accessing admin route receives 200 OK | **PASSED** |
| **REQ-004** | Role Authorization: admin sidebar visibility (DEF-001 regression) | IT-109 | Integration | `test_it109_admin_sidebar_link_visible_for_admin`<br>`tests/integration/test_auth_integration.py` | Admin user sees admin links in sidebar navigation | **PASSED** |
| **REQ-004** | Role Authorization: student sidebar hides admin link | IT-110 | Integration | `test_it110_admin_sidebar_link_hidden_for_student`<br>`tests/integration/test_auth_integration.py` | Student user does not see admin sidebar links | **PASSED** |
| **REQ-004** | Role Authorization: E2E access control | E2E-012 | E2E (System) | `test_e2e012_authorization_access_control_scenario`<br>`tests/e2e/tests/test_booking_journeys.py` | Student browser session forbidden from loading admin screens | **BLOCKED** *(Pending CI)* |
| **REQ-005** | Dashboards: student and admin metrics display | IT-108, IT-109 | Integration | `test_it108_admin_only_route_accessible_for_admin`<br>`test_it109_admin_sidebar_link_visible_for_admin` | Dashboard renders correct operational statistics and navigation links | **PASSED** |
| **REQ-006** | Equipment Browsing: catalogue display | IT-201 | Integration | `test_it201_admin_can_add_equipment`<br>`tests/integration/test_equipment_integration.py` | Added equipment appears in catalogue with quantity and status | **PASSED** |
| **REQ-006** | Equipment Browsing: browser catalogue view | E2E-003 | E2E (System) | `test_e2e003_browse_equipment`<br>`tests/e2e/tests/test_booking_journeys.py` | Student browses equipment catalogue and views available items | **BLOCKED** *(Pending CI)* |
| **REQ-007** | Equipment Creation: admin creates item | IT-201 | Integration | `test_it201_admin_can_add_equipment`<br>`tests/integration/test_equipment_integration.py` | Admin adds equipment successfully; stock recorded in DB | **PASSED** |
| **REQ-007** | Equipment Creation: student denied addition | IT-202 | Integration | `test_it202_student_cannot_add_equipment`<br>`tests/integration/test_equipment_integration.py` | Student attempt to add equipment receives 403 Forbidden | **PASSED** |
| **REQ-007** | Equipment Creation: name required | IT-203 | Integration | `test_it203_add_equipment_rejects_missing_name`<br>`tests/integration/test_equipment_integration.py` | Submitting equipment without name rejected with flash message | **PASSED** |
| **REQ-007** | Equipment Creation: positive quantity required | IT-204 | Integration | `test_it204_add_equipment_rejects_quantity_below_one`<br>`tests/integration/test_equipment_integration.py` | Submitting equipment with quantity < 1 rejected | **PASSED** |
| **REQ-008** | Equipment Modification: edit preserves checked-out units | IT-205 | Integration | `test_it205_edit_equipment_preserves_checked_out_count`<br>`tests/integration/test_equipment_integration.py` | Total quantity update preserves checked-out units calculation | **PASSED** |
| **REQ-008** | Equipment Modification: cannot reduce below checked-out | IT-206 | Integration | `test_it206_edit_equipment_rejects_quantity_below_checked_out_count`<br>`tests/integration/test_equipment_integration.py` | Reducing total quantity below currently active loans rejected | **PASSED** |
| **REQ-009** | Date Validation: missing start date | EP-001 | Unit | `test_ep001_missing_start_date_raises`<br>`tests/unit/test_validation.py` | `validate_dates(None, end)` raises ValueError | **PASSED** |
| **REQ-009** | Date Validation: missing end date | EP-002 | Unit | `test_ep002_missing_end_date_raises`<br>`tests/unit/test_validation.py` | `validate_dates(start, None)` raises ValueError | **PASSED** |
| **REQ-009** | Date Validation: start date equals end date | EP-003 | Unit | `test_ep003_start_equal_to_end_raises`<br>`tests/unit/test_validation.py` | `validate_dates(now, now)` raises ValueError | **PASSED** |
| **REQ-009** | Date Validation: start date after end date | EP-004 | Unit | `test_ep004_start_after_end_raises`<br>`tests/unit/test_validation.py` | `validate_dates(end, start)` raises ValueError | **PASSED** |
| **REQ-009** | Date Validation: valid date range accepted | EP-005 | Unit | `test_ep005_end_after_start_is_accepted`<br>`tests/unit/test_validation.py` | Valid start and end dates pass without exception | **PASSED** |
| **REQ-009** | Quantity Validation: None quantity raises | EP-006 | Unit | `test_ep006_none_quantity_raises`<br>`tests/unit/test_validation.py` | `validate_quantity(None)` raises ValueError | **PASSED** |
| **REQ-009** | Quantity Validation: zero quantity raises | EP-007 | Unit | `test_ep007_zero_quantity_raises`<br>`tests/unit/test_validation.py` | `validate_quantity(0)` raises ValueError | **PASSED** |
| **REQ-009** | Quantity Validation: negative quantity raises | EP-008 | Unit | `test_ep008_negative_quantity_raises`<br>`tests/unit/test_validation.py` | `validate_quantity(-1)` raises ValueError | **PASSED** |
| **REQ-009** | Quantity Validation: quantity of 1 accepted (BVA) | BVA-001 | Unit | `test_bva001_quantity_of_one_is_accepted`<br>`tests/unit/test_validation.py` | Minimum valid boundary (1) passes without exception | **PASSED** |
| **REQ-009** | Quantity Validation: positive quantity accepted | EP-009 | Unit | `test_ep009_positive_quantity_is_accepted`<br>`tests/unit/test_validation.py` | Positive quantity (5) passes without exception | **PASSED** |
| **REQ-009** | Booking Creation: creates DB record in REQUESTED status | IT-301 | Integration | `test_it301_submit_booking_creates_row`<br>`tests/integration/test_booking_integration.py` | Booking row created in DB with status REQUESTED | **PASSED** |
| **REQ-009** | Booking Creation: invalid dates rejected | IT-303 | Integration | `test_it303_booking_invalid_dates_rejected`<br>`tests/integration/test_booking_integration.py` | Form submission with return <= start date flashes validation error | **PASSED** |
| **REQ-009** | Booking Creation: browser valid booking journey | E2E-004 | E2E (System) | `test_e2e004_create_valid_booking`<br>`tests/e2e/tests/test_booking_journeys.py` | User submits booking form; row appears in My Bookings | **BLOCKED** *(Pending CI)* |
| **REQ-009** | Booking Creation: browser invalid booking validation | E2E-005 | E2E (System) | `test_e2e005_reject_invalid_booking_shows_validation_error`<br>`tests/e2e/tests/test_booking_journeys.py` | Submitting invalid date in browser shows error message | **BLOCKED** *(Pending CI)* |
| **REQ-010** | Date Overlap: identical windows overlap | ST-001 | Unit | `test_st001_identical_windows_overlap`<br>`tests/unit/test_validation.py` | Identical time windows return True | **PASSED** |
| **REQ-010** | Date Overlap: disjoint windows do not overlap | ST-002 | Unit | `test_st002_disjoint_windows_do_not_overlap`<br>`tests/unit/test_validation.py` | Disjoint time windows return False | **PASSED** |
| **REQ-010** | Date Overlap: adjacent windows do not overlap | ST-003 | Unit | `test_st003_adjacent_windows_do_not_overlap`<br>`tests/unit/test_validation.py` | Touching boundary (start_b == end_a) returns False (half-open) | **PASSED** |
| **REQ-010** | Date Overlap: partial overlap detected | ST-004 | Unit | `test_st004_partial_overlap_is_detected`<br>`tests/unit/test_validation.py` | Partially overlapping intervals return True | **PASSED** |
| **REQ-010** | Date Overlap: fully contained window overlaps | ST-005 | Unit | `test_st005_fully_contained_window_overlaps`<br>`tests/unit/test_validation.py` | Fully nested intervals return True | **PASSED** |
| **REQ-010** | Availability: zero reservations when empty | UT-001 | Unit | `test_ut001_no_bookings_full_quantity_available`<br>`tests/unit/test_booking_service.py` | Reserved quantity equals 0 with no existing bookings | **PASSED** |
| **REQ-010** | Availability: overlapping booking increases reserved | UT-002 | Unit | `test_ut002_overlapping_booking_increases_reserved_quantity`<br>`tests/unit/test_booking_service.py` | Overlapping booking adds to reserved count | **PASSED** |
| **REQ-010** | Availability: non-overlapping booking not counted | UT-003 | Unit | `test_ut003_non_overlapping_booking_does_not_count`<br>`tests/unit/test_booking_service.py` | Adjacent/non-overlapping booking does not consume stock | **PASSED** |
| **REQ-010** | Availability: CANCELLED booking releases capacity | UT-004 | Unit | `test_ut004_cancelled_booking_does_not_reserve_stock`<br>`tests/unit/test_booking_service.py` | CANCELLED booking contributes 0 to reserved stock | **PASSED** |
| **REQ-010** | Availability: REJECTED booking releases capacity | UT-005 | Unit | `test_ut005_rejected_booking_does_not_reserve_stock`<br>`tests/unit/test_booking_service.py` | REJECTED booking contributes 0 to reserved stock | **PASSED** |
| **REQ-010** | Availability: stock sufficient returns True | UT-006 | Unit | `test_ut006_check_availability_true_when_stock_sufficient`<br>`tests/unit/test_booking_service.py` | `check_availability()` returns True when capacity available | **PASSED** |
| **REQ-010** | Availability: requested exceeds total capacity | UT-007 | Unit | `test_ut007_check_availability_raises_when_quantity_exceeds_stock`<br>`tests/unit/test_booking_service.py` | Raises ValueError when quantity > equipment total quantity | **PASSED** |
| **REQ-010** | Availability: under maintenance raises error | UT-008 | Unit | `test_ut008_check_availability_raises_under_maintenance`<br>`tests/unit/test_booking_service.py` | Raises ValueError if `equipment.maintenance == True` | **PASSED** |
| **REQ-010** | Availability: stock reserved by others raises error | UT-009 | Unit | `test_ut009_check_availability_raises_when_reserved_by_others`<br>`tests/unit/test_booking_service.py` | Raises ValueError if remaining available stock is insufficient | **PASSED** |
| **REQ-010** | Availability: DB-isolated query mocking | UT-ISO-01 | Unit | `test_ut_isolated_001_filters_using_mocked_query_no_database`<br>`tests/unit/test_booking_service_isolated.py` | Verifies overlap filter logic via unittest.mock test double | **PASSED** |
| **REQ-010** | Availability: maintenance equipment rejected in route | IT-302 | Integration | `test_it302_booking_maintenance_equipment_rejected`<br>`tests/integration/test_booking_integration.py` | Booking attempt for maintenance equipment flashes error | **PASSED** |
| **REQ-010** | Availability: second conflicting booking rejected | IT-304 | Integration | `test_it304_second_conflicting_booking_rejected`<br>`tests/integration/test_booking_integration.py` | Second booking for overlapping window exceeding stock rejected | **PASSED** |
| **REQ-010** | Availability: browser equipment unavailable scenario | E2E-009 | E2E (System) | `test_e2e009_equipment_unavailable_scenario`<br>`tests/e2e/tests/test_booking_journeys.py` | UI blocks booking when stock unavailable for chosen period | **BLOCKED** *(Pending CI)* |
| **REQ-011** | Booking Approval: valid approval succeeds (DEF-002 fix) | UT-013 | Unit | `test_ut013_approve_requested_booking_succeeds`<br>`tests/unit/test_booking_service.py` | REQUESTED booking moves to APPROVED; no self-double-counting | **PASSED** |
| **REQ-011** | Booking Approval: non-requested booking raises error | UT-014 | Unit | `test_ut014_approve_non_requested_booking_raises`<br>`tests/unit/test_booking_service.py` | Attempting to approve non-REQUESTED booking raises ValueError | **PASSED** |
| **REQ-011** | Booking Approval: re-checks availability for conflicts | UT-015 | Unit | `test_ut015_approve_rechecks_availability_and_rejects_conflict`<br>`tests/unit/test_booking_service.py` | Conflicting overlapping booking causes approval to raise ValueError | **PASSED** |
| **REQ-011** | Booking Approval: lifecycle approval integration | IT-305 | Integration | `test_it305_full_lifecycle_approve_activate_return`<br>`tests/integration/test_booking_integration.py` | Admin approves booking; status changes to APPROVED | **PASSED** |
| **REQ-011** | Booking Approval: browser admin approval | E2E-006 | E2E (System) | `test_e2e006_admin_approves_booking`<br>`tests/e2e/tests/test_booking_journeys.py` | Admin clicks approve in UI; status badge updates to APPROVED | **BLOCKED** *(Pending CI)* |
| **REQ-011** | Booking Approval: student views approved status | E2E-007 | E2E (System) | `test_e2e007_user_views_approved_booking`<br>`tests/e2e/tests/test_booking_journeys.py` | Student sees APPROVED badge on My Bookings page | **BLOCKED** *(Pending CI)* |
| **REQ-012** | Booking Rejection: admin rejects requested booking | UT-016 | Unit | `test_ut016_reject_requested_booking_succeeds`<br>`tests/unit/test_booking_service.py` | Booking transitions to REJECTED | **PASSED** |
| **REQ-012** | Booking Rejection: route integration | IT-306 | Integration | `test_it306_admin_can_reject_booking`<br>`tests/integration/test_booking_integration.py` | Admin rejects booking via POST; status in DB becomes REJECTED | **PASSED** |
| **REQ-013** | Handover & Activation: approved booking activates | UT-017 | Unit | `test_ut017_activate_approved_booking_reduces_available_quantity`<br>`tests/unit/test_booking_service.py` | Booking becomes ACTIVE; equipment.available_quantity decremented | **PASSED** |
| **REQ-013** | Handover & Activation: non-approved booking raises | UT-018 | Unit | `test_ut018_activate_non_approved_booking_raises`<br>`tests/unit/test_booking_service.py` | Activating non-APPROVED booking raises ValueError | **PASSED** |
| **REQ-013** | Handover & Activation: maintenance prevents activation | UT-019 | Unit | `test_ut019_activate_raises_when_equipment_under_maintenance`<br>`tests/unit/test_booking_service.py` | Activation raises ValueError if equipment under maintenance | **PASSED** |
| **REQ-013** | Handover & Activation: insufficient physical stock | UT-020 | Unit | `test_ut020_activate_raises_when_physical_stock_insufficient`<br>`tests/unit/test_booking_service.py` | Activation raises ValueError if available_quantity < booking.quantity | **PASSED** |
| **REQ-013** | Handover & Activation: integration lifecycle | IT-305 | Integration | `test_it305_full_lifecycle_approve_activate_return`<br>`tests/integration/test_booking_integration.py` | Admin activates booking; status becomes ACTIVE and stock decrements | **PASSED** |
| **REQ-014** | Late Tracking: past due active booking becomes late | UT-021 | Unit | `test_ut021_mark_late_transitions_active_past_due_booking`<br>`tests/unit/test_booking_service.py` | Active booking past expected return date moves to LATE | **PASSED** |
| **REQ-014** | Late Tracking: non-active booking raises error | UT-022 | Unit | `test_ut022_mark_late_raises_for_non_active_booking`<br>`tests/unit/test_booking_service.py` | Calling mark_late on non-ACTIVE booking raises ValueError | **PASSED** |
| **REQ-014** | Late Tracking: not late yet raises error | UT-023 | Unit | `test_ut023_mark_late_raises_when_not_yet_late`<br>`tests/unit/test_booking_service.py` | Calling mark_late before return date raises ValueError | **PASSED** |
| **REQ-014** | Late Tracking: automatic transition on My Bookings load | IT-310 | Integration | `test_it310_my_bookings_auto_flags_late`<br>`tests/integration/test_booking_integration.py` | Loading /bookings automatically marks past-due active loans as LATE | **PASSED** |
| **REQ-015** | Equipment Return: active booking returns successfully | UT-024 | Unit | `test_ut024_return_active_booking_succeeds`<br>`tests/unit/test_booking_service.py` | Status becomes RETURNED; sets return date; increments stock | **PASSED** |
| **REQ-015** | Equipment Return: late booking returns successfully | UT-025 | Unit | `test_ut025_return_late_booking_succeeds`<br>`tests/unit/test_booking_service.py` | LATE booking transitions to RETURNED and restores inventory | **PASSED** |
| **REQ-015** | Equipment Return: non-active/non-late booking raises | UT-026 | Unit | `test_ut026_return_non_active_non_late_booking_raises`<br>`tests/unit/test_booking_service.py` | Attempting to return REQUESTED/APPROVED raises ValueError | **PASSED** |
| **REQ-015** | Equipment Return: inventory capped at total | UT-027 | Unit | `test_ut027_return_never_pushes_available_quantity_above_total`<br>`tests/unit/test_booking_service.py` | Available quantity never exceeds total equipment quantity | **PASSED** |
| **REQ-015** | Equipment Return: integration lifecycle return | IT-305 | Integration | `test_it305_full_lifecycle_approve_activate_return`<br>`tests/integration/test_booking_integration.py` | Full flow: Return sets status RETURNED and restores inventory | **PASSED** |
| **REQ-015** | Equipment Return: browser return process | E2E-010 | E2E (System) | `test_e2e010_complete_return_process`<br>`tests/e2e/tests/test_booking_journeys.py` | Admin processes return via UI; available stock restored | **BLOCKED** *(Pending CI)* |
| **REQ-016** | Booking Cancellation: owner cancels before start | UT-028 | Unit | `test_ut028_owner_can_cancel_before_start`<br>`tests/unit/test_booking_service.py` | Owner student cancels REQUESTED booking prior to start date | **PASSED** |
| **REQ-016** | Booking Cancellation: admin cancels student's booking | UT-029 | Unit | `test_ut029_admin_can_cancel_someone_elses_booking`<br>`tests/unit/test_booking_service.py` | Admin cancels any student's eligible booking before start date | **PASSED** |
| **REQ-016** | Booking Cancellation: unauthorized student rejected | UT-030 | Unit | `test_ut030_other_student_cannot_cancel`<br>`tests/unit/test_booking_service.py` | Other student receives PermissionError attempting cancellation | **PASSED** |
| **REQ-016** | Booking Cancellation: past start time rejected | UT-031 | Unit | `test_ut031_cannot_cancel_after_start_time`<br>`tests/unit/test_booking_service.py` | Cancellation attempt after start date raises ValueError | **PASSED** |
| **REQ-016** | Booking Cancellation: approved booking can be cancelled | UT-032 | Unit | `test_ut032_cancel_approved_booking_also_allowed`<br>`tests/unit/test_booking_service.py` | APPROVED booking can be cancelled before start date | **PASSED** |
| **REQ-016** | Booking Cancellation: active booking cannot be cancelled | UT-033 | Unit | `test_ut033_cannot_cancel_an_active_booking`<br>`tests/unit/test_booking_service.py` | Cancellation of ACTIVE booking raises ValueError | **PASSED** |
| **REQ-016** | Booking Cancellation: owner cancel route integration | IT-307 | Integration | `test_it307_owner_can_cancel_own_booking`<br>`tests/integration/test_booking_integration.py` | Owner posts to /cancel; booking status becomes CANCELLED | **PASSED** |
| **REQ-016** | Booking Cancellation: unauthorized student route | IT-308 | Integration | `test_it308_other_student_cannot_cancel_someone_elses_booking`<br>`tests/integration/test_booking_integration.py` | Non-owner student cancelled attempt flashes permission error | **PASSED** |
| **REQ-016** | Booking Cancellation: admin cancel route integration | IT-309 | Integration | `test_it309_admin_can_cancel_a_students_booking`<br>`tests/integration/test_booking_integration.py` | Admin cancels student booking via route successfully | **PASSED** |
| **REQ-016** | Booking Cancellation: browser cancellation journey | E2E-008 | E2E (System) | `test_e2e008_user_cancels_eligible_booking`<br>`tests/e2e/tests/test_booking_journeys.py` | User clicks cancel button; badge updates to CANCELLED | **BLOCKED** *(Pending CI)* |
| **REQ-017** | State Machine: valid transitions table check (8 tests) | ST-1xx | Unit | `test_st1xx_valid_transition_in_table[...]`<br>`tests/unit/test_state_machine.py` | All 8 legal state transitions present in VALID_TRANSITIONS | **PASSED** |
| **REQ-017** | State Machine: invalid transitions table check (10 tests) | ST-1xx | Unit | `test_st1xx_invalid_transition_not_in_table[...]`<br>`tests/unit/test_state_machine.py` | All 10 illegal state transitions absent from table | **PASSED** |
| **REQ-017** | State Machine: transition_booking applies valid (8 tests) | ST-2xx | Unit | `test_st2xx_transition_booking_applies_valid_transition[...]`<br>`tests/unit/test_state_machine.py` | `transition_booking()` correctly updates booking status | **PASSED** |
| **REQ-017** | State Machine: transition_booking rejects invalid (10 tests) | ST-3xx | Unit | `test_st3xx_transition_booking_rejects_invalid_transition[...]`<br>`tests/unit/test_state_machine.py` | Illegal transitions raise ValueError and are rejected | **PASSED** |
| **REQ-017** | State Machine: UI and route forge transition rejection | E2E-011 | E2E (System) | `test_e2e011_invalid_state_transition_is_rejected`<br>`tests/e2e/tests/test_booking_journeys.py` | Forged cancel POST against CANCELLED booking rejected by backend | **BLOCKED** *(Pending CI)* |

---

## 3. Test Level Coverage Summary

| Test Level | Total Test Cases | Executed | Passed | Failed | Blocked (Pending CI) | Pass Rate of Executed |
|---|---|---|---|---|---|---|
| **Unit Testing** (`tests/unit`) | 88 | 88 | 88 | 0 | 0 | **100%** |
| **Integration Testing** (`tests/integration`) | 27 | 27 | 27 | 0 | 0 | **100%** |
| **E2E / Selenium Testing** (`tests/e2e`) | 12 | 0 | 0 | 0 | 12 | *N/A* |
| **Total Suite** | **127** | **115** | **115** | **0** | **12** | **100%** |

---

## 4. Quality Conclusion & Verification Sign-Off

- **100% Requirement Coverage**: Every functional requirement (`REQ-001` through `REQ-017`) has corresponding automated tests at the unit, integration, and/or system level.
- **Defect Verification**: Critical defects (e.g. DEF-001 admin navigation, DEF-002 capacity double-counting bug) have explicit regression test coverage mapped to requirements REQ-004 and REQ-011.
- **Traceability Verification**: No orphaned requirements exist, and every executed test has passed successfully against the codebase without modification.
