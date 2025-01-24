from config import db

# class Follow(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     follower_clerkId = db.Column(db.String(255), db.ForeignKey('user.clerkId'), nullable=False)
#     followed_clerkId = db.Column(db.String(255), db.ForeignKey('user.clerkId'), nullable=False)
#     createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

#     follower = db.relationship('User', foreign_keys=[follower_clerkId], backref='following')
#     followed = db.relationship('User', foreign_keys=[followed_clerkId], backref='followers')

#     def __init__(self, follower_clerkId, followed_clerkId):
#         self.follower_clerkId = follower_clerkId
#         self.followed_clerkId = followed_clerkId

