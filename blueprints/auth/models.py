from config import db

class User(db.Model):
    __tablename__ = 'users'
    clerkId = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    role = db.Column(db.String(50), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    user_details = db.relationship('UserDetails', back_populates='user', uselist=False)
    mentor_details = db.relationship('MentorDetails', back_populates='mentor', uselist=False)
    organiser_details = db.relationship('OrganiserDetails', back_populates='user', uselist=False)
    projects = db.relationship('Project', back_populates='user')

    # Updated relationships with back_populates
    following_relationships = db.relationship(
        'Follow', 
        foreign_keys='Follow.follower_id', 
        back_populates='follower',  # Link to Follow.follower
        lazy='dynamic'
    )
    
    follower_relationships = db.relationship(
        'Follow', 
        foreign_keys='Follow.followed_id', 
        back_populates='followed',  # Link to Follow.followed
        lazy='dynamic'
    )

    # In your User model
    @property
    def followers(self):
        return [rel.follower for rel in self.follower_relationships]

    @property
    def following(self):
        return [rel.followed for rel in self.following_relationships]

    def __init__(self, clerkId, name, email, phone_number, role):
        self.clerkId = clerkId
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.role = role


