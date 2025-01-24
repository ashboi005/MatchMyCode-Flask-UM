from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from config import configure_app, db
from blueprints.auth.auth_bp import auth_bp
from blueprints.follow.follow_bp import follow_bp

app = Flask(__name__)
configure_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})

auth_bp = Blueprint('auth_bp', __name__)
follow_bp = Blueprint('follow_bp', __name__)

with app.app_context():
    db.create_all()

# Default Route
@app.route('/')
def hello():
    return "Hello World!"
    
if __name__ == "__main__":
    app.run(debug=True)
