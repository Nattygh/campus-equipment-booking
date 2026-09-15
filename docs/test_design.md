# Test Design Document: Campus Equipment Booking & Return System

**Course:** Software Testing and Validation - Addis Ababa University  
**Project:** Campus Equipment Booking & Return System  
**Document Version:** 2.0  
**Target Application:** Flask Campus Equipment Booking Application  

---

## 1. Introduction

This Test Design Document presents the systematic functional test design for the **Campus Equipment Booking & Return System**. The application is a Flask-based web service enabling university students to browse equipment catalogues, place booking requests, manage active loans, and cancel pending reservations, while empowering administrators to perform equipment CRUD operations, approve or reject booking requests, handle equipment dispatch (activation) and returns, and manage maintenance states.

This document derives test cases directly from the underlying application source code (`app/services/booking_service.py`, `app/routes.py`, `app/models.py`) using four formal test design techniques:
- **Equivalence Partitioning (EP)**
- **Boundary Value Analysis (BVA)**
- **Decision Table Testing (DT)**
- **State Transition Testing (ST)**

Additionally, comprehensive **Positive Test Scenarios** and **Negative Test Scenarios** are documented to validate end-to-end functional workflows and error-handling mechanisms. Every test case documented herein directly corresponds to verified automated test cases in the test suite (`tests/unit/`, `tests/integration/`, `tests/e2e/`), ensuring zero drift between specifications and system behavior.

---

## 2. Test Design Objectives

The main objectives of this test design suite are:
1. **Systematic Coverage:** Ensure all functional requirements—including user authentication, equipment cataloging, booking validation, stock management, status state machine transitions, and access authorization—are thoroughly validated.
2. **Defect Prevention & Boundary Safeguards:** Uncover edge cases and boundary conditions (such as capacity limits, zero/negative inputs, touching date windows, and post-approval inventory updates) that lead to software failures.
3. **Rigorous Access Control Verification:** Enforce strict role-based access control (RBAC), verifying that non-administrative users cannot access privileged operations or modify other users' bookings.
4. **State Machine Integrity:** Validate that booking status transitions strictly adhere to valid lifecycle paths and that illegal state transitions are deterministically blocked.
5. **Traceability:** Maintain complete 1-to-1 mapping between documented test cases and execution assertions in the automated pytest test suite.

---

## 3. Equivalence Partitioning (EP)

Equivalence Partitioning divides system input domains into disjoint partitions (valid and invalid) such that testing a single representative value from a partition provides confidence for all values in that partition.

### 3.1 Booking Dates (`REQ-DATES`)
- **Rule:** `start_date` and `expected_return_date` are mandatory, and `start_date < expected_return_date`.

| Test ID | Feature | Technique | Input / Condition | Valid / Invalid | Expected Result | Automated Test |
|---|---|---|---|---|---|---|
| EP-001 | Booking Dates | EP | `start_date` is `None`, `expected_return_date` is valid | Invalid | `ValueError: "Start and return dates are required."` | `test_ep001_missing_start_date_raises` |
| EP-002 | Booking Dates | EP | `start_date` valid, `expected_return_date` is `None` | Invalid | `ValueError: "Start and return dates are required."` | `test_ep002_missing_end_date_raises` |
| EP-003 | Booking Dates | EP | `start_date == expected_return_date` | Invalid | `ValueError: "Expected return date must be after the start date."` | `test_ep003_start_equal_to_end_raises` |
| EP-004 | Booking Dates | EP | `start_date > expected_return_date` | Invalid | `ValueError: "Expected return date must be after the start date."` | `test_ep004_start_after_end_raises` |
| EP-005 | Booking Dates | EP | `start_date < expected_return_date` | Valid | Period accepted without exception | `test_ep005_end_after_start_is_accepted` |

### 3.2 Booking Quantity (`REQ-QTY`)
- **Rule:** Requested quantity must be a non-null, strictly positive integer (`quantity > 0`).

