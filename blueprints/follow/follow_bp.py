from flask import Blueprint, request, jsonify
from flasgger import swag_from
from config import db
from blueprints.auth.models import User
from blueprints.follow.models import Follow

follow_bp = Blueprint('follow_bp', __name__)


@swag_from({
    'tags': ['Follow'],
    'summary': 'Follow a user directly',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'follower_clerkid': {'type': 'string'},
                    'followed_clerkid': {'type': 'string'}
                },
                'required': ['follower_clerkid', 'followed_clerkid']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Follow action completed successfully'
        },
        '400': {
            'description': 'Invalid input or action'
        }
    }
})
@follow_bp.route('/follow', methods=['POST'])
def follow_user():
    data = request.get_json()

    # Extract follower and followed clerk IDs
    follower_clerkid = data['follower_clerkid']
    followed_clerkid = data['followed_clerkid']

    # Check if the user is trying to follow themselves
    if follower_clerkid == followed_clerkid:
        return jsonify({"message": "You cannot follow yourself"}), 400

    # Create the Follow record for the follower and followed user
    new_follow = Follow(
        clerkId=follower_clerkid,
        follower_clerkId=follower_clerkid,
        followed_clerkId=followed_clerkid
    )

    # Update the Followed Clerk's list (add the follower's clerkId to their list)
    existing_followed = Follow.query.filter_by(clerkId=followed_clerkid).first()
    if existing_followed:
        followed_list = existing_followed.followed_clerkId.split(",")  # Get existing followed list
        followed_list.append(follower_clerkid)  # Add the follower
        existing_followed.followed_clerkId = ",".join(followed_list)  # Update the list
    else:
        existing_followed = Follow(
            clerkId=followed_clerkid,
            follower_clerkId="",
            followed_clerkId=follower_clerkid
        )
        db.session.add(existing_followed)

    # Update the Follower Clerk's list (add the followed clerkId to their list)
    existing_follower = Follow.query.filter_by(clerkId=follower_clerkid).first()
    if existing_follower:
        follower_list = existing_follower.follower_clerkId.split(",")  # Get existing follower list
        follower_list.append(followed_clerkid)  # Add the followed user
        existing_follower.follower_clerkId = ",".join(follower_list)  # Update the list
    else:
        existing_follower = Follow(
            clerkId=follower_clerkid,
            follower_clerkId=followed_clerkid,
            followed_clerkId=""
        )
        db.session.add(existing_follower)

    # Commit the changes to the database
    db.session.add(new_follow)
    db.session.commit()

    return jsonify({"message": "Follow action completed successfully"}), 201

@swag_from({
    'tags': ['Follow'],
    'summary': 'Accept or reject follow request',
    'parameters': [
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'enum': ['accepted', 'rejected'],
            'required': True,
            'description': 'Status of the follow request'
        }
    ],
    'responses': {
        '200': {
            'description': 'Follow request updated successfully'
        },
        '400': {
            'description': 'Invalid input'
        }
    }
})
@follow_bp.route('/request/<clerkId>/<follower_clerkid>', methods=['PUT'])
def handle_follow_request(clerkId, follower_clerkid):
    status = request.args.get('status')

    if status not in ['accepted', 'rejected']:
        return jsonify({"message": "Invalid status. Must be either 'accepted' or 'rejected'"}), 400

    follow_request = Follow.query.filter_by(
        clerkid=clerkId,
        follower_clerkid=follower_clerkid
    ).first()

    if not follow_request:
        return jsonify({"message": "Follow request not found"}), 404

    # Handle acceptance or rejection of follow request
    if status == 'accepted':
        # Logic to accept follow request, e.g., add to following list
        # Update the status or any other logic for acceptance
        pass
    else:
        # Logic to reject follow request
        db.session.delete(follow_request)
        db.session.commit()

    return jsonify({"message": f"Follow request {status} successfully"}), 200


@swag_from({
    'tags': ['Follow'],
    'summary': 'Get the follower and followed list',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The clerkId of the user whose follow lists are being retrieved'
        }
    ],
    'responses': {
        '200': {
            'description': 'Follower and followed list retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'followers': {'type': 'array', 'items': {'type': 'string'}},
                    'followed': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        },
        '400': {
            'description': 'Invalid input'
        }
    }
})
@follow_bp.route('/list/<clerkId>', methods=['GET'])
def get_follow_lists(clerkId):
    followers = Follow.query.filter_by(followed_clerkid=clerkId).all()
    followed = Follow.query.filter_by(follower_clerkid=clerkId).all()

    followers_list = [follower.follower_clerkid for follower in followers]
    followed_list = [followed_user.followed_clerkid for followed_user in followed]

    return jsonify({
        "followers": followers_list,
        "followed": followed_list
    }), 200


@swag_from({
    'tags': ['Follow'],
    'summary': 'Unfollow a user',
    'parameters': [
        {
            'name': 'clerkId',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The clerkId of the user who is unfollowing'
        },
        {
            'name': 'followed_clerkid',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The clerkId of the user to unfollow'
        }
    ],
    'responses': {
        '200': {
            'description': 'Successfully unfollowed the user'
        },
        '404': {
            'description': 'Follow relationship not found'
        }
    }
})
@follow_bp.route('/unfollow/<clerkId>/<followed_clerkid>', methods=['DELETE'])
def unfollow_user(clerkId, followed_clerkid):
    follow_request = Follow.query.filter_by(
        follower_clerkid=clerkId,
        followed_clerkid=followed_clerkid
    ).first()

    if not follow_request:
        return jsonify({"message": "Follow relationship not found"}), 404

    db.session.delete(follow_request)
    db.session.commit()

    return jsonify({"message": "Successfully unfollowed the user"}), 200
