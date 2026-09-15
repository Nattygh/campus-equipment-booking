# Software Requirements Specification (SRS)
## Campus Equipment Booking & Return System

**Author:** Mihiret Girum — REQUIREMENTS & TEST PLANNING  
**Course:** Software Testing and Validation - Addis Ababa University  
**Project:** Campus Equipment Booking & Return System Refinement  

---

## 1. Introduction

This document specifies the functional requirements for the **Campus Equipment Booking & Return System**, a Flask-based web application designed to manage shared academic and laboratory equipment on campus. Every requirement listed here reflects actual application logic implemented in `app/models.py`, `app/routes.py`, `app/services/booking_service.py`, and `app/auth.py`. No hypothetical or unimplemented features are included.

---

## 2. User Roles & Personas

The system defines two distinct roles via the `User.role` attribute:

1. **Student (`student`)**:
   - Registers for an account and logs into the system.
   - Browses the equipment catalogue and checks item details and availability.
   - Submits booking requests for specific time windows.
   - Views personal booking status on the dashboard and booking history page.
   - Cancels own `REQUESTED` or `APPROVED` bookings prior to the booking start date.

2. **Administrator (`admin`)**:
   - Inherits all student capabilities.
   - Adds new equipment to the catalogue and edits existing equipment details.
   - Manages equipment maintenance status.
   - Views all booking requests across all campus users.
   - Reviews and approves or rejects `REQUESTED` bookings.
   - Hands over physical equipment to activate `APPROVED` bookings into `ACTIVE` status.
   - Processes equipment returns for `ACTIVE` or `LATE` bookings back into inventory.
   - Cancels any eligible booking across the system prior to its start date.

---

## 3. Functional Requirements

### 3.1 Authentication & Account Management

#### REQ-001: User Registration
The system shall allow new users to register an account with a unique username and a password.
- **Rules**:
  - The username field is required and must not be empty or whitespace.
  - The password must be at least 8 characters in length.
  - The username must be unique in the system; duplicate usernames shall be rejected with an appropriate error message.
  - Newly registered users are assigned the `student` role by default.
  - Passwords must be securely hashed using Werkzeug security functions before database storage.

#### REQ-002: User Login & Session Initiation
The system shall allow registered users to log in by providing valid credentials.
- **Rules**:
  - Valid username and password hash matching logs the user in and establishes an authenticated session via Flask-Login.
  - Invalid credentials shall be rejected with a user-friendly error message ("Invalid username or password.").
  - Already authenticated users accessing `/login` or `/register` shall be redirected to `/dashboard`.

#### REQ-003: User Logout
The system shall allow authenticated users to log out and terminate their active session.
- **Rules**:
  - Accessing the logout endpoint clears session cookies and redirects the user to the login page.
  - Unauthenticated access to logout is prevented.

---

### 3.2 Role-Based Access Control & Authorization

#### REQ-004: Role-Based Authorization Enforcement
The system shall enforce role-based access control on protected routes using the `@admin_required` decorator.
- **Rules**:
  - Protected administrative endpoints (`/admin-test`, `/equipment/add`, `/equipment/<id>/edit`, `/admin/bookings`, `/admin/bookings/<id>/approve`, `/admin/bookings/<id>/reject`, `/admin/bookings/<id>/activate`, `/admin/bookings/<id>/return`) require an authenticated user with `role == "admin"`.
  - If an unauthenticated user attempts to access an admin route, the system shall return HTTP status `401 Unauthorized`.
  - If an authenticated non-admin user (role `student`) attempts to access an admin route, the system shall return HTTP status `403 Forbidden`.
  - Administrative navigation elements (such as the admin sidebar link) shall render only for users with administrative privileges (`current_user.is_admin == True`).

---

### 3.3 Dashboards & Operational Monitoring

#### REQ-005: User and Administrative Dashboards
The system shall provide role-tailored dashboards upon login.
- **Rules**:
  - For **Students**, the dashboard displays personal metrics: total bookings count, requested bookings count, active bookings count, late bookings count, and the 5 most recent personal bookings.
  - For **Administrators**, the dashboard displays system-wide metrics: total equipment count, available equipment count, pending booking requests awaiting review, total active loans across campus, and overdue/late loans across campus.

