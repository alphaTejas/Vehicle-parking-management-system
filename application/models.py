from .database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    full_name = db.Column(db.String(120))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    location_name = db.Column(db.String(255))
    vehicle_number = db.Column(db.String(20))

class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    ad_username = db.Column(db.String(80), unique=True, nullable=False)
    ad_password_hash = db.Column(db.String(128), nullable=False)
    ad_email = db.Column(db.String(120), unique=True, nullable=False)
    ad_full_name = db.Column(db.String(120))
    all_lots = db.relationship('ParkingLot', backref='admin', lazy=True)

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    name= db.Column(db.String(120), nullable=False)  # Added name field
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    pin_code = db.Column(db.String(10), nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    #some many to one
    occupied_spots = db.Column(db.Integer, default=0, nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete-orphan")
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

    

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # 'A' for available, 'O' for occupied
    spot_number = db.Column(db.String(20))

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost_per_unit = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vehicle_number = db.Column(db.String(20), nullable=False)  # <-- Added this line

    spot = db.relationship('ParkingSpot', backref='bookings')
    user = db.relationship('User', backref='bookings')
