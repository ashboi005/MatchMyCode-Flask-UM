from datetime import datetime
from config import db

class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.String, db.ForeignKey('users.clerkId'), nullable=False, index=True)
    followed_id = db.Column(db.String, db.ForeignKey('users.clerkId'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Use back_populates to explicitly link relationships
    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='following_relationships')
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='follower_relationships')

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
    )