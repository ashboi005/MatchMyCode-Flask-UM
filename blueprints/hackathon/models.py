from config import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy import CheckConstraint

class Hackathon(db.Model):
    __tablename__ = 'hackathons'
    
    id = db.Column(db.Integer, primary_key=True)
    organiser_clerkId = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.String(50), nullable=False)
    max_team_size = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255))
    location = db.Column(db.String(255))
    tags = db.Column(JSONB, default=[])
    category = db.Column(db.String(255))
    prize_money = db.Column(db.Float)
    registration_fees = db.Column(db.String(50))
    registration_deadline = db.Column(db.DateTime, nullable=False)
    themes = db.Column(JSONB, default=[])
    rules = db.Column(JSONB, default=[])
    status = db.Column(db.String(50), default='pending')
    additional_info = db.Column(JSONB, default={})
    winners = db.Column(JSONB, default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('max_team_size >= 1 AND max_team_size <= 6', 
                       name='max_team_size_range'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'organiser_clerkId': self.organiser_clerkId,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'mode': self.mode,
            'max_team_size': self.max_team_size,
            'address': self.address,
            'location': self.location,
            'tags': self.tags,
            'category': self.category,
            'prize_money': self.prize_money,
            'registration_fees': self.registration_fees,
            'registration_deadline': self.registration_deadline.isoformat(),
            'themes': self.themes,
            'rules': self.rules,
            'status': self.status,
            'additional_info': self.additional_info,
            'winners': self.winners,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }