from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User  
from flasgger import swag_from
from blueprints.mentor.models import Mentor  

mentor_bp = Blueprint('mentor_bp', __name__)

# POST - Create a new mentor
@swag_from({
    'tags': ['Mentors'],
    'summary': 'Create a new mentor',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clerkId': {'type': 'string'},
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'skills': {'type': 'array', 'items': {'type': 'string'}},  
                    'tags': {'type': 'array', 'items': {'type': 'string'}},   
                    'bio': {'type': 'string'}  # Bio field
                },
                'required': ['clerkId', 'name', 'email']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Mentor created successfully'
        },
        '400': {
            'description': 'Invalid input'
        }
    }
})
@mentor_bp.route('/create_mentor', methods=['POST'])
def create_mentor():
    data = request.get_json()

    # Check if the mentor already exists
    existing_mentor = Mentor.query.filter_by(clerkId=data['clerkId']).first()
    if existing_mentor:
        return jsonify({"message": "Mentor with this clerkId already exists"}), 400

    new_mentor = Mentor(
        clerkId=data['clerkId'],
        name=data['name'],
        email=data['email'],
        phone_number=data.get('phone_number'),
        skills=data.get('skills', []),  # Default to empty list if no skills are provided
        tags=data.get('tags', []),      # Default to empty list if no tags are provided
        bio=data.get('bio', '')         # Default to empty string if no bio is provided
    )

    db.session.add(new_mentor)
    db.session.commit()
    return jsonify({"message": "Mentor created successfully"}), 201


# GET - Fetch mentor details by clerkId
@swag_from({
    'tags': ['Mentors'],
    'summary': 'Get mentor details by clerkId',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'path',
            'required': True,
            'type': 'string'
        }
    ],
    'responses': {
        '200': {
            'description': 'Mentor details fetched successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'clerkId': {'type': 'string'},
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'skills': {'type': 'array', 'items': {'type': 'string'}},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'bio': {'type': 'string'}
                }
            }
        },
        '404': {
            'description': 'Mentor not found'
        }
    }
})
@mentor_bp.route('/mentor/<clerkId>', methods=['GET'])
def get_mentor(clerkId):
    mentor = Mentor.query.filter_by(clerkId=clerkId).first()
    if mentor:
        return jsonify({
            'clerkId': mentor.clerkId,
            'name': mentor.name,
            'email': mentor.email,
            'phone_number': mentor.phone_number,
            'skills': mentor.skills,
            'tags': mentor.tags,
            'bio': mentor.bio
        }), 200
    return jsonify({"message": "Mentor not found"}), 404


# DELETE - Delete a mentor by clerkId
@swag_from({
    'tags': ['Mentors'],
    'summary': 'Delete a mentor by clerkId',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'path',
            'required': True,
            'type': 'string'
        }
    ],
    'responses': {
        '200': {
            'description': 'Mentor deleted successfully'
        },
        '404': {
            'description': 'Mentor not found'
        }
    }
})
@mentor_bp.route('/mentor/<clerkId>', methods=['DELETE'])
def delete_mentor(clerkId):
    mentor = Mentor.query.filter_by(clerkId=clerkId).first()
    if mentor:
        db.session.delete(mentor)
        db.session.commit()
        return jsonify({"message": "Mentor deleted successfully"}), 200
    return jsonify({"message": "Mentor not found"}), 404
