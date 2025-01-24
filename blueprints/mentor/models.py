from config import db

class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), db.ForeignKey('user.clerkId'), nullable=False)


    def __init__(self, clerkId):
        self.clerkId = clerkId
        
    user = db.relationship('User', backref='mentor', uselist=False)