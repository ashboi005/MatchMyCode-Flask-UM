from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User
from blueprints.user.models import UserDetails
from flasgger import swag_from

user_bp = Blueprint('user_bp', __name__)

# POST USER DETAILS ROUTE
@swag_from({
    'tags': ['User'],
    'summary': 'Post user details',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clerkId': {'type': 'string'},
                    'portfolio_links': {'type': 'array', 'items': {'type': 'string'}},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'skills': {'type': 'array', 'items': {'type': 'string'}},
                    'interests': {'type': 'array', 'items': {'type': 'string'}},
                    'socials': {'type': 'array', 'items': {'type': 'string'}},
                    'ongoing_project_links': {'type': 'array', 'items': {'type': 'string'}}
                },
                'required': ['clerkId']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'User details posted successfully'
        },
        '400': {
            'description': 'Invalid input'
        }
    }
})
@user_bp.route('/post_user_details', methods=['POST'])
def post_user_details():
    data = request.get_json()
    user = User.query.filter_by(clerkId=data['clerkId']).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user_details = UserDetails(
        clerkId=data['clerkId'],
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        city=data.get('city', ''),
        state=data.get('state', ''),
        country=data.get('country', ''),
        bio=data.get('bio', ''),
        portfolio_links=data.get('portfolio_links', []),
        tags=data.get('tags', []),
        skills=data.get('skills', []),
        interests=data.get('interests', []),
        socials=data.get('socials', []),
        ongoing_project_links=data.get('ongoing_project_links', [])
    )
    db.session.add(user_details)
    db.session.commit()
    return jsonify({"message": "User details posted successfully"}), 201

# GET USER DETAILS FOR DASHBOARD ROUTE
@swag_from({
    'tags': ['User'],
    'summary': 'Get user details for dashboard',
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
            'description': 'User details retrieved successfully'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
@user_bp.route('/get_user_details_dashboard/<clerkId>', methods=['GET'])
def get_user_details_dashboard(clerkId):
    user_details = UserDetails.query.filter_by(clerkId=clerkId).first()
    if not user_details:
        return jsonify({"message": "User details not found"}), 404

    return jsonify(user_details.to_dict()), 200


# GET USER DETAILS FOR PUBLIC VIEW ROUTE
@swag_from({
    'tags': ['User'],
    'summary': 'Get user details for public view',
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
            'description': 'User details retrieved successfully'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
@user_bp.route('/get_user_details_public/<clerkId>', methods=['GET'])
def get_user_details_public(clerkId):
    user_details = UserDetails.query.filter_by(clerkId=clerkId).first()
    if not user_details:
        return jsonify({"message": "User details not found"}), 404

    public_details = {
        "name": user_details.user.name,
        "bio": user_details.bio,
        "portfolio_links": user_details.portfolio_links,
        "city": user_details.city,
        "state": user_details.state,
        "country": user_details.country,
        "tags": user_details.tags,
        "skills": user_details.skills,
        "interests": user_details.interests,
        "socials": user_details.socials,
        "ongoing_project_links": user_details.ongoing_project_links
    }
    return jsonify(public_details), 200

@swag_from({
    'tags': ['User'],
    'summary': 'Update user details',
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
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'bio': {'type': 'string'},
                    'portfolio_links': {'type': 'array', 'items': {'type': 'string'}},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'skills': {'type': 'array', 'items': {'type': 'string'}},
                    'interests': {'type': 'array', 'items': {'type': 'string'}},
                    'socials': {'type': 'array', 'items': {'type': 'string'}},
                    'ongoing_project_links': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'User details updated successfully'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
@user_bp.route('/update_user_details/<clerkId>', methods=['PUT'])
def update_user_details(clerkId):
    data = request.get_json()
    user_details = UserDetails.query.filter_by(clerkId=clerkId).first()
    if not user_details:
        return jsonify({"message": "User details not found"}), 404

    user_details.name = data.get('name', user_details.name)
    user_details.email = data.get('email', user_details.email)
    user_details.phone_number = data.get('phone_number', user_details.phone_number)
    user_details.bio = data.get('bio', user_details.bio)
    user_details.city = data.get('city', user_details.city)
    user_details.state = data.get('state', user_details.state)
    user_details.country = data.get('country', user_details.country)
    user_details.portfolio_links = data.get('portfolio_links', user_details.portfolio_links)
    user_details.tags = data.get('tags', user_details.tags)
    user_details.skills = data.get('skills', user_details.skills)
    user_details.interests = data.get('interests', user_details.interests)
    user_details.socials = data.get('socials', user_details.socials)
    user_details.ongoing_project_links = data.get('ongoing_project_links', user_details.ongoing_project_links)

    db.session.commit()
    return jsonify({"message": "User details updated successfully"}), 200

# SEARCH USERS BY SKILLS/TAGS/INTERESTS ROUTE
@swag_from({
    'tags': ['User'],
    'summary': 'Search users by skills/tags/interests',
    'parameters': [
        {
            'name': 'skills',
            'in': 'query',
            'type': 'string'
        },
        {
            'name': 'tags',
            'in': 'query',
            'type': 'string'
        },
        {
            'name': 'interests',
            'in': 'query',
            'type': 'string'
        }
    ],
    'responses': {
        '200': {
            'description': 'Users retrieved successfully'
        }
    }
})
@user_bp.route('/search_users', methods=['GET'])
def search_users():
    skills = request.args.get('skills')
    tags = request.args.get('tags')
    interests = request.args.get('interests')
    query = UserDetails.query

    if skills:
        # Use contains method for JSONB array containment
        query = query.filter(UserDetails.skills.contains([skills]))
    if tags:
        query = query.filter(UserDetails.tags.contains([tags]))
    if interests:
        # "interests" is a text field, use ILIKE for partial matches
        query = query.filter(UserDetails.interests.ilike(f'%{interests}%'))

    users = query.all()
    return jsonify([user.to_dict() for user in users]), 200


# VERIFY USER ROUTE (BY MENTOR)
@swag_from({
    'tags': ['User'],
    'summary': 'Verify a user by mentor',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'ClerkID of the user to verify'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clerkId': {'type': 'string', 'description': 'ClerkID of the mentor performing verification'}
                },
                'required': ['clerkId']
            }
        }
    ],
    'responses': {
        '200': {'description': 'User verified successfully'},
        '403': {'description': 'Only mentors can verify users'},
        '404': {'description': 'User/Mentor not found'}
    }
})
@user_bp.route('/verify_user/<clerkId>', methods=['POST'])
def verify_user(clerkId):
    data = request.get_json()
    mentor_clerkId = data.get('clerkId')  # ClerkID of the mentor
    
    # Check if requester is a mentor
    mentor = User.query.filter_by(clerkId=mentor_clerkId).first()
    if not mentor or mentor.role != 'mentor':
        return jsonify({"message": "Only mentors can verify users"}), 403
    
    # Find user to verify
    user_details = UserDetails.query.filter_by(clerkId=clerkId).first()
    if not user_details:
        return jsonify({"message": "User not found"}), 404
    
    # Update verification status
    user_details.verified = True
    db.session.commit()
    
    return jsonify({"message": "User verified successfully"}), 200