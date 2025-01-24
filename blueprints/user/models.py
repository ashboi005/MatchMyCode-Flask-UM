from config import db

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), db.ForeignKey('user.clerkId'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    portfolio_links = db.Column(db.JSON, nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    skills = db.Column(db.JSON, nullable=True)
    interests = db.Column(db.Text, nullable=True)
    socials = db.Column(db.JSON, nullable=True)
    ongoing_project_links = db.Column(db.JSON, nullable=True)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    user = db.relationship('User', back_populates='user_details', foreign_keys=[clerkId])

    def __init__(self, clerkId, name, email, phone_number, role, bio, portfolio_links, tags, skills, interests, ongoing_project_links, socials):
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