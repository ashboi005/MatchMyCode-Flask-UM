from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User
from flasgger import swag_from

auth_bp = Blueprint('auth_bp', __name__)


#CREATE USER ROUTE
@swag_from({
    'tags': ['Auth'],
    'summary': 'Create a new user',
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
                    'role': {'type': 'string'}
                },
                'required': ['clerkId', 'name', 'email', 'role']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'User created successfully'
        },
        '400': {
            'description': 'Invalid input'
        }
    }
})
@auth_bp.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        clerkId=data['clerkId'],
        name=data['name'],
        email=data['email'],
        phone_number=data.get('phone_number'),
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201


#UPGRADE USER ROLE ROUTE
@swag_from({
    'tags': ['Auth'],
    'summary': 'Upgrade user role',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'path',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'role': {'type': 'string'}
                },
                'required': ['role']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'User role updated successfully'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
@auth_bp.route('/upgrade_role/<clerkId>', methods=['PUT'])
def upgrade_role(clerkId):
    data = request.get_json()
    user = User.query.filter_by(clerkId=clerkId).first()
    if user:
        user.role = data['role']
        db.session.commit()
        return jsonify({"message": "User role updated successfully"}), 200
    return jsonify({"message": "User not found"}), 404


#DELETE USER ROUTE
@swag_from({
    'tags': ['Auth'],
    'summary': 'Delete a user',
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
            'description': 'User deleted successfully'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
@auth_bp.route('/delete_user/<clerkId>', methods=['DELETE'])
def delete_user(clerkId):
    user = User.query.filter_by(clerkId=clerkId).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"message": "User not found"}), 404

