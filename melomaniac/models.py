from flask_login import UserMixin
from sqlalchemy import func
from . import db
from datetime import datetime
from enum import Enum
import hashlib

class EventStatus(Enum):
    OPEN = 0
    INACTIVE = 1
    SOLDOUT = 2
    CANCELLED = 3


class Genre(Enum):
    ROCK = 0
    POP = 1
    JAZZ = 2
    CLASSICAL = 3
    COUNTRY = 4
    HIPHOP = 5
    ELECTRONIC = 6
    FOLK = 7
    BLUES = 8
    LATIN = 9
    REGGAE = 10
    RNB = 11
    METAL = 12
    PUNK = 13
    FUNK = 14
    SOUL = 15

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(100), nullable=True)

    comments = db.relationship('Comment', backref='user')
    events = db.relationship('Event', backref='user')
    bookings = db.relationship('Booking', backref='user')

    def __repr__(self):
        return '<User {}, {}, {}, {}>'.format(self.name, self.email, self.contact_number, self.address)
    
    def get_profile_color(self):
        """
        This function returns a color based on the user's id.
        This ensures that the same user will always have the same color when viewing comments.
        """
        colors = [
            "#FFDAB9",
            "#E6E6FA",
            "#FFC0CB",
            "#FFFACD",
        ]
        color_index = self.id % len(colors)
        return colors[color_index]

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    publish_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    genre = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(400), nullable=False)
    ticket_price = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.Integer, default=EventStatus.OPEN.value)

    bookings = db.relationship('Booking', backref='event')
    comments = db.relationship('Comment', backref='event')

    @property
    def bookings_count(self):
        return db.session.query(func.sum(Booking.quantity)).filter_by(event_id=self.id).scalar() or 0
    
    @property
    def available_tickets(self):
        return self.venue.capacity - self.bookings_count

    def to_dicts(self):
        return {
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'venue_id': self.venue_id,
            'publish_date': self.publish_date,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'genre': self.genre,
            'image': self.image,
            'ticket_price': self.ticket_price,
            # Add other fields if needed
        }

    def readable_date(self, time):
        return time.strftime("%b %d, %Y at %I:%M %p")

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    text = db.Column(db.String(500), nullable=False)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    def readable_date(self, time):
        return time.strftime("%b %d, %Y at %I:%M %p")

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    events = db.relationship('Event', backref='venue')

    def to_dict(self):
        return {
            'name': self.name,
            'address': self.address,
            'capacity': self.capacity,
            'id': self.id
            # Add other fields if needed
        }
