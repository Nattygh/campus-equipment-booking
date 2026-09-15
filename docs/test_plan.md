# Master Test Plan
## Campus Equipment Booking & Return System

**Author:** Mihiret Girum — REQUIREMENTS & TEST PLANNING  
**Course:** Software Testing and Validation - Addis Ababa University  
**Project:** Campus Equipment Booking & Return System Refinement  

---

## 1. Testing Objectives

The primary objectives of testing the Campus Equipment Booking & Return System are:
1. **Functional Correctness**: Verify all functional requirements (`REQ-001` through `REQ-017`) across authentication, role-based access control, catalogue management, booking workflow, and state transitions.
2. **High Test Coverage**: Achieve >=80% branch coverage on core business logic modules. Achieved results:
   - `app/services/booking_service.py`: **99%** branch coverage.
   - `app/auth.py`: **100%** branch coverage.
   - `app/models.py`: **93%** branch coverage.
   - Overall project: **87%** branch coverage.
3. **Defect Verification & Regression Prevention**: Ensure real defects identified in the audit (`DEF-001`, `DEF-002`, `DEF-003`, `DEF-004`) remain completely resolved and guarded with dedicated automated regression tests.
4. **State Machine Integrity**: Guarantee that only valid state transitions are permitted, preventing illegal operations such as bypassing approval, unauthorized cancellation, or transitions from terminal states (`REJECTED`, `RETURNED`, `CANCELLED`).
5. **Test Pyramid Demonstration**: Maintain a balanced testing pyramid comprising 88 unit tests, 27 integration tests, and 12 end-to-end browser journeys.

---

## 2. Scope

### 2.1 In-Scope
- **Authentication & User Management**: User registration (username constraints, password length >= 8 chars), login/logout, session lifecycle.
- **Role-Based Authorization**: Enforcement of student vs. admin access across all routes via the `@admin_required` decorator; UI element visibility based on user role.
- **Equipment Catalogue**: Catalogue listing, adding equipment, editing equipment with loan-preservation rules, maintenance mode toggles.
- **Booking Lifecycle**:
  - Request creation with date and quantity validation.
  - Conflict-aware capacity calculation over overlapping half-open intervals.
  - Admin approval with self-exclusion bug fix (`DEF-002`) and rejection.
  - Physical equipment handover/activation and inventory decrementing.
  - Automatic and manual overdue/late detection.
  - Equipment return and inventory restoration.
  - User and admin booking cancellation with start-date deadline enforcement.
- **Automated Test Pipelines**: Continuous Integration via GitHub Actions and local Jenkins Docker Compose.

### 2.2 Out-of-Scope
- Monetary payments, billing, or penalty fee processing.
- Multi-campus physical branch locations.
- Email, SMS, or external push notification services.
- Stress, load, and performance benchmarking under high concurrent traffic.
- Accessibility auditing beyond semantic HTML compliance.

---

## 3. Test Levels & Strategy

### 3.1 Unit Testing (`tests/unit/` — 88 Test Cases)
- **Focus**: Isolated verification of core business rules and helper functions without external dependencies.
- **Modules Covered**:
  - `app/services/booking_service.py`: Pure functions (`validate_dates`, `validate_quantity`, `dates_overlap`), availability math (`calculate_reserved_quantity`), and state operations (`approve_booking`, `activate_booking`, `mark_late`, `cancel_booking`, `return_booking`).
  - `app/auth.py`: Direct testing of the `@admin_required` decorator using monkeypatched mock users (verifying 401, 403, and 200 responses).
  - State machine transition table: Parametrized verification of all 8 valid transitions and 10 invalid transitions (`tests/unit/test_state_machine.py`).
- **Test Doubles & Seams**:
  - Clock injection seam: Service functions accept an optional `now=` parameter to allow deterministic testing of time-dependent rules (e.g. cancellation deadlines and late transitions) without system clock flakiness.
  - Database-free isolation: `tests/unit/test_booking_service_isolated.py` uses genuine `unittest.mock` doubles to test booking query filters with zero database interaction.
  - In-memory SQLite: Fast, ephemeral DB fixture for state and availability tests.

### 3.2 Integration Testing (`tests/integration/` — 27 Test Cases)
- **Focus**: Interaction between Flask routes, SQLAlchemy ORM models, session-based authentication (Flask-Login), and business services.
- **Modules Covered**:
  - `test_auth_integration.py`: Endpoints `/register`, `/login`, `/logout`, `/admin-test`, and role-based template rendering.
  - `test_equipment_integration.py`: Equipment creation (`/equipment/add`) and editing (`/equipment/<id>/edit`), input validation, and unauthorized student attempts.
  - `test_booking_integration.py`: Booking submission, availability re-checks, full lifecycle (`REQUESTED` → `APPROVED` → `ACTIVE` → `RETURNED`), cancellation permissions, and auto-flagging of late loans on dashboard view.
- **Execution & Tooling**: Uses pytest with the Flask test client and an isolated in-memory database per test case.

### 3.3 End-to-End (E2E) Testing (`tests/e2e/` — 12 Test Cases)
- **Focus**: Full system browser journeys driving the user interface as real end users.
- **Architecture**:
  - Implements the **Page Object Model (POM)** pattern (`LoginPage`, `EquipmentPage`, `BookingPage`, `AdminBookingPage`) inheriting from `BasePage`.
  - UI elements use dedicated `data-testid` attributes for resilient locator binding independent of styling changes.
  - Runs a live Flask test server on an ephemeral port in a background thread with an isolated SQLite database.
