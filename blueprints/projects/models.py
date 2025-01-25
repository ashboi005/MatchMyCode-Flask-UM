from config import db
from sqlalchemy.dialects.postgresql import JSONB

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    clerkId = db.Column(db.String(255), db.ForeignKey('users.clerkId'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    big_description = db.Column(db.Text, nullable=False)
    tags = db.Column(JSONB, nullable=True)
    progress = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.String(255), nullable=True)
    goals = db.Column(db.Text, nullable=True)
    skills_required = db.Column(JSONB, nullable=True)
    project_status = db.Column(db.String(50), nullable=False, default='open')
    project_links = db.Column(JSONB, nullable=True)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    user = db.relationship('User', foreign_keys=[clerkId])

    def __init__(
        self,
        clerkId,
        name,
        title,
        short_description,
        big_description,
        tags=None,
        progress=None,
        duration=None,
        goals=None,
        skills_required=None,
        project_status='open',
        project_links=None
    ):
        self.clerkId = clerkId
        self.name = name
        self.title = title
        self.short_description = short_description
        self.big_description = big_description
        self.tags = tags
        self.progress = progress
        self.duration = duration
        self.goals = goals
        self.skills_required = skills_required
        self.project_status = project_status
        self.project_links = project_links

    def to_dict(self):
        return {
            'id': self.id,
            'clerkId': self.clerkId,
            'name': self.name,
            'title': self.title,
            'short_description': self.short_description,
            'big_description': self.big_description,
            'tags': self.tags,
            'progress': self.progress,
            'duration': self.duration,
            'goals': self.goals,
            'skills_required': self.skills_required,
            'project_status': self.project_status,
            'project_links': self.project_links,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }