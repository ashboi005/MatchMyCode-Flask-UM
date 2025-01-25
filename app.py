from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from config import configure_app, db
from flasgger import Swagger
from blueprints.auth.auth_bp import auth_bp
from blueprints.follow.follow_bp import follow_bp
from blueprints.user.user_bp import user_bp
from blueprints.mentor.mentor_bp import mentors_bp
from blueprints.organiser.organiser_bp import organiser_bp
from blueprints.auth.models import User
from blueprints.follow.models import Follow
from blueprints.user.models import UserDetails
from blueprints.mentor.models import MentorDetails
from blueprints.organiser.models import OrganiserDetails


app = Flask(__name__)
configure_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
swagger = Swagger(app) 

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(follow_bp, url_prefix='/follow')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(mentors_bp, url_prefix='/mentor')
app.register_blueprint(organiser_bp, url_prefix='/organisers')


with app.app_context():
    db.create_all()

# Default Route 
@app.route('/')
def hello():
    return "Hello World!"
    
if __name__ == "__main__":
    app.run(debug=True)
