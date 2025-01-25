from flask import Blueprint, request, jsonify
from config import db
from flasgger import swag_from
from .models import OrganiserDetails

organiser_bp = Blueprint('organiser_bp', __name__, url_prefix='/organisers')

# CREATE ORGANISER PROFILE
@organiser_bp.route('', methods=['POST'])
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
                'name': {'type': 'string'},
                'email': {'type': 'string'},
                'phone_number': {'type': 'string'},
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
            'required': ['clerkId', 'name', 'email']
        }
    }],
    'responses': {
        201: {'description': 'Organiser profile created successfully'},
        400: {'description': 'Invalid input or profile already exists'},
        500: {'description': 'Server error'}
    }
})
def create_organiser():
    try:
        data = request.get_json()
        
        if Organiser.query.filter_by(clerkId=data['clerkId']).first():
            return jsonify({"error": "Organiser profile already exists"}), 400

        organiser = Organiser(
            clerkId=data['clerkId'],
            name=data['name'],
            email=data['email'],
            phone_number=data.get('phone_number'),
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
@organiser_bp.route('/<string:clerkId>', methods=['PUT'])
@swag_from({
    'tags': ['Organiser'],
    'summary': 'Update organiser profile',
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
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
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
def update_organiser(clerkId):
    try:
        data = request.get_json()
        organiser = Organiser.query.filter_by(clerkId=clerkId).first()

        if not organiser:
            return jsonify({"error": "Organiser not found"}), 404

        updatable_fields = [
            'name', 'email', 'phone_number', 'organization',
            'website', 'bio', 'socials', 'tags'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(organiser, field, data[field])

        db.session.commit()
        return jsonify(organiser.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# GET ORGANISER PROFILE (DASHBOARD)
@organiser_bp.route('/<string:clerkId>', methods=['GET'])
@swag_from({
    'tags': ['Organiser'],
    'summary': 'Get full organiser details',
    'parameters': [{
        'name': 'clerkId',
        'in': 'path',
        'type': 'string',
        'required': True,
        'description': 'ClerkID of the organiser'
    }],
    'responses': {
        200: {'description': 'Organiser details retrieved'},
        404: {'description': 'Organiser not found'}
    }
})
def get_organiser(clerkId):
    organiser = Organiser.query.filter_by(clerkId=clerkId).first()
    if not organiser:
        return jsonify({"error": "Organiser not found"}), 404
    return jsonify(organiser.to_dict()), 200

# GET PUBLIC ORGANISER PROFILE
@organiser_bp.route('/<string:clerkId>/public', methods=['GET'])
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
    organiser = Organiser.query.filter_by(clerkId=clerkId).first()
    if not organiser:
        return jsonify({"error": "Organiser not found"}), 404

    public_profile = {
        "name": organiser.name,
        "organization": organiser.organization,
        "website": organiser.website,
        "bio": organiser.bio,
        "socials": organiser.socials,
        "tags": organiser.tags,
        "contact": {
            "phone": organiser.phone_number,
            "email": organiser.email
        }
    }
    return jsonify(public_profile), 200