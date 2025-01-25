from flask import Blueprint, request, jsonify
from flasgger import swag_from
from config import db
from blueprints.auth.models import User
from blueprints.follow.models import Follow

follow_bp = Blueprint('follow_bp', __name__)

@follow_bp.route('/follow', methods=['POST'])
@swag_from({
    'tags': ['Follow'],
    'summary': 'Follow another user',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'follower_clerk_id': {
                        'type': 'string',
                        'description': 'Clerk ID of the follower (current user)'
                    },
                    'followed_clerk_id': {
                        'type': 'string',
                        'description': 'Clerk ID of the user to follow'
                    }
                },
                'required': ['follower_clerk_id', 'followed_clerk_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Successfully followed user',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Already following or invalid input',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'User not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def follow_user():
    data = request.get_json()
    follower_id = data.get('follower_clerk_id')
    followed_id = data.get('followed_clerk_id')

    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)
    
    if not follower or not followed:
        return jsonify({'error': 'User not found'}), 404

    if Follow.query.filter_by(follower_id=follower_id, followed_id=followed_id).first():
        return jsonify({'error': 'Already following'}), 400

    new_follow = Follow(follower_id=follower_id, followed_id=followed_id)
    db.session.add(new_follow)
    db.session.commit()

    return jsonify({'message': 'Successfully followed'}), 201

@follow_bp.route('/unfollow', methods=['POST'])
@swag_from({
    'tags': ['Follow'],
    'summary': 'Unfollow a user',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'follower_clerk_id': {'type': 'string'},
                    'followed_clerk_id': {'type': 'string'}
                },
                'required': ['follower_clerk_id', 'followed_clerk_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully unfollowed',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Follow relationship not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def unfollow_user():
    data = request.get_json()
    follower_id = data.get('follower_clerk_id')
    followed_id = data.get('followed_clerk_id')

    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)
    
    if not follower or not followed:
        return jsonify({'error': 'User not found'}), 404

    follow = Follow.query.filter_by(follower_id=follower_id, followed_id=followed_id).first()
    if not follow:
        return jsonify({'error': 'Not following'}), 404

    db.session.delete(follow)
    db.session.commit()

    return jsonify({'message': 'Successfully unfollowed'}), 200

@follow_bp.route('/users/<string:clerkId>/followers', methods=['GET'])
@swag_from({
    'tags': ['Follow'],
    'summary': 'Get list of followers for a user',
    'parameters': [
        {
            'name': 'clerkId',  # Changed from clerk_id to match route parameter
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Clerk ID of the user'
        }
    ],
    'responses': {
        200: {
            'description': 'List of follower IDs',
            'schema': {
                'type': 'object',
                'properties': {
                    'followers': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        },
        404: {
            'description': 'User not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_followers(clerkId):
    user = User.query.get(clerkId)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    followers = [follower.clerkId for follower in user.followers]
    return jsonify({'followers': followers})

@follow_bp.route('/users/<string:clerkId>/following', methods=['GET'])
@swag_from({
    'tags': ['Follow'],
    'summary': 'Get list of users being followed',
    'parameters': [
        {
            'name': 'clerkId',  # Changed from clerk_id to match route parameter
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Clerk ID of the user'
        }
    ],
    'responses': {
        200: {
            'description': 'List of followed user IDs',
            'schema': {
                'type': 'object',
                'properties': {
                    'following': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        },
        404: {
            'description': 'User not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_following(clerkId):
    user = User.query.get(clerkId)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    following = [followed.clerkId for followed in user.following]
    return jsonify({'following': following})