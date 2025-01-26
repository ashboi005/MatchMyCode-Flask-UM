from config import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import event
from blueprints.chat.models import Chat

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
    chat_room_id = db.Column(db.String(255), unique=True)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    user = db.relationship('User', foreign_keys=[clerkId])
    chat = db.relationship('Chat', backref='project', uselist=False)

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
            'updatedAt': self.updatedAt,
            'chat_room_id': self.chat_room_id,
            'has_chat': bool(self.chat)
        }
    
@event.listens_for(Project, 'after_insert')
def create_chat_room(mapper, connection, target):
    # Only create chat if project_status is 'open'
    if target.project_status != 'open':
        return
    
    # Generate chat_room_id after project has an ID
    chat_room_id = f"project-{target.id}"
    
    # Update the project's chat_room_id using the connection
    connection.execute(
        db.update(Project)
        .where(Project.id == target.id)
        .values(chat_room_id=chat_room_id)
    )
    
    # Create the chat room using raw SQL to avoid session conflicts
    connection.execute(
        db.insert(Chat.__table__).values(
            room_id=chat_room_id,
            is_group=True,
            participants=[target.clerkId],
            created_at=db.func.current_timestamp()
        )
    )