| Test ID | Feature | Technique | Input / Condition | Valid / Invalid | Expected Result | Automated Test |
|---|---|---|---|---|---|---|
| EP-006 | Booking Quantity | EP | `quantity` is `None` | Invalid | `ValueError: "Quantity is required."` | `test_ep006_none_quantity_raises` |
| EP-007 | Booking Quantity | EP | `quantity == 0` | Invalid | `ValueError: "Booking quantity must be greater than zero."` | `test_ep007_zero_quantity_raises` |
| EP-008 | Booking Quantity | EP | `quantity < 0` (e.g. -5) | Invalid | `ValueError: "Booking quantity must be greater than zero."` | `test_ep008_negative_quantity_raises` |
| EP-009 | Booking Quantity | EP | `quantity > 0` (e.g. 5) within available capacity | Valid | Quantity accepted without exception | `test_ep009_positive_quantity_is_accepted` |

### 3.3 Equipment Availability & Maintenance (`REQ-MAINT`, `REQ-QTY`)
- **Rule:** Equipment flagged with `maintenance = True` cannot be booked; requested quantity cannot exceed available stock.

| Test ID | Feature | Technique | Input / Condition | Valid / Invalid | Expected Result | Automated Test |
|---|---|---|---|---|---|---|
| EP-010 | Equipment Availability | EP | `maintenance = False`, `quantity <= available_quantity` | Valid | Availability check returns `True` | `test_ut006_check_availability_true_when_stock_sufficient` |
| EP-011 | Equipment Availability | EP | `maintenance = True` | Invalid | `ValueError: "This equipment is currently under maintenance."` | `test_ut008_check_availability_raises_under_maintenance` |
| EP-012 | Equipment Availability | EP | `quantity > total_quantity` | Invalid | `ValueError: "Requested quantity exceeds total equipment quantity."` | `test_ut007_check_availability_raises_when_quantity_exceeds_stock` |
| EP-013 | Equipment Availability | EP | `quantity > (total_quantity - reserved_by_others)` | Invalid | `ValueError: "The requested quantity is not available for the selected period."` | `test_ut009_check_availability_raises_when_reserved_by_others` |

### 3.4 User Registration & Authentication (`REQ-AUTH`)
- **Rule:** Registration requires unique username and password length >= 8 characters.

| Test ID | Feature | Technique | Input / Condition | Valid / Invalid | Expected Result | Automated Test |
|---|---|---|---|---|---|---|
| EP-014 | Authentication | EP | Registration password length < 8 chars (e.g. "pass") | Invalid | Flash message: "Password must be at least 8 characters." | `test_register_short_password_fails` |
| EP-015 | Authentication | EP | Registration with existing username | Invalid | Flash message: "Username already exists." | `test_register_duplicate_username_fails` |
| EP-016 | Authentication | EP | Login with incorrect password | Invalid | Flash message: "Invalid username or password." | `test_login_invalid_password_fails` |
| EP-017 | Authentication | EP | Valid registration credentials | Valid | User created, redirected to login page | `test_register_success` |

---

## 4. Boundary Value Analysis (BVA)

Boundary Value Analysis tests system behaviors at the boundaries of equivalence partitions, including values at the minimum/maximum boundaries and immediately outside them.

### 4.1 Quantity Lower Boundary
- **Boundary:** Minimum valid quantity is `1`. Boundary testing points: `0` (just below), `1` (on boundary).

| Test ID | Feature | Technique | Input Value / Scenario | Expected Result | Automated Test |
|---|---|---|---|---|---|
| BVA-001 | Quantity Boundary | BVA | `quantity = 0` (Just below boundary) | Rejected: `ValueError: "Booking quantity must be greater than zero."` | `test_ep007_zero_quantity_raises` |
| BVA-002 | Quantity Boundary | BVA | `quantity = 1` (Exact lower boundary) | Accepted: Validation succeeds | `test_bva001_quantity_of_one_is_accepted` |

### 4.2 Date-Range Overlap Boundaries (Half-Open Interval)
- **Boundary:** Overlap detection algorithm uses half-open interval `[start, end)`. Touching windows (`start_b == end_a`) do not overlap.

| Test ID | Feature | Technique | Input Value / Scenario | Expected Result | Automated Test |
|---|---|---|---|---|---|
| BVA-003 | Date Overlap | BVA | Window B starts exactly at Window A end date (`start_b == end_a`) | Accepted: No overlap (`dates_overlap == False`) | `test_st003_adjacent_windows_do_not_overlap` |
| BVA-004 | Date Overlap | BVA | Window B starts 1 unit before Window A end date (`start_b == end_a - 1 min`) | Rejected: Overlap detected (`dates_overlap == True`) | `test_st004_partial_overlap_is_detected` |

### 4.3 Available Capacity Boundary
- **Boundary:** Total physical capacity vs. active reservations.

| Test ID | Feature | Technique | Input Value / Scenario | Expected Result | Automated Test |
|---|---|---|---|---|---|
| BVA-005 | Capacity Boundary | BVA | Requested quantity equals exact remaining unreserved capacity | Accepted: Approval succeeds (self-booking excluded during re-check) | `test_ut013_approve_requested_booking_succeeds` |
| BVA-006 | Capacity Boundary | BVA | Requested quantity equals remaining unreserved capacity + 1 | Rejected: `ValueError: "The requested quantity is not available for the selected period."` | `test_ut015_approve_rechecks_availability_and_rejects_conflict` |

---

## 5. Decision Table Testing

Decision table testing models complex business logic where multiple boolean conditions combine to determine system actions.

### 5.1 Booking Approval Logic (`approve_booking`)
**Conditions:**
- `C1`: Is the actor an Administrator?
- `C2`: Is the booking status `REQUESTED`?
- `C3`: Is the equipment currently operational (not under maintenance)?
- `C4`: Is requested quantity available after excluding self-reservation?

| Rule ID | C1 | C2 | C3 | C4 | Action / Expected Result | Automated Test |
|---|---|---|---|---|---|---|
| DT-001 | N | - | - | - | HTTP 403 Forbidden ("Admin access required") | `test_it107_admin_only_route_forbidden_for_student` |
| DT-002 | Y | N | - | - | Rejected: `ValueError: "Only requested bookings can be approved."` | `test_ut014_approve_non_requested_booking_raises` |
| DT-003 | Y | Y | N | - | Rejected: `ValueError: "This equipment is currently under maintenance."` | `test_ut008_check_availability_raises_under_maintenance` |
| DT-004 | Y | Y | Y | N | Rejected: `ValueError: "The requested quantity is not available for the selected period."` | `test_ut015_approve_rechecks_availability_and_rejects_conflict` |
| DT-005 | Y | Y | Y | Y | **Approved:** Status updated to `APPROVED` | `test_ut013_approve_requested_booking_succeeds` |

### 5.2 Booking Activation Logic (`activate_booking`)
**Conditions:**
- `C1`: Is the actor an Administrator?
- `C2`: Is the booking status `APPROVED`?
- `C3`: Is the equipment operational (not placed in maintenance after approval)?
- `C4`: Is physical available stock >= requested quantity?

| Rule ID | C1 | C2 | C3 | C4 | Action / Expected Result | Automated Test |
|---|---|---|---|---|---|---|
| DT-006 | N | - | - | - | HTTP 403 Forbidden | `test_it107_admin_only_route_forbidden_for_student` |
| DT-007 | Y | N | - | - | Rejected: `ValueError: "Only approved bookings can be activated."` | `test_ut018_activate_non_approved_booking_raises` |
| DT-008 | Y | Y | N | - | Rejected: `ValueError: "Cannot activate equipment that is under maintenance."` | `test_ut019_activate_raises_when_equipment_under_maintenance` |
| DT-009 | Y | Y | Y | N | Rejected: `ValueError: "Not enough physical equipment is currently available."` | `test_ut020_activate_raises_when_physical_stock_insufficient` |
| DT-010 | Y | Y | Y | Y | **Activated:** Status updated to `ACTIVE`, physical stock decremented | `test_ut017_activate_approved_booking_reduces_available_quantity` |

