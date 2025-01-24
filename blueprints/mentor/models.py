from config import db

class Mentor(db.Model):
    __tablename__ = 'mentor'

    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), db.ForeignKey('user.clerkId'), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    skills = db.Column(db.ARRAY(db.String), nullable=True)  # List of skills (stored as an array of strings)
    tags = db.Column(db.ARRAY(db.String), nullable=True)    # List of tags (stored as an array of strings)
    bio = db.Column(db.String, nullable=True)               # Mentor's bio

    # Define relationships if necessary
    user = db.relationship('User', back_populates='mentor', uselist=False, foreign_keys=[clerkId])

    def __init__(self, clerkId, name, email, phone_number=None, skills=None, tags=None, bio=None):
        self.clerkId = clerkId
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.skills = skills or []  # Default to empty list if no skills are provided
        self.tags = tags or []      # Default to empty list if no tags are provided
        self.bio = bio or ''        # Default to empty string if no bio is provided

    def __repr__(self):
        return f"<Mentor {self.name}>"