- **Scenarios Covered**:
  - `E2E-001`: Student successful login.
  - `E2E-002`: Login rejection with invalid credentials.
  - `E2E-003`: Equipment catalogue browsing.
  - `E2E-004`: Valid booking request creation.
  - `E2E-005`: Form validation rejection on invalid dates.
  - `E2E-006`: Admin approval of booking request.
  - `E2E-007`: Student viewing approved booking status.
  - `E2E-008`: Student cancelling eligible booking before deadline.
  - `E2E-009`: Equipment unavailable conflict scenario.
  - `E2E-010`: Full return workflow restoring inventory.
  - `E2E-011`: State machine violation rejection via route forging.
  - `E2E-012`: Access control enforcement blocking students from admin screens.
- **Execution Strategy**: Configured for Headless Chrome in GitHub Actions (`.github/workflows/ci.yml`) and Jenkins Docker pipelines.

### 3.4 Regression Testing
Dedicated automated regression tests ensure resolved defects never reoccur:
- **DEF-001 (Admin Sidebar Navigation)**: Regression tested by `test_it109_admin_sidebar_link_visible_for_admin` and `test_it110_admin_sidebar_link_hidden_for_student` ensuring `User.is_admin` correctly controls UI link visibility.
- **DEF-002 (Approval Capacity Double-Counting Bug)**: Regression tested by unit test `test_ut013_approve_requested_booking_succeeds` and integration test `test_it305_full_lifecycle_approve_activate_return` via `exclude_booking_id`.
- **DEF-004 (Misleading Available Quantity Input)**: Regression tested by `test_it201_admin_can_add_equipment` verifying server-side calculation.
- **Missing Cancellation Feature**: Regression tested by 6 unit tests (`UT-028` to `UT-033`) and 3 integration tests (`IT-307` to `IT-309`).

---

## 4. Test Environment

| Component | Specification |
|---|---|
| **Operating System** | Windows / Linux (Ubuntu in CI) |
| **Runtime** | Python 3.12+ |
| **Frameworks** | Flask 3.0.3, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3 |
| **Database** | SQLite (in-memory for Unit & Integration; isolated file for E2E) |
| **Test Runner** | pytest 8.3.3 |
| **Coverage Tool** | pytest-cov 5.0.0 (branch coverage enabled via `--cov-branch`) |
| **Browser Automation** | Selenium 4.24.0, Google Chrome / Chromedriver (Headless) |
| **CI/CD** | GitHub Actions (`.github/workflows/ci.yml`), Jenkins (`Jenkinsfile`) |

---

## 5. Entry & Exit Criteria

### 5.1 Entry Criteria
- Application source code and dependencies successfully installable via `pip install -r requirements.txt`.
- Application starts locally and database schema initializes cleanly.
- Unit and integration test fixtures provide clean, isolated state per test.

### 5.2 Exit Criteria
- **100% Pass Rate on Executed Tests**: All 88 unit tests and 27 integration tests (115 total) must pass without failure.
- **Branch Coverage Threshold**: Minimum 80% branch coverage across core business logic (achieved: 99% on `booking_service.py`, 100% on `auth.py`, 87% overall).
- **Zero Critical / High Defects**: 0 open defects of High or Critical severity (DEF-002 resolved and verified).
- **Bidirectional Traceability**: 100% of defined requirements in `docs/requirements.md` mapped to tests in `docs/requirements_traceability.md`.
- **Complete Documentation**: Master Test Plan, SRS Requirements, Traceability Matrix, Defect Log, and Quality Metrics documents complete and consistent.

---

## 6. Risk-Based Prioritisation & Mitigations

| Risk Area | Risk Level | Mitigation Strategy |
|---|---|---|
| **Approval Self-Conflict (DEF-002)** | **Critical** | Thread `exclude_booking_id` through all availability checks during approval; verified by UT-013, IT-305, and BVA boundary test. |
| **Inventory Overbooking / Date Conflicts** | **High** | Unit tests UT-001 through UT-009, integration test IT-304, and formal decision table tests covering date overlaps and capacity bounds. |
| **State Machine Bypass / Forgery** | **High** | Centralized `VALID_TRANSITIONS` table in `booking_service.py` checked before every state change; E2E-011 forges invalid transitions to prove rejection. |
| **Privilege Escalation** | **High** | `@admin_required` decorator tested at unit level (AUTH-001..003) and route integration level (IT-107, IT-108, IT-202). |
| **Clock / Timezone Flakiness** | **Medium** | Clock-injection seam (`now=` parameter) allows tests to supply synthetic timestamps instead of relying on real time. |
| **E2E Headless Driver Dependencies** | **Medium** | Automated skipping in local environments lacking browser binaries, with full automated execution configured in CI via `setup-chrome`. |

---

## 7. Test Deliverables

1. **Requirements Document** (`docs/requirements.md`): Formal requirement definitions (`REQ-001` through `REQ-017`).
2. **Requirements Traceability Matrix** (`docs/requirements_traceability.md`): Mapping linking requirements to 127 automated test cases with execution statuses.
3. **Master Test Plan** (`docs/test_plan.md`): Scope, strategies, levels, regression tests, environments, criteria, and risks.
4. **Defect Log** (`docs/defect_log.md`): Log of 4 real audited defects and 1 missing feature enhancement.
5. **Quality Metrics Report** (`docs/metrics.md`): Execution figures, coverage data, defect density, and DRE.
6. **Automated Test Suite** (`tests/`): 88 unit tests, 27 integration tests, 12 E2E test journeys.
7. **CI/CD Pipelines** (`.github/workflows/ci.yml`, `Jenkinsfile`, `docker/`): Automated multi-stage test pipelines.
