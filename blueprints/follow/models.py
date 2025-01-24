from config import db
import re

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), db.ForeignKey('user.clerkId'), nullable=False)
    follower_clerkId = db.Column(db.String(255), nullable=False)
    followed_clerkId = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='follow', foreign_keys=[clerkId])

    def __init__(self, clerkId, follower_clerkId, followed_clerkId):
        # Ensure the clerkId is in the desired format (e.g., xxxx-xxxx-xxxx)
        self.clerkId = self.format_clerkid(clerkId)
        self.follower_clerkId = self.format_clerkid(follower_clerkId)
        self.followed_clerkId = self.format_clerkid(followed_clerkId)

    def format_clerkid(self, clerkId):
        """
        Formats clerkId by inserting dashes in the format: xxxx-xxxx-xxxx
        """
        if len(clerkId) == 12 and clerkId.isdigit():  # Check if it's a 12-digit number
            return f"{clerkId[:4]}-{clerkId[4:8]}-{clerkId[8:]}"
        else:
            raise ValueError("Invalid clerkId format. Expected 12-digit number.")
