from config import db

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clerkid = db.Column(db.String(255), db.ForeignKey('user.clerkId'), nullable=False)
    follower_clerkid = db.Column(db.String(255), nullable=False)
    followed_clerkid = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='follow', foreign_keys=[clerkid])

    def __init__(self, clerkid, follower_clerkid, followed_clerkid):
        self.clerkid = clerkid
        self.follower_clerkid = follower_clerkid
        self.followed_clerkid = followed_clerkid