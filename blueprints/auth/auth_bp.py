from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User
from flasgger import swag_from
from blueprints.hackathon.models import Hackathon
from blueprints.chat.models import Chat


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


# Create Open Group (Admin only)
@auth_bp.route('/create-open-group', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Create a new open group (Admin only)',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'clerkId': {'type': 'string'},
                'topic': {'type': 'string'},
                'description': {'type': 'string'}
            },
            'required': ['clerkId', 'topic']
        }
    }],
    'responses': {
        201: {'description': 'Group created'},
        403: {'description': 'Admin privileges required'},
        409: {'description': 'Group already exists'}
    }
})
def create_open_group():
    data = request.json
    admin = User.query.filter_by(clerkId=data['clerkId'], role='admin').first()
    if not admin:
        return jsonify({"error": "Admin privileges required"}), 403
    
    topic_slug = data['topic'].lower().replace(' ', '-')
    room_id = f"open-{topic_slug}"
    
    if Chat.query.filter_by(room_id=room_id).first():
        return jsonify({"error": "Group already exists"}), 409
    
    new_group = Chat(
        room_id=room_id,
        is_group=True,
        is_open_group=True,
        topic=data['topic'],
        description=data.get('description'),
        created_by=data['clerkId'],
        participants=[]
    )
    db.session.add(new_group)
    db.session.commit()
    
    return jsonify({
        "room_id": room_id,
        "topic": data['topic'],
        "description": data.get('description')
    }), 201

# Get All Open Groups
@auth_bp.route('/open-groups', methods=['GET'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Get list of all open groups',
    'responses': {
        200: {
            'description': 'List of open groups',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'room_id': {'type': 'string'},
                        'topic': {'type': 'string'},
                        'description': {'type': 'string'},
                        'participant_count': {'type': 'integer'}
                    }
                }
            }
        }
    }
})
def get_open_groups():
    groups = Chat.query.filter_by(is_open_group=True).all()
    return jsonify([{
        'room_id': g.room_id,
        'topic': g.topic,
        'description': g.description,
        'participant_count': len(g.participants),
        'participants': g.participants
    } for g in groups])

# Get Group Details
@auth_bp.route('/open-group/<topic_slug>', methods=['GET'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Get open group details by topic slug',
    'parameters': [{
        'name': 'topic_slug',
        'in': 'path',
        'type': 'string',
        'required': True
    }],
    'responses': {
        200: {'description': 'Group details'},
        404: {'description': 'Group not found'}
    }
})
def get_open_group_details(topic_slug):
    group = Chat.query.filter_by(room_id=f"open-{topic_slug}").first()
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    return jsonify({
        'room_id': group.room_id,
        'topic': group.topic,
        'description': group.description,
        'participants': group.participants,
        'created_at': group.created_at.isoformat()
    })

