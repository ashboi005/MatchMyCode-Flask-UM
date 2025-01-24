from config import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    role = db.Column(db.String(50), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, clerkId, name, email, phone_number, role):
        self.clerkId = clerkId
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.role = role

    user_details = db.relationship('UserDetails', back_populates='user', uselist=False, foreign_keys='UserDetails.clerkId')
    mentor = db.relationship('Mentor', back_populates='user', uselist=False, foreign_keys='Mentor.clerkId')
    # following = db.relationship('Follow', foreign_keys='Follow.follower_clerkId', backref='follower_user')
    # followers = db.relationship('Follow', foreign_keys='Follow.followed_clerkId', backref='followed_user')



