from flask import Blueprint, request, jsonify
from config import db
from blueprints.reviews.models import Review
from blueprints.user.models import UserDetails  
from flasgger import swag_from

reviews_bp = Blueprint('reviews_bp', __name__)

# CREATE REVIEW ROUTE
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Create a new review',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_clerkId': {'type': 'string', 'example': 'user_123'},
                    'reviewer_clerkId': {'type': 'string', 'example': 'user_456'},
                    'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'comment': {'type': 'string', 'example': 'Great mentor!'}
                },
                'required': ['user_clerkId', 'reviewer_clerkId', 'rating']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Review created successfully',
            'examples': {'message': 'Review created successfully'}
        },
        400: {
            'description': 'Invalid input',
            'examples': {'error': 'Missing required fields'}
        },
        404: {
            'description': 'User not found',
            'examples': {'error': 'User or reviewer not found'}
        }
    }
})
@reviews_bp.route('/create_review', methods=['POST'])
def create_review():
    data = request.get_json()
    
    try:
        # Check required fields
        required = ['user_clerkId', 'reviewer_clerkId', 'rating']
        if not all(field in data for field in required):
            return jsonify({"error": "Missing required fields"}), 400

        # Start a fresh transaction
        db.session.begin()

        # Check user existence
        user = UserDetails.query.filter_by(clerkId=data['user_clerkId']).first()
        reviewer = UserDetails.query.filter_by(clerkId=data['reviewer_clerkId']).first()
        
        if not user or not reviewer:
            db.session.rollback()
            return jsonify({"error": "User or reviewer not found"}), 404

        # Check for existing review
        existing_review = Review.query.filter_by(
            user_clerkId=data['user_clerkId'],
            reviewer_clerkId=data['reviewer_clerkId']
        ).first()

        if existing_review:
            db.session.rollback()
            return jsonify({"error": "You have already reviewed this user"}), 409

        # Create and add review
        new_review = Review(
            user_clerkId=data['user_clerkId'],
            reviewer_clerkId=data['reviewer_clerkId'],
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        return jsonify({"message": "Review created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# GET REVIEWS FOR A USER ROUTE
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Get reviews for a user',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Clerk ID of the user',
            'example': 'user_123'
        }
    ],
    'responses': {
        200: {
            'description': 'List of reviews',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'reviewer': {'type': 'string'},
                        'rating': {'type': 'integer'},
                        'comment': {'type': 'string'},
                        'created_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        404: {
            'description': 'User not found',
            'examples': {'error': 'User not found'}
        }
    }
})
@reviews_bp.route('/get_reviews/<string:clerkId>', methods=['GET'])
def get_reviews(clerkId):
    # Check if user exists in UserDetails
    user = UserDetails.query.filter_by(clerkId=clerkId).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get reviews with reviewer details
    reviews = Review.query.filter_by(user_clerkId=clerkId).all()
    
    return jsonify([{
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.isoformat()
    } for review in reviews]), 200