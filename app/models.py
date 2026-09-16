from datetime import datetime

from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")

    bookings = db.relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    available_quantity = db.Column(db.Integer, nullable=False, default=1)
    maintenance = db.Column(db.Boolean, nullable=False, default=False)

    bookings = db.relationship(
        "Booking",
        back_populates="equipment",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Equipment {self.name}>"


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    equipment_id = db.Column(
        db.Integer,
        db.ForeignKey("equipment.id"),
        nullable=False,
    )

    quantity = db.Column(db.Integer, nullable=False)

    start_date = db.Column(db.DateTime, nullable=False)
    expected_return_date = db.Column(db.DateTime, nullable=False)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="REQUESTED",
    )

    actual_return_date = db.Column(
    db.DateTime,
    nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    user = db.relationship(
        "User",
        back_populates="bookings",
    )

    equipment = db.relationship(
        "Equipment",
        back_populates="bookings",
    )

    def __repr__(self):
        return f"<Booking {self.id} {self.status}>"