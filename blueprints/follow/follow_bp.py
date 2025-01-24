from flask import Blueprint, request, jsonify
from flasgger import swag_from
from config import db
from blueprints.auth.models import User
from .models import Follow

follow_bp = Blueprint('follow_bp', __name__)

@swag_from({
    'tags': ['Follow'],
    'summary': 'Send a follow request directly and update both lists',
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
            'description': 'Follow request created successfully'
        },
        '400': {
            'description': 'Invalid input'
        }
    }
})
@follow_bp.route('/request/<clerkId>', methods=['POST'])
def send_follow_request(clerkId):
    data = request.get_json()
    follower_clerkid = data['follower_clerkid']
    followed_clerkid = data['followed_clerkid']
    
#     # Check if the user is trying to follow themselves
#     if follower_clerkid == followed_clerkid:
#         return jsonify({"message": "You cannot follow yourself"}), 400

#     # Check if follow request already exists
#     existing_follow = Follow.query.filter_by(
#         follower_clerkid=follower_clerkid,
#         followed_clerkid=followed_clerkid
#     ).first()

#     if existing_follow:
#         return jsonify({"message": "Follow request already exists"}), 400

    # Create follow relationship from the follower's side
    follow_from_follower = Follow(
        clerkid=clerkId,
        follower_clerkid=follower_clerkid,
        followed_clerkid=followed_clerkid
    )
    
    # Create follow relationship from the followed person's side (followers list)
    follow_from_followed = Follow(
        clerkid=clerkId,
        follower_clerkid=followed_clerkid,
        followed_clerkid=follower_clerkid
    )

    # Add both follow relationships to the session
    db.session.add(follow_from_follower)
    db.session.add(follow_from_followed)
    
    # Commit both changes to the database
    db.session.commit()

    return jsonify({"message": "Follow request sent successfully, both lists updated"}), 201


# @swag_from({
#     'tags': ['Follow'],
#     'summary': 'Accept or reject follow request',
#     'parameters': [
#         {
#             'name': 'status',
#             'in': 'query',
#             'type': 'string',
#             'enum': ['accepted', 'rejected'],
#             'required': True,
#             'description': 'Status of the follow request'
#         }
#     ],
#     'responses': {
#         '200': {
#             'description': 'Follow request updated successfully'
#         },
#         '400': {
#             'description': 'Invalid input'
#         }
#     }
# })
# @follow_bp.route('/request/<clerkId>/<follower_clerkid>', methods=['PUT'])
# def handle_follow_request(clerkId, follower_clerkid):
#     status = request.args.get('status')

#     if status not in ['accepted', 'rejected']:
#         return jsonify({"message": "Invalid status. Must be either 'accepted' or 'rejected'"}), 400

#     follow_request = Follow.query.filter_by(
#         clerkid=clerkId,
#         follower_clerkid=follower_clerkid
#     ).first()

#     if not follow_request:
#         return jsonify({"message": "Follow request not found"}), 404

#     # Handle acceptance or rejection of follow request
#     if status == 'accepted':
#         # Logic to accept follow request, e.g., add to following list
#         # Update the status or any other logic for acceptance
#         pass
#     else:
#         # Logic to reject follow request
#         db.session.delete(follow_request)
#         db.session.commit()

#     return jsonify({"message": f"Follow request {status} successfully"}), 200


# @swag_from({
#     'tags': ['Follow'],
#     'summary': 'Get the follower and followed list',
#     'parameters': [
#         {
#             'name': 'clerkId',
#             'in': 'path',
#             'type': 'string',
#             'required': True,
#             'description': 'The clerkId of the user whose follow lists are being retrieved'
#         }
#     ],
#     'responses': {
#         '200': {
#             'description': 'Follower and followed list retrieved successfully',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'followers': {'type': 'array', 'items': {'type': 'string'}},
#                     'followed': {'type': 'array', 'items': {'type': 'string'}}
#                 }
#             }
#         },
#         '400': {
#             'description': 'Invalid input'
#         }
#     }
# })
# @follow_bp.route('/list/<clerkId>', methods=['GET'])
# def get_follow_lists(clerkId):
#     followers = Follow.query.filter_by(followed_clerkid=clerkId).all()
#     followed = Follow.query.filter_by(follower_clerkid=clerkId).all()

#     followers_list = [follower.follower_clerkid for follower in followers]
#     followed_list = [followed_user.followed_clerkid for followed_user in followed]

#     return jsonify({
#         "followers": followers_list,
#         "followed": followed_list
#     }), 200


# @swag_from({
#     'tags': ['Follow'],
#     'summary': 'Unfollow a user',
#     'parameters': [
#         {
#             'name': 'clerkId',
#             'in': 'path',
#             'type': 'string',
#             'required': True,
#             'description': 'The clerkId of the user who is unfollowing'
#         },
#         {
#             'name': 'followed_clerkid',
#             'in': 'path',
#             'type': 'string',
#             'required': True,
#             'description': 'The clerkId of the user to unfollow'
#         }
#     ],
#     'responses': {
#         '200': {
#             'description': 'Successfully unfollowed the user'
#         },
#         '404': {
#             'description': 'Follow relationship not found'
#         }
#     }
# })
# @follow_bp.route('/unfollow/<clerkId>/<followed_clerkid>', methods=['DELETE'])
# def unfollow_user(clerkId, followed_clerkid):
#     follow_request = Follow.query.filter_by(
#         follower_clerkid=clerkId,
#         followed_clerkid=followed_clerkid
#     ).first()

#     if not follow_request:
#         return jsonify({"message": "Follow relationship not found"}), 404

#     db.session.delete(follow_request)
#     db.session.commit()

#     return jsonify({"message": "Successfully unfollowed the user"}), 200
