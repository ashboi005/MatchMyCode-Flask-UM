from config import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
from blueprints.reviews.models import Review
from blueprints.auth.models import User

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    portfolio_links = db.Column(JSONB, nullable=True)
    tags = db.Column(JSONB, nullable=True)
    skills = db.Column(JSONB, nullable=True)
    interests = db.Column(db.Text, nullable=True)
    socials = db.Column(JSONB, nullable=True)
    ongoing_project_links = db.Column(JSONB, nullable=True)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    verified = db.Column(db.Boolean, default=False)
    average_rating = db.Column(db.Float, nullable=True)

    user = db.relationship('User', back_populates='user_details', foreign_keys=[clerkId])

    def to_dict(self):
        return {
            'clerkId': self.clerkId,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role,
            'bio': self.bio,
            'portfolio_links': self.portfolio_links,
            'tags': self.tags,
            'skills': self.skills,
            'interests': self.interests,
            'socials': self.socials,
            'ongoing_project_links': self.ongoing_project_links,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'verified': self.verified,
            'average_rating': self.average_rating
        }

    @hybrid_property
    def average_rating(self):
        return db.session.query(func.avg(Review.rating))\
                        .filter(Review.user_clerkId == self.clerkId)\
                        .scalar()

    def __init__(self, clerkId, name, email, phone_number, role, bio, portfolio_links, tags, skills, interests, ongoing_project_links, socials, city=None, state=None, country=None, verified=False, average_rating=None):
        self.clerkId = clerkId
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.role = role
        self.bio = bio
        self.portfolio_links = portfolio_links
        self.tags = tags
        self.skills = skills
        self.interests = interests
        self.socials = socials
        self.ongoing_project_links = ongoing_project_links
        self.city = city
        self.state = state
        self.country = country
        self.verified = verified
        self.average_rating = average_rating
