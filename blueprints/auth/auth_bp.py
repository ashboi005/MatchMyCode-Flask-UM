from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User
from flasgger import swag_from
from blueprints.hackathon.models import Hackathon




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
    existing_user = User.query.filter_by(clerkId=data['clerkId']).first()
    if existing_user:
        return jsonify({"message": "User with this clerkId already exists"}), 400

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

# Add to your auth_bp routes
@auth_bp.route('/approve_hackathon/<int:hackathon_id>', methods=['PUT'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Approve a pending hackathon (Admin only)',
    'parameters': [
        {
            'name': 'hackathon_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the hackathon to approve'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clerkId': {
                        'type': 'string',
                        'description': 'Admin Clerk ID'
                    }
                },
                'required': ['clerkId']
            }
        }
    ],
    'responses': {
        200: {'description': 'Hackathon approved successfully'},
        403: {'description': 'Admin privileges required'},
        404: {'description': 'Hackathon not found'},
        400: {'description': 'Invalid request'}
    }
})
def approve_hackathon(hackathon_id):
    data = request.get_json()
    try:
        # Verify admin user
        admin = User.query.filter_by(clerkId=data['clerkId']).first()
        if not admin or admin.role != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403

        # Get and validate hackathon
        hackathon = Hackathon.query.get_or_404(hackathon_id)
        if hackathon.status != 'pending':
            return jsonify({"error": "Hackathon is not in pending state"}), 400

        # Update status
        hackathon.status = 'approved'
        db.session.commit()
        return jsonify({
            "message": "Hackathon approved successfully",
            "hackathon": hackathon.to_dict()
        }), 200

    except KeyError:
        return jsonify({"error": "clerkId is required"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# VERIFY USER ROUTE (Mentor only)
@auth_bp.route('/verify_user/<user_clerkId>', methods=['PUT'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Verify a user account (Mentor only)',
    'parameters': [
        {
            'name': 'user_clerkId',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Clerk ID of user to verify'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'mentor_clerkId': {
                        'type': 'string',
                        'description': 'Mentor\'s Clerk ID'
                    }
                },
                'required': ['mentor_clerkId']
            }
        }
    ],
    'responses': {
        200: {'description': 'User verified successfully'},
        403: {'description': 'Mentor privileges required'},
        404: {'description': 'User not found'},
        400: {'description': 'User already verified'}
    }
})
def verify_user(user_clerkId):
    data = request.get_json()
    try:
        # Verify mentor credentials
        mentor = User.query.filter_by(clerkId=data['mentor_clerkId']).first()
        if not mentor or mentor.role != 'mentor':
            return jsonify({"error": "Mentor privileges required"}), 403

        # Get target user
        user = User.query.filter_by(clerkId=user_clerkId).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if user.status == 'verified':
            return jsonify({"error": "User already verified"}), 400

        # Update verification status
        user.status = 'verified'
        db.session.commit()
        return jsonify({"message": "User verified successfully"}), 200

    except KeyError:
        return jsonify({"error": "mentor_clerkId is required"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

