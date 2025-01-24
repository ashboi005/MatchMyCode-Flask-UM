from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User
from flasgger import swag_from

follow_bp = Blueprint('follow_bp', __name__)