---

### 3.4 Equipment Catalogue Management

#### REQ-006: Equipment Catalogue Browsing
The system shall allow authenticated users to browse the catalogue of equipment items.
- **Rules**:
  - The catalogue presents item name, category, total quantity, available physical quantity, and maintenance status.
  - Items under maintenance are visibly marked with a badge or alert.

#### REQ-007: Equipment Creation (Admin)
The system shall allow administrators to create new equipment items in the catalogue.
- **Rules**:
  - The administrator must provide equipment name, category, and total quantity.
  - Equipment name and category are required.
  - Total quantity must be an integer greater than or equal to 1.
  - Initial `available_quantity` is automatically set equal to the total `quantity`.
  - An optional maintenance toggle sets whether the equipment is immediately placed under maintenance.

#### REQ-008: Equipment Modification (Admin)
The system shall allow administrators to edit existing equipment attributes.
- **Rules**:
  - An administrator can modify the name, category, total quantity, and maintenance status.
  - The new total quantity must be an integer greater than or equal to 1.
  - The new total quantity must not be set lower than the number of units currently checked out (`quantity - available_quantity`).
  - Available quantity is updated automatically to reflect changes in total quantity while preserving checked-out inventory.

---

### 3.5 Booking Lifecycle & Business Rules

#### REQ-009: Booking Request Creation & Date/Quantity Validation
The system shall allow authenticated users to request an equipment booking for a specified period and quantity.
- **Rules**:
  - New bookings are created with initial status `REQUESTED`.
  - `start_date` and `expected_return_date` are strictly required.
  - `expected_return_date` must be strictly after `start_date` (`start_date < expected_return_date`).
  - Requested `quantity` must be a positive integer strictly greater than zero (`quantity >= 1`).
  - Requested `quantity` must not exceed the total physical capacity of the equipment item (`quantity <= equipment.quantity`).

#### REQ-010: Conflict-Aware Availability Checking
The system shall verify equipment availability prior to creating or approving any booking request.
- **Rules**:
  - Booking periods overlap if and only if `start_a < end_b AND end_a > start_b` (half-open interval; touching windows do not conflict).
  - Existing bookings in states `REQUESTED`, `APPROVED`, `ACTIVE`, and `LATE` consume reserved capacity for their respective overlapping date windows.
  - Bookings in states `REJECTED`, `RETURNED`, or `CANCELLED` do not consume reserved capacity.
  - Total reserved quantity is calculated by summing quantities of all overlapping active reservations.
  - Available capacity for the period is `equipment.quantity - reserved_quantity`.
  - If requested quantity exceeds available capacity for the window, the booking request shall be rejected with an error.
  - Equipment flagged as `maintenance == True` cannot be booked under any circumstance.

#### REQ-011: Booking Approval (Admin)
The system shall allow administrators to approve `REQUESTED` bookings.
- **Rules**:
  - Only bookings in `REQUESTED` status can be approved.
  - Approval re-verifies availability over the requested period against all *other* overlapping bookings, explicitly excluding the booking's own ID from the reserved count (`exclude_booking_id=booking.id`) to prevent self-conflict failures at capacity boundaries.
  - Upon approval, the booking status transitions to `APPROVED`.
  - Physical inventory counter (`available_quantity`) is not decremented at approval time; reservation is held by schedule.

#### REQ-012: Booking Rejection (Admin)
The system shall allow administrators to reject `REQUESTED` bookings.
- **Rules**:
  - Only bookings in `REQUESTED` status can be rejected.
  - Upon rejection, the booking transitions to terminal status `REJECTED`.
  - The rejected booking immediately releases any reserved capacity for that period.

#### REQ-013: Booking Handover & Activation (Admin)
The system shall allow administrators to hand over physical equipment, activating an `APPROVED` booking.
- **Rules**:
  - Only bookings in `APPROVED` status can be activated.
  - Activation fails if the equipment has been placed under maintenance since approval.
  - Activation fails if the current physical `available_quantity` is less than the booking's requested quantity.
  - Upon successful activation, the booking transitions to `ACTIVE` status.
  - The equipment's physical inventory counter `available_quantity` is decremented by the booking's quantity.

#### REQ-014: Automatic & On-Demand Late Status Flagging
The system shall flag active bookings as overdue when the expected return date has passed.
- **Rules**:
  - An `ACTIVE` booking whose `expected_return_date < current_timestamp` shall transition to `LATE`.
  - Non-active bookings cannot transition to `LATE`.
  - The system automatically triggers late-flagging evaluations when users load the My Bookings page (`/bookings`).

#### REQ-015: Equipment Return Processing (Admin)
The system shall allow administrators to process the return of borrowed equipment.
- **Rules**:
  - Only bookings in `ACTIVE` or `LATE` status can be returned.
  - Processing a return sets the booking's `actual_return_date` to the current timestamp.
  - The booking status transitions to terminal status `RETURNED`.
  - The equipment's physical inventory counter `available_quantity` is incremented by the booking's quantity, capped at the equipment's total `quantity`.

#### REQ-016: Booking Cancellation (Owner or Admin)
The system shall allow booking owners or administrators to cancel eligible bookings before the start date.
- **Rules**:
  - Only bookings in `REQUESTED` or `APPROVED` status can be cancelled.
  - Cancellation must occur strictly before the booking's `start_date` (`now < booking.start_date`); once the start time arrives or passes, cancellation is prohibited.
  - Only the user who created the booking or an administrator has permission to cancel the booking. Other non-admin users attempting cancellation shall be rejected with a permission error.
  - Upon cancellation, the booking transitions to terminal status `CANCELLED`.
  - Cancelled bookings immediately release reserved capacity.

#### REQ-017: State Machine Enforcement & Transition Integrity
The system shall strictly enforce legal state transitions according to the formal state model.
- **Rules**:
  - Allowed transitions are strictly defined by `VALID_TRANSITIONS`:
    - `REQUESTED` → `APPROVED`, `REJECTED`, `CANCELLED`
    - `APPROVED` → `ACTIVE`, `CANCELLED`
    - `ACTIVE` → `LATE`, `RETURNED`
    - `LATE` → `RETURNED`
    - `REJECTED` → (terminal: no transitions allowed)
    - `RETURNED` → (terminal: no transitions allowed)
    - `CANCELLED` → (terminal: no transitions allowed)
  - Any attempt to bypass the state machine (e.g. jumping `REQUESTED` → `ACTIVE`, `REQUESTED` → `RETURNED`), reverse state (e.g. `APPROVED` → `REQUESTED`, `ACTIVE` → `APPROVED`), or transition out of terminal states shall raise a `ValueError` and be rejected.

---

## 4. Summary Requirement IDs Reference Table

| Requirement ID | Requirement Title | Category | Applicable Roles |
|---|---|---|---|
| **REQ-001** | User Registration | Authentication | Public / Guest |
| **REQ-002** | User Login & Session | Authentication | Public / Guest |
| **REQ-003** | User Logout | Authentication | Student, Admin |
| **REQ-004** | Role-Based Authorization Enforcement | Authorization | Student, Admin |
| **REQ-005** | User and Administrative Dashboards | Reporting & Monitoring | Student, Admin |
| **REQ-006** | Equipment Catalogue Browsing | Equipment | Student, Admin |
| **REQ-007** | Equipment Creation | Equipment | Admin |
| **REQ-008** | Equipment Modification | Equipment | Admin |
| **REQ-009** | Booking Request Creation & Date/Quantity Validation | Booking | Student, Admin |
| **REQ-010** | Conflict-Aware Availability Checking | Booking | Student, Admin |
| **REQ-011** | Booking Approval | Booking Lifecycle | Admin |
| **REQ-012** | Booking Rejection | Booking Lifecycle | Admin |
| **REQ-013** | Booking Handover & Activation | Booking Lifecycle | Admin |
| **REQ-014** | Automatic & On-Demand Late Status Flagging | Booking Lifecycle | System / Student |
| **REQ-015** | Equipment Return Processing | Booking Lifecycle | Admin |
| **REQ-016** | Booking Cancellation | Booking Lifecycle | Student (Owner), Admin |
| **REQ-017** | State Machine Enforcement & Transition Integrity | Architecture & Integrity | System-wide |