### 5.3 Booking Cancellation Logic (`cancel_booking`)
**Conditions:**
- `C1`: Is actor the booking owner OR an admin?
- `C2`: Is booking status `REQUESTED` or `APPROVED`?
- `C3`: Is current time < booking `start_date` (cancellation deadline)?

| Rule ID | C1 | C2 | C3 | Action / Expected Result | Automated Test |
|---|---|---|---|---|---|
| DT-011 | N | - | - | Rejected: `PermissionError: "Only the booking owner or an admin may cancel this booking."` | `test_it308_student_cannot_cancel_others_booking` |
| DT-012 | Y | N | - | Rejected: `ValueError: "Invalid booking transition..."` | `test_ut023_cancel_active_booking_raises` |
| DT-013 | Y | Y | N | Rejected: `ValueError: "This booking can no longer be cancelled; the cancellation deadline has passed."` | `test_ut024_cancel_past_start_date_raises` |
| DT-014 | Y | Y | Y | **Cancelled:** Status updated to `CANCELLED` | `test_it307_owner_can_cancel_own_booking` |

---

## 6. State Transition Testing

State Transition testing evaluates system compliance with allowed state lifecycle paths and verifies that invalid transitions are blocked.

### 6.1 State Lifecycle Diagram

```
                 +-----------+
                 | REQUESTED |
                 +-----+-----+
                       |
         +-------------+-------------+
         |             |             |
     (approve)     (reject)      (cancel)
         |             |             |
         v             v             v
   +----------+  +----------+  +-----------+
   | APPROVED |  | REJECTED |  | CANCELLED |
   +-----+----+  +----------+  +-----------+
         |
    +----+----+
    |         |
(activate) (cancel)
    |         |
    v         v
+--------+ +-----------+
| ACTIVE | | CANCELLED |
+---+----+ +-----------+
    |
    +---------------+
    |               |
(time passes)    (return)
    |               |
    v               v
 +------+     +----------+
 | LATE |     | RETURNED |
 +--+---+     +----------+
    |
 (return)
    |
    v
+----------+
| RETURNED |
+----------+
```

### 6.2 Valid State Transitions

| Test ID | Current State | Action | Expected New State | Valid / Invalid | Automated Test |
|---|---|---|---|---|---|
| ST-001 | REQUESTED | `approve_booking()` | APPROVED | Valid | `test_st2xx_transition_booking_applies_valid_transition[REQUESTED-APPROVED]` |
| ST-002 | REQUESTED | `reject_booking()` | REJECTED | Valid | `test_st2xx_transition_booking_applies_valid_transition[REQUESTED-REJECTED]` |
| ST-003 | REQUESTED | `cancel_booking()` | CANCELLED | Valid | `test_it307_owner_can_cancel_own_booking` |
| ST-004 | APPROVED | `activate_booking()` | ACTIVE | Valid | `test_it305_full_lifecycle_approve_activate_return` |
| ST-005 | APPROVED | `cancel_booking()` | CANCELLED | Valid | `test_it309_admin_can_cancel_a_students_booking` |
| ST-006 | ACTIVE | Time > `expected_return_date` | LATE | Valid | `test_ut021_mark_late_transitions_active_past_due_booking` |
| ST-007 | ACTIVE | `return_booking()` | RETURNED | Valid | `test_it305_full_lifecycle_approve_activate_return` |
| ST-008 | LATE | `return_booking()` | RETURNED | Valid | `test_ut025_return_late_booking_succeeds` |

### 6.3 Invalid State Transitions

