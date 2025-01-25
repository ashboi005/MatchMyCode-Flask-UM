from datetime import datetime
from config import db
from blueprints.auth.models import User

class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.String, db.ForeignKey('users.clerkId'), nullable=False, index=True)
    followed_id = db.Column(db.String, db.ForeignKey('users.clerkId'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to User model
    follower = db.relationship('User', foreign_keys=[follower_id])
    followed = db.relationship('User', foreign_keys=[followed_id])

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
    )