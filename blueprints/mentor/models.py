from config import db

class MentorDetails(db.Model):
    __tablename__ = 'mentor_details'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    clerkId = db.Column(db.String(255),db.ForeignKey('user.clerkId'),unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(50), nullable=False)
    
    # Location Information
    city = db.Column(db.String(255), nullable=True)  # City of the mentor
    state = db.Column(db.String(255), nullable=True)  # State of the mentor
    country = db.Column(db.String(255), nullable=True)  # Country of the mentor
    
    # Detailed Information
    bio = db.Column(db.String, nullable=True)  # Short description of the mentor's background
    portfolio_links = db.Column(db.ARRAY(db.String), nullable=True)  # Links to portfolio or projects
    tags = db.Column(db.ARRAY(db.String), nullable=True)  # Tags for the mentor's expertise (e.g., #Python, #WebDev)
    skills = db.Column(db.ARRAY(db.String), nullable=True)  # List of skills (e.g., ["Python", "Machine Learning"])
    interests = db.Column(db.ARRAY(db.String), nullable=True)  # Interests (e.g., ["AI", "Blockchain"])
    
    # Social Media Links
    socials = db.Column(db.ARRAY(db.String), nullable=True)  # Social media links (e.g., LinkedIn, GitHub, etc.)
    
    # Ongoing Project Links
    ongoing_project_links = db.Column(db.ARRAY(db.String), nullable=True)  # Links to current projects
    
    # Education & Experience
    education = db.Column(db.String(255), nullable=True)  # Education background (degree, university, etc.)
    experience_years = db.Column(db.Integer, nullable=True)  # Number of years of experience

    # Timestamps
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    mentor = db.relationship('User', back_populates='mentor_details', foreign_keys=[clerkId])


    def to_dict(self):
        return {
            'id': self.id,
            'clerkId': self.clerkId,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role,
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
            'updatedAt': self.updatedAt
        }

    
    
    
    def __init__(self, clerkId, name, email, phone_number, role, bio=None, portfolio_links=None, tags=None, 
                 skills=None, interests=None, socials=None, ongoing_project_links=None, education=None, 
                 experience_years=None, city=None, state=None, country=None):
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



