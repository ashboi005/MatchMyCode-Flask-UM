from config import db

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), db.ForeignKey('user.clerkId'), nullable=False)
    follower_clerkId = db.Column(db.String(255), nullable=False)
    followed_clerkId = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='follow', foreign_keys=[clerkId])

    def __init__(self, clerkId, follower_clerkId, followed_clerkId):
        self.clerkId = clerkId
        self.follower_clerkId = follower_clerkId
        self.followed_clerkId = followed_clerkId

