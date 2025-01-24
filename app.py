from flask import Flask, request, jsonify
from flask_cors import CORS
from config import configure_app, db
from models import Test

app = Flask(__name__)
configure_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})


with app.app_context():
    db.create_all()

# Default Route
@app.route('/')
def hello():
    return "Hello World!"
    
if __name__ == "__main__":
    app.run(debug=True)
