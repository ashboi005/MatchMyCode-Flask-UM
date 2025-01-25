from config import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class OrganiserDetails(db.Model):
    __tablename__ = 'organiser_details'

    # Required Fields
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), db.ForeignKey('users.clerkId'), unique=True, nullable=False)
    role = db.Column(db.String(50), default='organiser', nullable=False)
    
    # Organiser-Specific Fields (No duplicates of User fields)
    organization = db.Column(db.String(255))
    website = db.Column(db.String(255))
    bio = db.Column(db.Text)
    socials = db.Column(JSONB, default={})
    tags = db.Column(JSONB, default=[])
    
    # Timestamps
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='organiser_details')

    def __init__(self, clerkId, **kwargs):
        self.clerkId = clerkId
        self.role = 'organiser'
        self.organization = kwargs.get('organization')
        self.website = kwargs.get('website')
        self.bio = kwargs.get('bio')
        self.socials = kwargs.get('socials', {})
        self.tags = kwargs.get('tags', [])

    def to_dict(self):
        return {
            # User Info from User table
            'clerkId': self.user.clerkId,
            'name': self.user.name,
            'email': self.user.email,
            'phone_number': self.user.phone_number,
            
            # Organiser-Specific Info
            'role': self.role,
            'organization': self.organization,
            'website': self.website,
            'bio': self.bio,
            'socials': self.socials,
            'tags': self.tags,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat()
        }