| Test ID | Current State | Action | Target State | Valid / Invalid | Expected Result | Automated Test |
|---|---|---|---|---|---|---|
| ST-101 | RETURNED | Transition | APPROVED | Invalid | `ValueError: Invalid booking transition: RETURNED -> APPROVED` | `test_st3xx_transition_booking_rejects_invalid_transition[RETURNED-APPROVED]` |
| ST-102 | REJECTED | Transition | ACTIVE | Invalid | `ValueError: Invalid booking transition: REJECTED -> ACTIVE` | `test_st3xx_transition_booking_rejects_invalid_transition[REJECTED-ACTIVE]` |
| ST-103 | CANCELLED | Transition | APPROVED | Invalid | `ValueError: Invalid booking transition: CANCELLED -> APPROVED` | `test_st3xx_transition_booking_rejects_invalid_transition[CANCELLED-APPROVED]` |
| ST-104 | REQUESTED | Skip Approval | ACTIVE | Invalid | `ValueError: Invalid booking transition: REQUESTED -> ACTIVE` | `test_st3xx_transition_booking_rejects_invalid_transition[REQUESTED-ACTIVE]` |
| ST-105 | CANCELLED | Transition | ACTIVE | Invalid | `ValueError: Invalid booking transition: CANCELLED -> ACTIVE` | `test_st3xx_transition_booking_rejects_invalid_transition[CANCELLED-ACTIVE]` |
| ST-106 | APPROVED | Revert | REQUESTED | Invalid | `ValueError: Invalid booking transition: APPROVED -> REQUESTED` | `test_st3xx_transition_booking_rejects_invalid_transition[APPROVED-REQUESTED]` |
| ST-107 | ACTIVE | Revert | APPROVED | Invalid | `ValueError: Invalid booking transition: ACTIVE -> APPROVED` | `test_st3xx_transition_booking_rejects_invalid_transition[ACTIVE-APPROVED]` |

---

## 7. Positive Test Scenarios

Positive test scenarios validate expected core functional user journeys under valid conditions.

| Test ID | Feature | Scenario Description | Inputs / Steps | Expected Result | Automated Test |
|---|---|---|---|---|---|
| POS-001 | User Auth | Valid Registration & Login | 1. Register with username "student1", password "StudentPass123!".<br>2. Log in with credentials. | Registration succeeds, login redirects to user dashboard. | `test_it101_register_and_login_flow` |
| POS-002 | Booking | Valid Booking Request | Student selects item "Projector", quantity 1, valid dates (tomorrow to +2 days). | Booking request created with status `REQUESTED`. Flash message displayed. | `test_it301_create_booking_route_creates_requested_booking` |
| POS-003 | Booking | Admin Approval | Admin logs in, views pending requests, clicks Approve on `REQUESTED` booking. | Booking status changes to `APPROVED`. Re-check of availability passes. | `test_it305_full_lifecycle_approve_activate_return` |
| POS-004 | Booking | Admin Activation | Admin clicks Activate on `APPROVED` booking. | Status changes to `ACTIVE`. Equipment `available_quantity` decremented. | `test_it305_full_lifecycle_approve_activate_return` |
| POS-005 | Booking | Equipment Return | Admin/Student processes return on `ACTIVE` booking. | Status changes to `RETURNED`. Equipment `available_quantity` restored. | `test_it305_full_lifecycle_approve_activate_return` |
| POS-006 | Booking | Student Cancellation | Student cancels own `REQUESTED` booking before start date. | Status updated to `CANCELLED`. Reservation freed. | `test_it307_owner_can_cancel_own_booking` |
| POS-007 | Admin CRUD | Equipment Management | Admin adds new equipment item (Name: "VR Headset", Qty: 3). | Equipment saved to database and rendered in catalogue. | `test_it201_admin_can_add_equipment` |

---

## 8. Negative Test Scenarios

Negative test scenarios verify system resilience, error handling, and security enforcement when encountering invalid inputs or unauthorized operations.

