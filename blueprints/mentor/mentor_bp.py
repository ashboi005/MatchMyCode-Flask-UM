from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User
from blueprints.mentor.models import MentorDetails
from flasgger import swag_from

mentors_bp = Blueprint('mentors_bp', __name__)

# POST MENTOR DETAILS ROUTE
@swag_from({
    'tags': ['Mentor'],
    'summary': 'Post mentor details',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clerkId': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'bio': {'type': 'string'},
                    'portfolio_links': {'type': 'array', 'items': {'type': 'string'}},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'skills': {'type': 'array', 'items': {'type': 'string'}},
                    'interests': {'type': 'array', 'items': {'type': 'string'}},
                    'socials': {'type': 'array', 'items': {'type': 'string'}},
                    'ongoing_project_links': {'type': 'array', 'items': {'type': 'string'}},
                    'education': {'type': 'string'},
                    'experience_years': {'type': 'integer'},
                    'city': {'type': 'string'},
                    'state': {'type': 'string'},
                    'country': {'type': 'string'}
                },
                'required': ['clerkId']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Mentor details posted successfully'
        },
        '400': {
            'description': 'Invalid input'
        }
    }
})
@mentors_bp.route('/post_mentor_details', methods=['POST'])
def post_mentor_details():
    data = request.get_json()
    mentor = User.query.filter_by(clerkId=data['clerkId']).first()
    if mentor.role != 'mentor':
        return jsonify({"message": "User is not a mentor"}), 400
    if not mentor:
        return jsonify({"message": "Mentor not found"}), 404

    mentor_details = MentorDetails(
        clerkId=data['clerkId'],
        name=mentor.name,
        email=mentor.email,
        phone_number=mentor.phone_number,
        role=mentor.role,
        bio=data.get('bio'),
        portfolio_links=data.get('portfolio_links', []),
        tags=data.get('tags', []),
        skills=data.get('skills', []),
        interests=data.get('interests', []),
        socials=data.get('socials', []),
        ongoing_project_links=data.get('ongoing_project_links', []),
        education=data.get('education'),
        experience_years=data.get('experience_years'),
        city=data.get('city'),
        state=data.get('state'),
        country=data.get('country')
    )
    db.session.add(mentor_details)
    db.session.commit()
    return jsonify({"message": "Mentor details posted successfully"}), 201

# GET MENTOR DETAILS FOR PUBLIC VIEW ROUTE
@swag_from({
    'tags': ['Mentor'],
    'summary': 'Get mentor details for public view',
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
            'description': 'Mentor details retrieved successfully'
        },
        '404': {
            'description': 'Mentor not found'
        }
    }
})
@mentors_bp.route('/get_mentor_details_public/<clerkId>', methods=['GET'])
def get_mentor_details_public(clerkId):
    mentor_details = MentorDetails.query.filter_by(clerkId=clerkId).first()
    if not mentor_details:
        return jsonify({"message": "Mentor details not found"}), 404

    public_details = {
        "name": mentor_details.name,
        "bio": mentor_details.bio,
        "tags": mentor_details.tags,
        "skills": mentor_details.skills,
        "portfolio_links": mentor_details.portfolio_links,
        "interests": mentor_details.interests,
        "socials": mentor_details.socials,
        "ongoing_project_links": mentor_details.ongoing_project_links,
        "education": mentor_details.education,
        "experience_years": mentor_details.experience_years,
        "city": mentor_details.city,
        "state": mentor_details.state,
        "country": mentor_details.country
    }
    return jsonify(public_details), 200

# UPDATE MENTOR DETAILS ROUTE
@swag_from({
    'tags': ['Mentor'],
    'summary': 'Update mentor details',
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
                    'bio': {'type': 'string'},
                    'portfolio_links': {'type': 'array', 'items': {'type': 'string'}},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'skills': {'type': 'array', 'items': {'type': 'string'}},
                    'interests': {'type': 'array', 'items': {'type': 'string'}},
                    'socials': {'type': 'array', 'items': {'type': 'string'}},
                    'ongoing_project_links': {'type': 'array', 'items': {'type': 'string'}},
                    'education': {'type': 'string'},
                    'experience_years': {'type': 'integer'},
                    'city': {'type': 'string'},
                    'state': {'type': 'string'},
                    'country': {'type': 'string'},
                    'phone_number': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Mentor details updated successfully'
        },
        '404': {
            'description': 'Mentor not found'
        }
    }
})
@mentors_bp.route('/update_mentor_details/<clerkId>', methods=['PUT'])
def update_mentor_details(clerkId):
    data = request.get_json()
    mentor_details = MentorDetails.query.filter_by(clerkId=clerkId).first()
    if not mentor_details:
        return jsonify({"message": "Mentor details not found"}), 404

    mentor_details.bio = data.get('bio', mentor_details.bio)
    mentor_details.portfolio_links = data.get('portfolio_links', mentor_details.portfolio_links)
    mentor_details.tags = data.get('tags', mentor_details.tags)
    mentor_details.skills = data.get('skills', mentor_details.skills)
    mentor_details.interests = data.get('interests', mentor_details.interests)
    mentor_details.socials = data.get('socials', mentor_details.socials)
    mentor_details.ongoing_project_links = data.get('ongoing_project_links', mentor_details.ongoing_project_links)
    mentor_details.education = data.get('education', mentor_details.education)
    mentor_details.experience_years = data.get('experience_years', mentor_details.experience_years)
    mentor_details.city = data.get('city', mentor_details.city)
    mentor_details.state = data.get('state', mentor_details.state)
    mentor_details.country = data.get('country', mentor_details.country)
    mentor_details.phone_number = data.get('phone_number', mentor_details.phone_number)

    db.session.commit()
    return jsonify({"message": "Mentor details updated successfully"}), 200

# SEARCH MENTORS BY TAGS/SKILLS ROUTE
@swag_from({
    'tags': ['Mentor'],
    'summary': 'Search mentors by tags or skills',
    'parameters': [
        {
            'name': 'tags',
            'in': 'query',
            'type': 'string'
        },
        {
            'name': 'skills',
            'in': 'query',
            'type': 'string'
        }
    ],
    'responses': {
        '200': {
            'description': 'Mentors retrieved successfully'
        }
    }
})
@mentors_bp.route('/search_mentors', methods=['GET'])
def search_mentors():
    tags = request.args.get('tags')
    skills = request.args.get('skills')
    query = MentorDetails.query

    if tags:
        query = query.filter(MentorDetails.tags.contains([tags]))
    if skills:
        query = query.filter(MentorDetails.skills.contains([skills]))

    mentors = query.all()
    return jsonify([mentor.to_dict() for mentor in mentors]), 200


# VERIFY USER ROUTE (BY MENTOR)
@mentors_bp.route('/verify_user/<user_clerkId>', methods=['POST'])
@swag_from({
    'tags': ['Mentor'],
    'summary': 'Verify a user account by mentor',
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
            
        if user.verified:
            return jsonify({"error": "User already verified"}), 400

        # Update verification status
        user.verified = True
        db.session.commit()
        return jsonify({"message": "User verified successfully"}), 200

    except KeyError:
        return jsonify({"error": "mentor_clerkId is required"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500