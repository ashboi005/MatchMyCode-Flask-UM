# registration_routes.py (updated)
from flask import Blueprint, request, jsonify
from config import db
from datetime import datetime
from flasgger import swag_from
from sqlalchemy.orm.attributes import flag_modified  # New import
from blueprints.auth.models import User
from blueprints.hackathon.models import Hackathon
from .models import Team
from blueprints.chat.models import Chat

registration_bp = Blueprint('registration', __name__)

@registration_bp.route('/create_team', methods=['POST'])
@swag_from({
    'tags': ['Registration'],
    'summary': 'Create a new team',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'clerkId': {'type': 'string'},
                'hackathon_id': {'type': 'integer'},
                'team_name': {'type': 'string'}
            },
            'required': ['clerkId', 'hackathon_id', 'team_name']
        }
    }],
    'responses': {
        201: {'description': 'Team created'},
        400: {'description': 'Invalid request'},
        403: {'description': 'Registration closed'}
    }
})
def create_team():
    data = request.get_json()
    user = User.query.get(data['clerkId'])
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    hackathon = Hackathon.query.get(data['hackathon_id'])
    
    # Validate registration conditions
    if not hackathon:
        return jsonify({'error': 'Hackathon not found'}), 404
    if hackathon.status in ['live', 'expired']:
        return jsonify({'error': 'Registration closed'}), 403
    if datetime.utcnow() > hackathon.registration_deadline:
        return jsonify({'error': 'Registration deadline passed'}), 403
        
    # Check existing team
    existing_team = Team.query.filter_by(
        leader_id=user.clerkId, 
        hackathon_id=hackathon.id
    ).first()
    if existing_team:
        return jsonify({'error': 'Already created team for this hackathon'}), 400

    # Create new team with organizer-defined max size
    new_team = Team(
        hackathon_id=hackathon.id,
        leader_id=user.clerkId,
        team_name=data['team_name'],
        max_members=hackathon.max_team_size
    )
    
    try:
        db.session.add(new_team)
        db.session.commit()
        return jsonify(new_team.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@registration_bp.route('/join_team', methods=['POST'])
@swag_from({
    'tags': ['Registration'],
    'summary': 'Join existing team',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'clerkId': {'type': 'string'},
                'team_code': {'type': 'string'},
                'hackathon_id': {'type': 'integer'}
            },
            'required': ['clerkId', 'team_code', 'hackathon_id']
        }
    }],
    'responses': {
        200: {'description': 'Joined team'},
        400: {'description': 'Invalid request'},
        403: {'description': 'Registration closed'}
    }
})
def join_team():
    data = request.get_json()
    user = User.query.get(data['clerkId'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Case-insensitive team code search
    team = Team.query.filter(Team.team_code.ilike(data['team_code'])).first()
    hackathon = Hackathon.query.get(data['hackathon_id'])
    
    # Validate team and hackathon
    if not team or not hackathon:
        return jsonify({'error': 'Invalid team code or hackathon'}), 400
    if team.hackathon_id != hackathon.id:
        return jsonify({'error': 'Team not part of this hackathon'}), 400
        
    # Check registration conditions
    if hackathon.status in ['live', 'expired']:
        return jsonify({'error': 'Registration closed'}), 403
    if datetime.utcnow() > hackathon.registration_deadline:
        return jsonify({'error': 'Registration deadline passed'}), 403
        
    # Check team membership
    if user.clerkId in team.members:
        return jsonify({'error': 'Already in team'}), 400
    if len(team.members) >= team.max_members:
        return jsonify({'error': f'Team full (max {team.max_members} members)'}), 400
    
    try:
        # Add user to team members
        team.members.append(user.clerkId)
        flag_modified(team, 'members')

        # Add user to the associated group chat (use chat_room_id)
        chat = Chat.query.filter_by(room_id=team.chat_room_id).first()
        if chat and user.clerkId not in chat.participants:
            chat.participants.append(user.clerkId)
            flag_modified(chat, 'participants')

        db.session.commit()
        return jsonify({'message': 'Joined team successfully', 'team': team.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@registration_bp.route('/announce_winner', methods=['POST'])  # Removed path parameter
@swag_from({
    'tags': ['Registration'],
    'summary': 'Announce hackathon winner',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'clerkId': {'type': 'string'},
                'winner_team_id': {'type': 'integer'},
                'hackathon_id': {'type': 'integer'}  # Added to request body
            },
            'required': ['clerkId', 'winner_team_id', 'hackathon_id']  # Updated requirements
        }
    }],
    'responses': {
        200: {'description': 'Winner announced'},
        403: {'description': 'Forbidden'},
        400: {'description': 'Invalid request'}
    }
})
def announce_winner():
    data = request.get_json()
    user = User.query.get(data['clerkId'])
    hackathon_id = data.get('hackathon_id')  # Get from request body
    
    # Authorization check
    if not user or user.role != 'organiser':
        return jsonify({'error': 'Unauthorized'}), 403
        
    hackathon = Hackathon.query.get(hackathon_id)
    if not hackathon:
        return jsonify({'error': 'Hackathon not found'}), 404
    if hackathon.status != 'expired':
        return jsonify({'error': 'Winner can only be announced for expired hackathons'}), 400
        
    team = Team.query.get(data['winner_team_id'])
    if not team or team.hackathon_id != hackathon_id:  # Verify team belongs to hackathon
        return jsonify({'error': 'Invalid winning team for this hackathon'}), 400
        
    try:
        if not hackathon.winners:
            hackathon.winners = []
        hackathon.winners.append(team.id)
        flag_modified(hackathon, 'winners')
        db.session.commit()
        return jsonify({
            'message': 'Winner announced successfully',
            'hackathon': hackathon.to_dict(),
            'winning_team': team.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@registration_bp.route('/get_hackathon_teams', methods=['GET'])
@swag_from({
    'tags': ['Registration'],
    'summary': 'Get all teams for a specific hackathon by Hackathon ID',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Clerk ID of the user requesting the teams'
        },
        {
            'name': 'hackathon_id',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'ID of the hackathon'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of teams retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'team_name': {'type': 'string'},
                        'team_code': {'type': 'string'},
                        'leader_id': {'type': 'string'},
                        'members': {'type': 'array', 'items': {'type': 'string'}},
                        'max_members': {'type': 'integer'},
                        'created_at': {'type': 'string', 'format': 'date-time'},
                        'chat_room_id': {'type': 'string'}
                    }
                }
            }
        },
        '400': {
            'description': 'Invalid input'
        },
        '403': {
            'description': 'Forbidden: Unauthorized access'
        },
        '404': {
            'description': 'Hackathon not found'
        }
    }
})
def get_hackathon_teams():
    clerk_id = request.args.get('clerkId')
    hackathon_id = request.args.get('hackathon_id')
    
    if not clerk_id or not hackathon_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    user = User.query.get(clerk_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role not in ['organiser', 'admin']:
        return jsonify({'error': 'Forbidden: Unauthorized access'}), 403
    
    hackathon = Hackathon.query.get(hackathon_id)
    if not hackathon:
        return jsonify({'error': 'Hackathon not found'}), 404
    
    teams = Team.query.filter_by(hackathon_id=hackathon_id).all()
    return jsonify([team.to_dict() for team in teams]), 200