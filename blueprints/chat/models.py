from config import db
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

IST_OFFSET = timedelta(hours=5, minutes=30)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(255), unique=True)
    is_group = db.Column(db.Boolean, default=False)
    is_open_group = db.Column(db.Boolean, default=False)  # New field
    participants = db.Column(JSONB, nullable=False, default=list)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now() + IST_OFFSET)
    topic = db.Column(db.String(255))  # New field
    description = db.Column(db.Text)  # New field
    created_by = db.Column(db.String(255), db.ForeignKey('users.clerkId'))  # Admin creator
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), unique=True)
    team = db.relationship('Team', backref='chat', uselist=False)

    def add_participant(self, user_id):
        if not self.participants:
            self.participants = []
        
        if user_id not in self.participants:
            # Convert to Python list, modify, then convert back
            participants_list = list(self.participants)
            participants_list.append(user_id)
            self.participants = participants_list
    
    def remove_participant(self, user_id):
        if self.participants and user_id in self.participants:
            participants_list = list(self.participants)
            participants_list.remove(user_id)
            self.participants = participants_list


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(255))
    sender_id = db.Column(db.String(255))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now() + IST_OFFSET)