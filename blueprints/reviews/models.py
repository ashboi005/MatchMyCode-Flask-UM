from config import db
from datetime import datetime

# blueprints/reviews/models.py
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_clerkId = db.Column(db.String, db.ForeignKey('user_details.clerkId'), nullable=False)
    reviewer_clerkId = db.Column(db.String, db.ForeignKey('user_details.clerkId'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # CORRECTED RELATIONSHIPS
    user = db.relationship(
        'UserDetails', 
        foreign_keys=[user_clerkId],
        backref=db.backref('received_reviews', lazy='dynamic')
    )
    reviewer = db.relationship(
        'UserDetails', 
        foreign_keys=[reviewer_clerkId],
        backref=db.backref('given_reviews', lazy='dynamic')
    )

    def __repr__(self):
        return f'<Review by {self.reviewer.name} for {self.user.name}>'