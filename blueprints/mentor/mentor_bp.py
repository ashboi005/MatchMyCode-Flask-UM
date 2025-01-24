from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User
from flasgger import swag_from
from blueprints.mentor.models import Mentor

mentor_bp = Blueprint('mentor_bp', __name__)