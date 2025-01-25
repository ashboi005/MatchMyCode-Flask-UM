from config import db
from sqlalchemy.dialects.postgresql import JSONB  # Import JSONB

class MentorDetails(db.Model):
    __tablename__ = 'mentor_details'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    clerkId = db.Column(db.String(255), db.ForeignKey('users.clerkId'), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=True)  # Biography of the mentor
    portfolio_links = db.Column(JSONB, nullable=True)  # Links to portfolio or projects
    tags = db.Column(JSONB, nullable=True)  # Tags for the mentor's expertise (e.g., #Python, #WebDev)
    skills = db.Column(JSONB, nullable=True)  # List of skills (e.g., ["Python", "Machine Learning"])
    interests = db.Column(JSONB, nullable=True)  # Interests (e.g., ["AI", "Blockchain"])
    socials = db.Column(JSONB, nullable=True)  # Social media links (e.g., LinkedIn, GitHub, etc.)
    ongoing_project_links = db.Column(JSONB, nullable=True)  # Links to current projects
    
    # Location Information
    city = db.Column(db.String(255), nullable=True)  # City of the mentor
    state = db.Column(db.String(255), nullable=True)  # State of the mentor
    country = db.Column(db.String(255), nullable=True)  # Country of the mentor
    

    # Education & Experience
    education = db.Column(db.String(255), nullable=True)  # Education background (degree, university, etc.)
    experience_years = db.Column(db.Integer, nullable=True)  # Number of years of experience

    # Timestamps
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Verification status
    verified = db.Column(db.Boolean, default=False)

    mentor = db.relationship('User', back_populates='mentor_details', foreign_keys=[clerkId])

    def to_dict(self):
        return {
            'id': self.id,
            'clerkId': self.clerkId,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role,
            'bio': self.bio,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'bio': self.bio,
            'portfolio_links': self.portfolio_links,
            'tags': self.tags,
            'skills': self.skills,
            'interests': self.interests,
            'socials': self.socials,
            'ongoing_project_links': self.ongoing_project_links,
            'education': self.education,
            'experience_years': self.experience_years,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'verified': self.verified
        }

    def __init__(self, clerkId, name, email, phone_number, role, bio=None, portfolio_links=None, tags=None, 
                 skills=None, interests=None, socials=None, ongoing_project_links=None, education=None, 
                 experience_years=None, city=None, state=None, country=None, verified=False):
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
        self.education = education
        self.experience_years = experience_years
        self.city = city
        self.state = state
        self.country = country
        self.verified = verified



