#Flask App related imports
from flask import Flask
from flask_cors import CORS
from config import configure_app, db
from flasgger import Swagger
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os

#Blueprints imports
from blueprints.auth.auth_bp import auth_bp
from blueprints.follow.follow_bp import follow_bp
from blueprints.user.user_bp import user_bp
from blueprints.mentor.mentor_bp import mentors_bp
from blueprints.reviews.reviews_bp import reviews_bp
from blueprints.organiser.organiser_bp import organiser_bp
from blueprints.projects.projects_bp import projects_bp

#Models imports
from blueprints.hackathon.hackathon_bp import hackathon_bp
from blueprints.auth.models import User
from blueprints.follow.models import Follow
from blueprints.user.models import UserDetails
from blueprints.mentor.models import MentorDetails
from blueprints.reviews.models import Review
from blueprints.projects.models import Project
from blueprints.organiser.models import OrganiserDetails
from blueprints.hackathon.models import Hackathon

app = Flask(__name__)
configure_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
swagger = Swagger(app) 

scheduler = BackgroundScheduler()
scheduler.start()

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(follow_bp, url_prefix='/follow')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(mentors_bp, url_prefix='/mentor')
app.register_blueprint(reviews_bp, url_prefix='/reviews')
app.register_blueprint(organiser_bp, url_prefix='/organisers')
app.register_blueprint(projects_bp, url_prefix='/projects')
app.register_blueprint(hackathon_bp, url_prefix='/hackathon')

with app.app_context():
    db.create_all()

def update_hackathon_statuses():
    with app.app_context():
        from blueprints.hackathon.models import Hackathon  # Import inside context
        now = datetime.utcnow()
        hackathons = Hackathon.query.filter(
            Hackathon.status.in_(['approved', 'live'])
        ).all()
        
        for hackathon in hackathons:
            if hackathon.start_date <= now <= hackathon.end_date:
                hackathon.status = 'live'
            elif now > hackathon.end_date:
                hackathon.status = 'expired'
                hackathon.registration_deadline = now
            db.session.commit()

scheduler = None

def initialize_scheduler():
    global scheduler
    if not scheduler:
        # Initialize only if not already running
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_hackathon_statuses, 'interval', minutes=1)
        
        # Start only in the main process (avoid duplicate in debug reload)
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            if not scheduler.running:
                scheduler.start()
            else:
                print("Scheduler already running")


       
# Default Route 
@app.route('/')
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run(debug=True)
    initialize_scheduler()
else:
    with app.app_context():
        initialize_scheduler()


@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler and scheduler.running:
        scheduler.shutdown()
