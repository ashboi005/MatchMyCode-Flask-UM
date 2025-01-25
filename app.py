# Flask App related imports
from flask import Flask, jsonify
from flask_cors import CORS
from flask_apscheduler import APScheduler
from config import configure_app, db
from flasgger import Swagger
from datetime import datetime
import pytz  # Add this import
import logging

# Blueprints imports
from blueprints.auth.auth_bp import auth_bp
from blueprints.user.user_bp import user_bp
from blueprints.mentor.mentor_bp import mentors_bp
from blueprints.reviews.reviews_bp import reviews_bp
from blueprints.organiser.organiser_bp import organiser_bp
from blueprints.projects.projects_bp import projects_bp
from blueprints.hackathon.hackathon_bp import hackathon_bp
from blueprints.hackathon.models import Hackathon

# Initialize Flask app
app = Flask(__name__)
configure_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
swagger = Swagger(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# APScheduler setup
scheduler = APScheduler()

# Timezone setup
IST = pytz.timezone('Asia/Kolkata')

def update_hackathon_statuses():
    """Update hackathon statuses based on IST"""
    with app.app_context():
        try:
            now = datetime.now(IST)  # Get current IST time
            logger.info(f"Running status update at IST: {now}")

            # Convert to naive datetime for SQLite comparison
            now_naive = now.replace(tzinfo=None)
            
            # Update live hackathons
            Hackathon.query.filter(
                Hackathon.status == 'approved',
                Hackathon.start_date <= now_naive,
                Hackathon.end_date >= now_naive
            ).update({'status': 'live'})

            # Expire finished hackathons
            Hackathon.query.filter(
                Hackathon.status.in_(['approved', 'live']),
                Hackathon.end_date < now_naive
            ).update({'status': 'expired'})

            db.session.commit()
            logger.info("Successfully updated hackathon statuses")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Status update failed: {str(e)}", exc_info=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(mentors_bp, url_prefix='/mentor')
app.register_blueprint(reviews_bp, url_prefix='/reviews')
app.register_blueprint(organiser_bp, url_prefix='/organisers')
app.register_blueprint(projects_bp, url_prefix='/projects')
app.register_blueprint(hackathon_bp, url_prefix='/hackathon')

# Initialize database and scheduler
with app.app_context():
    db.create_all()
    # Schedule status updates every minute
    scheduler.add_job(
        id='hackathon_status_updater',
        func=update_hackathon_statuses,
        trigger='interval',
        minutes=15
    )
    scheduler.init_app(app)
    scheduler.start()

# Default route
@app.route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)