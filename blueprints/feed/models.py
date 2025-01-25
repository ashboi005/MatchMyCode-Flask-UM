from config import db

class FeedRequestProject(db.Model):
    __tablename__ = 'feed_requests_projects'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    clerkid_sender = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    clerkid_receiver = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), nullable=False, default='pending')

    project = db.relationship('Project', backref='feed_requests_projects')
    sender = db.relationship('User', foreign_keys=[clerkid_sender])
    receiver = db.relationship('User', foreign_keys=[clerkid_receiver])

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'clerkid_sender': self.clerkid_sender,
            'clerkid_receiver': self.clerkid_receiver,
            'message': self.message,
            'created_at': self.created_at,
            'status': self.status
        }

class FeedRequestPerson(db.Model):
    __tablename__ = 'feed_requests_people'
    id = db.Column(db.Integer, primary_key=True)
    clerkid_sender = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    clerkid_receiver = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), nullable=False, default='pending')

    sender = db.relationship('User', foreign_keys=[clerkid_sender])
    receiver = db.relationship('User', foreign_keys=[clerkid_receiver])

    def to_dict(self):
        return {
            'id': self.id,
            'clerkid_sender': self.clerkid_sender,
            'clerkid_receiver': self.clerkid_receiver,
            'message': self.message,
            'created_at': self.created_at,
            'status': self.status
        }


