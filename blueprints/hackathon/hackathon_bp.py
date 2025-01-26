from flask import Blueprint, request, jsonify
from config import db
from flasgger import swag_from
from blueprints.auth.models import User
from blueprints.hackathon.models import Hackathon,ProjectSubmission
from blueprints.registration.models import Team

from datetime import datetime

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
                'max_team_size': {'type': 'integer', 'minimum': 1, 'maximum': 6},
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
                'registration_deadline',
                'max_team_size'
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
        max_team_size = data['max_team_size']
        if not (1 <= max_team_size <= 6):
            return jsonify({"error": "max_team_size must be between 1 and 6"}), 400

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
            max_team_size=max_team_size,
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
                    'max_team_size': {'type': 'integer', 'minimum': 1, 'maximum': 6},
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
        'title', 'description', 'mode', 'max_team_size', 'address', 'tags',
        'category', 'prize_money', 'themes', 'rules', 'additional_info'
    ]
    
    if 'max_team_size' in data:
        new_size = data['max_team_size']
        if not (1 <= new_size <= 6):
            return jsonify({"error": "max_team_size must be between 1 and 6"}), 400
    
    for field in updatable_fields:
        if field in data:
            setattr(hackathon, field, data[field])
    
    if 'winners' in data and hackathon.status == 'expired':
        hackathon.winners = data['winners']
    
    hackathon.updated_at = datetime.utcnow()
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

@hackathon_bp.route('/<int:hackathon_id>', methods=['GET'])
@swag_from({
    'tags': ['Hackathon'],
    'summary': 'Get hackathon details',
    'parameters': [{
        'name': 'hackathon_id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'responses': {
        200: {'description': 'Hackathon details', 'schema': {'$ref': '#/definitions/Hackathon'}},
        404: {'description': 'Hackathon not found'}
    }
})
def get_hackathon(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    return jsonify(hackathon.to_dict()), 200


@hackathon_bp.route('/submit_project', methods=['POST'])
@swag_from({
    'tags': ['Hackathon'],
    'summary': 'Submit project for a hackathon',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'hackathon_id': {'type': 'integer'},
                'team_code': {'type': 'string'},
                'github_link': {'type': 'string'},
                'live_demo_link': {'type': 'string'}
            },
            'required': ['hackathon_id', 'team_code', 'github_link']
        }
    }],
    'responses': {
        201: {'description': 'Project submitted successfully'},
        400: {'description': 'Invalid input or hackathon not live'},
        403: {'description': 'Unauthorized'},
        404: {'description': 'Hackathon or team not found'}
    }
})
def submit_project():
    data = request.get_json()
    hackathon = Hackathon.query.get(data['hackathon_id'])
    team = Team.query.filter_by(team_code=data['team_code']).first()

    # Validate hackathon and team
    if not hackathon:
        return jsonify({"error": "Hackathon not found"}), 404
    if not team:
        return jsonify({"error": "Team not found"}), 404

    # Check hackathon status
    if hackathon.status != 'live':
        return jsonify({"error": "Project submission is only allowed when hackathon is live"}), 400

    # Check if team is part of the hackathon
    if team.hackathon_id != hackathon.id:
        return jsonify({"error": "Team is not part of this hackathon"}), 400

    # Check if team has already submitted
    existing_submission = ProjectSubmission.query.filter_by(
        hackathon_id=hackathon.id,
        team_code=team.team_code
    ).first()
    if existing_submission:
        return jsonify({"error": "Project already submitted for this hackathon"}), 400

    # Create new submission
    submission = ProjectSubmission(
        hackathon_id=hackathon.id,
        team_code=team.team_code,
        github_link=data['github_link'],
        live_demo_link=data.get('live_demo_link')
    )

    try:
        db.session.add(submission)
        db.session.commit()
        return jsonify({"message": "Project submitted successfully", "submission": submission.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500