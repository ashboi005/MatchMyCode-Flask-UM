from config import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class OrganiserDetails(db.Model):
    __tablename__ = 'organiser_details'

    # Required Fields
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(
        db.String(255), 
        db.ForeignKey('users.clerkId'), 
        unique=True, 
        nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(50), default='organiser', nullable=False)
    
    # Optional Fields
    phone_number = db.Column(db.String(20))
    organization = db.Column(db.String(255))
    website = db.Column(db.String(255))
    bio = db.Column(db.Text)
    socials = db.Column(JSONB, default={})  # {platform: username/url}
    tags = db.Column(JSONB, default=[])     # ["Tech", "Education"]
    
    # Timestamps
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    user = db.relationship('User', back_populates='organiser_details', foreign_keys=[clerkId])

    def __init__(
        self,
        clerkId,
        name,
        email,
        phone_number=None,
        organization=None,
        website=None,
        bio=None,
        socials=None,
        tags=None
    ):
        self.clerkId = clerkId
        self.name = name
        self.email = email
        self.role = 'organiser'  # Force role
        
        # Optional fields with safe defaults
        self.phone_number = phone_number
        self.organization = organization
        self.website = website
        self.bio = bio
        self.socials = socials if socials is not None else {}
        self.tags = tags if tags is not None else []

    def to_dict(self):
        return {
            'clerkId': self.clerkId,
            'name': self.user.name,
            'email': self.user.email,
            'role': self.role,
            'phone_number': self.phone_number,
            'organization': self.organization,
            'website': self.website,
            'bio': self.bio,
            'socials': self.socials,
            'tags': self.tags,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat()
        }