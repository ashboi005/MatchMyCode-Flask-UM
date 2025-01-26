from flask import Blueprint, request, jsonify
from config import db
from flasgger import swag_from
from blueprints.auth.models import User
from .models import OrganiserDetails
from blueprints.hackathon.models import Hackathon, ProjectSubmission

organiser_bp = Blueprint('organiser_bp', __name__, url_prefix='/organiser_details')

# CREATE ORGANISER PROFILE
@organiser_bp.route('/post_organiser_details', methods=['POST'])
@swag_from({
    'tags': ['Organiser'],
    'summary': 'Create new organiser profile',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'clerkId': {'type': 'string'},
                'organization': {'type': 'string'},
                'website': {'type': 'string'},
                'bio': {'type': 'string'},
                'socials': {
                    'type': 'object',
                    'properties': {
                        'twitter': {'type': 'string'},
                        'linkedin': {'type': 'string'},
                        'github': {'type': 'string'}
                    }
                },
                'tags': {'type': 'array', 'items': {'type': 'string'}}
            },
            'required': ['clerkId']
        }
    }],
    'responses': {
        201: {'description': 'Organiser profile created successfully'},
        400: {'description': 'Invalid input or profile already exists'},
        404: {'description': 'User not found'},
        500: {'description': 'Server error'}
    }
})
def create_organiser():
    try:
        data = request.get_json()
        user = User.query.filter_by(clerkId=data['clerkId']).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if OrganiserDetails.query.filter_by(clerkId=data['clerkId']).first():
            return jsonify({"error": "Organiser profile already exists"}), 400

        # Update user role to organiser
        if user.role != 'organiser':
            user.role = 'organiser'
            db.session.add(user)

        organiser = OrganiserDetails(
            clerkId=data['clerkId'],
            organization=data.get('organization'),
            website=data.get('website'),
            bio=data.get('bio'),
            socials=data.get('socials', {}),
            tags=data.get('tags', [])
        )

        db.session.add(organiser)
        db.session.commit()
        return jsonify(organiser.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# UPDATE ORGANISER PROFILE
@organiser_bp.route('/update_organiser_details_public/<string:clerkId>', methods=['PUT'])
@swag_from({
    'tags': ['Organiser'],
    'summary': 'Update organiser details',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ClerkID of the organiser'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'organization': {'type': 'string'},
                    'website': {'type': 'string'},
                    'bio': {'type': 'string'},
                    'socials': {'type': 'object'},
                    'tags': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Profile updated successfully'},
        404: {'description': 'Organiser not found'},
        400: {'description': 'Invalid input'}
    }
})
def update_organiser_details(clerkId):
    try:
        data = request.get_json()
        organiser = OrganiserDetails.query.filter_by(clerkId=clerkId).first()

        if not organiser:
            return jsonify({"error": "Organiser not found"}), 404

        updatable_fields = [
            'organization', 'website', 'bio',
            'socials', 'tags'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(organiser, field, data[field])

        db.session.commit()
        return jsonify(organiser.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# GET PUBLIC ORGANISER PROFILE
@organiser_bp.route('/get_organiser_details_public/<string:clerkId>', methods=['GET'])
@swag_from({
    'tags': ['Organiser'],
    'summary': 'Get public organiser profile',
    'parameters': [{
        'name': 'clerkId',
        'in': 'path',
        'type': 'string',
        'required': True,
        'description': 'ClerkID of the organiser'
    }],
    'responses': {
        200: {'description': 'Public profile retrieved'},
        404: {'description': 'Organiser not found'}
    }
})
def get_public_organiser(clerkId):
    organiser = OrganiserDetails.query.filter_by(clerkId=clerkId).first()
    if not organiser:
        return jsonify({"error": "Organiser not found"}), 404

    user = User.query.get(clerkId)
    public_profile = {
        "name": user.name,
        "organization": organiser.organization,
        "website": organiser.website,
        "bio": organiser.bio,
        "socials": organiser.socials,
        "tags": organiser.tags,
        "contact": {
            "phone": user.phone_number,
            "email": user.email
        }
    }
    return jsonify(public_profile), 200


@organiser_bp.route('/hackathons/<int:hackathon_id>/submissions', methods=['GET'])
@swag_from({
    'tags': ['Organiser'],
    'summary': 'Get all project submissions for a hackathon',
    'parameters': [
        {
            'name': 'hackathon_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the hackathon'
        },
        {
            'name': 'clerkId',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Clerk ID of the organiser'
        }
    ],
    'responses': {
        200: {
            'description': 'List of project submissions',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'team_code': {'type': 'string'},
                        'github_link': {'type': 'string'},
                        'live_demo_link': {'type': 'string'},
                        'submitted_at': {'type': 'string', 'format': 'date-time'},
                        'team_name': {'type': 'string'}
                    }
                }
            }
        },
        403: {'description': 'Unauthorized'},
        404: {'description': 'Hackathon not found'}
    }
})
def get_submissions(hackathon_id):
    try:
        clerk_id = request.args.get('clerkId')
        organiser = User.query.get(clerk_id)

        # Authorization check
        if not organiser or organiser.role != 'organiser':
            return jsonify({"error": "Unauthorized"}), 403

        # Get hackathon
        hackathon = Hackathon.query.get(hackathon_id)
        if not hackathon:
            return jsonify({"error": "Hackathon not found"}), 404

        # Verify organiser owns the hackathon
        if hackathon.organiser_clerkId != clerk_id:
            return jsonify({"error": "Unauthorized to view submissions for this hackathon"}), 403

        # Get submissions with team details
        submissions = ProjectSubmission.query.filter_by(hackathon_id=hackathon_id).all()
        
        # Enhanced response with team names
        result = []
        for submission in submissions:
            submission_data = submission.to_dict()
            submission_data['team_name'] = submission.team.team_name if submission.team else 'Unknown Team'
            result.append(submission_data)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

