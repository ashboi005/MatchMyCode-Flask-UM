from config import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    role = db.Column(db.String(50), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, clerkId, email, phone_number, role):
        self.clerkId = clerkId
        self.email = email
        self.phone_number = phone_number
        self.role = role

    user_details = db.relationship('UserDetails', back_populates='user', uselist=False, foreign_keys='UserDetails.clerkid')
    follow = db.relationship('Follow', back_populates='user', uselist=False, foreign_keys='Follow.clerkid')