| Test ID | Feature | Scenario Description | Inputs / Steps | Expected Result | Automated Test |
|---|---|---|---|---|---|
| NEG-001 | User Auth | Invalid Login Password | Attempt login with valid username but wrong password. | Authentication fails. Flash message: "Invalid username or password." | `test_it103_login_wrong_password_flashes_error` |
| NEG-002 | Booking | Over-allocation Quantity | Student requests quantity 10 for item with total quantity 5. | Form submission rejected. Flash: "Requested quantity exceeds total equipment quantity." | `test_it302_create_booking_exceeding_total_fails` |
| NEG-003 | Booking | Invalid Date Range | Student submits start date after return date. | Form submission rejected. Flash: "Expected return date must be after the start date." | `test_it303_create_booking_invalid_dates_fails` |
| NEG-004 | Booking | Conflicting Date Booking | Second student books item for date range overlapping existing confirmed reservation. | Booking request rejected due to stock conflict. | `test_it304_second_conflicting_booking_rejected` |
| NEG-005 | Access Control | Unauthorized Admin Access | Non-admin student navigates directly to `/admin/bookings`. | HTTP 403 Forbidden status returned. Access blocked. | `test_it107_admin_only_route_forbidden_for_student` |
| NEG-006 | Cancellation | Cancellation Past Start Date | Student attempts to cancel booking after start date has passed. | Operation rejected: "This booking can no longer be cancelled..." | `test_ut024_cancel_past_start_date_raises` |
| NEG-007 | Cancellation | Unauthorized Cancellation | Student A attempts to POST cancel request for Student B's booking. | Operation rejected: `PermissionError`. Status unchanged. | `test_it308_student_cannot_cancel_others_booking` |
| NEG-008 | State Machine | Double Cancellation / Action | Client attempts to trigger cancel action on already `CANCELLED` booking. | Backend rejects transition. Status remains `CANCELLED`. | `E2E-011` / `test_st3xx_transition_booking_rejects_invalid_transition` |

---

## 9. Test Case Summary

### 9.1 Summary by Test Design Technique

| Technique | Total Test Cases | Valid Cases | Invalid Cases | Unit / Integration Test Coverage |
|---|---|---|---|---|
| Equivalence Partitioning (EP) | 17 | 4 | 13 | `test_validation.py`, `test_auth_integration.py` |
| Boundary Value Analysis (BVA) | 6 | 3 | 3 | `test_validation.py`, `test_booking_service.py` |
| Decision Table Testing (DT) | 14 | 3 | 11 | `test_booking_service.py`, `test_booking_integration.py` |
| State Transition Testing (ST) | 15 | 8 | 7 | `test_state_machine.py`, `test_booking_integration.py` |
| Positive Scenarios (POS) | 7 | 7 | 0 | `test_auth_integration.py`, `test_booking_integration.py` |
| Negative Scenarios (NEG) | 8 | 0 | 8 | `test_booking_integration.py`, `test_equipment_integration.py` |
| **Total Functional Test Suite** | **67** | **25** | **42** | **100% Automated Coverage** |

### 9.2 Execution Suite Mapping Matrix

| Layer | Test Files | Primary Scope | Execution Status |
|---|---|---|---|
| **Unit Tests** | `test_validation.py`<br>`test_booking_service.py`<br>`test_state_machine.py`<br>`test_auth.py` | Pure validation logic, date overlap calculations, capacity rules, state machine transitions | Automated Pytest (Passing) |
| **Integration Tests** | `test_auth_integration.py`<br>`test_booking_integration.py`<br>`test_equipment_integration.py` | Flask HTTP request routes, DB transactions, Flask-Login authentication, session management | Automated Pytest (Passing) |
| **E2E Tests** | `tests/e2e/tests/` (12 journeys) | Full browser user journeys using Selenium WebDriver Page Object Pattern | Structurally verified; executable in CI container |

---
*End of Test Design Document.*
