from config import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class Hackathon(db.Model):
    __tablename__ = 'hackathons'
    
    id = db.Column(db.Integer, primary_key=True)
    organiser_clerkId = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.String(50), nullable=False)  # online/offline
    address = db.Column(db.String(255))
    location = db.Column(db.String(255))
    tags = db.Column(JSONB, default=[])
    category = db.Column(db.String(255))
    prize_money = db.Column(db.Float)
    registration_fees = db.Column(db.String(50))  #free/paid with amount
    registration_deadline = db.Column(db.DateTime, nullable=False)
    themes = db.Column(JSONB, default=[])
    rules = db.Column(JSONB, default=[])
    status = db.Column(db.String(50), default='pending')  # pending/approved/live/expired
    additional_info = db.Column(JSONB, default={})
    winners = db.Column(JSONB, default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'organiser': self.organiser_clerkId,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'mode': self.mode,
            'location': self.location,
            'status': self.status,
            'registration_deadline': self.registration_deadline.isoformat(),
            'prize_money': self.prize_money,
            # Add other fields as needed
        }

class UserHackathonRegistration(db.Model):
    __tablename__ = 'user_hackathon_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_clerkId = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    hackathon_id = db.Column(db.Integer, db.ForeignKey('hackathons.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)