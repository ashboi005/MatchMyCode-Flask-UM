from flask import Blueprint, request, jsonify
from config import db
from flasgger import swag_from
from blueprints.auth.models import User
from blueprints.hackathon.models import Hackathon, UserHackathonRegistration
from datetime import datetime
import os

hackathon_bp = Blueprint('hackathon_bp', __name__, url_prefix='/hackathons')


@hackathon_bp.route('/create_hackathon', methods=['POST'])
@swag_from({
    'tags': ['Hackathon'],
    'summary': 'Create new hackathon',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'organiser_clerkId': {'type': 'string'},
                'title': {'type': 'string'},
                'description': {'type': 'string'},
                'start_date': {'type': 'string', 'format': 'date-time'},
                'end_date': {'type': 'string', 'format': 'date-time'},
                'mode': {'type': 'string', 'enum': ['online', 'offline']},
                'address': {'type': 'string'},
                'location': {'type': 'string'},
                'tags': {'type': 'array', 'items': {'type': 'string'}},
                'category': {'type': 'string'},
                'prize_money': {'type': 'number'},
                'registration_fees': {'type': 'string'},
                'registration_deadline': {'type': 'string', 'format': 'date-time'},
                'themes': {'type': 'array', 'items': {'type': 'string'}},
                'rules': {'type': 'array', 'items': {'type': 'string'}},
                'additional_info': {'type': 'object'}
            },
            'required': [
                'organiser_clerkId', 
                'title', 
                'description', 
                'start_date', 
                'end_date',
                'mode',
                'registration_deadline'
            ]
        }
    }],
    'responses': {
        201: {'description': 'Hackathon created'},
        400: {'description': 'Invalid input'},
        403: {'description': 'Unauthorized'}
    }
})
def create_hackathon():
    data = request.get_json()
    try:
        organiser = User.query.get(data['organiser_clerkId'])
        if not organiser or organiser.role != 'organiser':
            return jsonify({"error": "Unauthorized"}), 403

        hackathon = Hackathon(
            organiser_clerkId=data['organiser_clerkId'],
            title=data['title'],
            description=data['description'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            mode=data['mode'],
            address=data.get('address'),
            location=data.get('location'),
            tags=data.get('tags', []),
            category=data.get('category'),
            prize_money=data.get('prize_money'),
            registration_fees=data.get('registration_fees', 'free'),
            registration_deadline=datetime.fromisoformat(data['registration_deadline']),
            themes=data.get('themes', []),
            rules=data.get('rules', []),
            status='pending',
            additional_info=data.get('additional_info', {}),
            winners=[]
        )

        if hackathon.mode == 'offline' and not hackathon.address:
            return jsonify({"error": "Address required for offline hackathons"}), 400

        db.session.add(hackathon)
        db.session.commit()
        return jsonify(hackathon.to_dict()), 201
        
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@hackathon_bp.route('/update_hackathon_details/<int:hackathon_id>', methods=['PUT'])
@swag_from({
    'tags': ['Hackathon'],
    'summary': 'Update hackathon details',
    'parameters': [
        {
            'name': 'hackathon_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the hackathon to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'organiser_clerkId': {'type': 'string'},
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'mode': {'type': 'string', 'enum': ['online', 'offline']},
                    'address': {'type': 'string'},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'category': {'type': 'string'},
                    'prize_money': {'type': 'number'},
                    'themes': {'type': 'array', 'items': {'type': 'string'}},
                    'rules': {'type': 'array', 'items': {'type': 'string'}},
                    'additional_info': {'type': 'object'}
                },
                'required': ['organiser_clerkId']
            }
        }
    ],
    'responses': {
        200: {'description': 'Hackathon updated successfully'},
        403: {'description': 'Unauthorized'},
        404: {'description': 'Hackathon not found'},
        400: {'description': 'Invalid input'}
    }
})
def update_hackathon(hackathon_id):
    data = request.get_json()
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    
    if hackathon.organiser_clerkId != data.get('organiser_clerkId'):
        return jsonify({"error": "Unauthorized"}), 403
    
    updatable_fields = [
        'title', 'description', 'mode', 'address', 'tags', 
        'category', 'prize_money', 'themes', 'rules', 'additional_info'
    ]
    
    for field in updatable_fields:
        if field in data:
            setattr(hackathon, field, data[field])
    
    if 'winners' in data and hackathon.status == 'expired':
        hackathon.winners = data['winners']
    
    db.session.commit()
    return jsonify(hackathon.to_dict()), 200

@hackathon_bp.route('/hackathons_of_organiser/<string:clerk_id>', methods=['GET'])
@swag_from({
    'tags': ['Hackathon'],
    'summary': 'Get hackathons by organizer',
    'parameters': [
        {
            'name': 'clerk_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Clerk ID of the organizer'
        }
    ],
    'responses': {
        200: {
            'description': 'List of hackathons',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Hackathon'}
            }
        },
        404: {'description': 'Organizer not found'}
    }
})
def get_organiser_hackathons(clerk_id):
    hackathons = Hackathon.query.filter_by(organiser_clerkId=clerk_id).all()
    if not hackathons:
        return jsonify({"error": "No hackathons found for this organizer"}), 404
    return jsonify([h.to_dict() for h in hackathons]), 200

@hackathon_bp.route('/public_hackathons', methods=['GET'])
@swag_from({
    'tags': ['Hackathon'],
    'summary': 'Get all public hackathons',
    'responses': {
        200: {
            'description': 'List of public hackathons',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Hackathon'}
            }
        }
    }
})
def get_public_hackathons():
    hackathons = Hackathon.query.filter(
        Hackathon.status.in_(['approved', 'live', 'expired'])
    ).all()
    return jsonify([h.to_dict() for h in hackathons]), 200

@hackathon_bp.route('/<int:hackathon_id>/register_for_hackathon', methods=['POST'])
@swag_from({
    'tags': ['Hackathon'],
    'summary': 'Register for a hackathon',
    'parameters': [
        {
            'name': 'hackathon_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the hackathon to register for'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_clerkId': {'type': 'string'}
                },
                'required': ['user_clerkId']
            }
        }
    ],
    'responses': {
        201: {'description': 'Registration successful'},
        400: {'description': 'Registration closed or already registered'},
        404: {'description': 'Hackathon not found'}
    }
})
def register_for_hackathon(hackathon_id):
    data = request.get_json()
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    
    if datetime.utcnow() > hackathon.registration_deadline:
        return jsonify({"error": "Registration closed"}), 400
    
    existing = UserHackathonRegistration.query.filter_by(
        user_clerkId=data['user_clerkId'],
        hackathon_id=hackathon_id
    ).first()
    
    if existing:
        return jsonify({"error": "Already registered"}), 400
    
    registration = UserHackathonRegistration(
        user_clerkId=data['user_clerkId'],
        hackathon_id=hackathon_id
    )
    
    db.session.add(registration)
    db.session.commit()
    return jsonify({"message": "Registration successful"}), 201