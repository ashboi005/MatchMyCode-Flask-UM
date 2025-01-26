from config import db
from datetime import datetime
import random
import string
from sqlalchemy.dialects.postgresql import JSONB

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    hackathon_id = db.Column(db.Integer, db.ForeignKey('hackathons.id'), nullable=False)
    leader_id = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    team_code = db.Column(db.String(8), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    max_members = db.Column(db.Integer, nullable=False)
    members = db.Column(JSONB, default=[])
    
    # Relationships
    hackathon = db.relationship('Hackathon', backref='teams')
    leader = db.relationship('User', backref='led_teams')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team_code = self._generate_team_code()
        if self.leader_id not in self.members:
            self.members.append(self.leader_id)

    def _generate_team_code(self):
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(chars, k=6))
        while Team.query.filter_by(team_code=code).first():
            code = ''.join(random.choices(chars, k=6))
        return code

    @property
    def current_members(self):
        return len(self.members)

    @property
    def is_full(self):
        return self.current_members >= self.max_members

    def to_dict(self):
        return {
            'id': self.id,
            'team_name': self.team_name,
            'team_code': self.team_code,
            'hackathon_id': self.hackathon_id,
            'hackathon_title': self.hackathon.title if self.hackathon else None,
            'leader_id': self.leader_id,
            'leader_name': self.leader.name if self.leader else None,
            'members': self.members,
            'max_members': self.max_members,
            'current_members': self.current_members,
            'is_full': self.is_full,
            'created_at': self.created_at.isoformat()
        }

    def add_member(self, clerk_id):
        if clerk_id in self.members:
            raise ValueError("User already in team")
        if self.is_full:
            raise ValueError(f"Team is full (max {self.max_members} members)")
        self.members.append(clerk_id)

    def remove_member(self, clerk_id):
        if clerk_id not in self.members:
            raise ValueError("User not in team")
        if clerk_id == self.leader_id:
            raise ValueError("Cannot remove team leader")
        self.members.remove(clerk_id)