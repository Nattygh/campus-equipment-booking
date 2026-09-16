Campus Equipment Booking & Return System
A Flask and SQLAlchemy web application for managing campus equipment requests, bookings, approvals, activation, returns, cancellations, and equipment availability.

Features
•	User registration, login, and authorization.
•	Student equipment browsing and booking creation.
•	Date and quantity validation.
•	Booking conflict and capacity checking.
•	Maintenance restrictions.
•	Administrator approval and rejection.
•	Booking activation and equipment availability updates.
•	Equipment return and availability restoration.
•	Late-booking detection.
•	Booking cancellation.
•	Booking-state transition validation.
•	Selenium browser testing using Page Objects.
•	GitHub Actions and Jenkins CI configuration.

Technology Stack
•	Python 3.13.5
•	Flask
•	SQLAlchemy
•	SQLite
•	pytest 8.3.3
•	pytest-cov 5.0.0
•	Selenium WebDriver
•	Google Chrome
•	GitHub Actions
•	Jenkins

Testing
The project contains 127 automated tests:
Test level	Tests
Unit	88
Integration	27
Selenium E2E	12
Total	127

Reported final results:
•	Passed: 127
•	Failed: 0
•	Errors: 0
•	Pass rate: 100%
•	Overall statement coverage: 88%
•	Booking-service coverage: 99%
•	Authentication coverage: 100%
•	Execution time: 147.03 seconds
•	Warnings: 99
Running Tests
Typical commands suggested by the project configuration would be:
pytest
pytest tests/unit
pytest tests/integration
pytest tests/e2e
pytest --cov=. --cov-report=term-missing
The exact directory names and setup commands cannot be confirmed because the actual repository README and source code were not included in the uploaded PDF. The report states that Jenkins was configured but had not been independently executed and captured.[ppl-ai-file-upload.s3.amazonaws]


