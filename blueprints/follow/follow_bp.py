from flask import Blueprint, request, jsonify
from config import db
from blueprints.auth.models import User
from .models import Follow
from flasgger import swag_from

follow_bp = Blueprint('follow_bp', __name__)

@follow_bp.route('/request/<string:clerkid>', methods=['POST'])
@swag_from('./docs/send_follow_request.yml')
def send_follow_request(clerkid):
    """
    Endpoint to send a follow request to a clerk.
    """
    data = request.get_json()
    follower_clerkid = data.get('follower_clerkid')
    followed_clerkid = data.get('followed_clerkid')

    if not follower_clerkid or not followed_clerkid:
        return jsonify({'error': 'Both follower_clerkid and followed_clerkid are required'}), 400

    follow_request = Follow(clerkid=clerkid, follower_clerkid=follower_clerkid, followed_clerkid=followed_clerkid)
    db.session.add(follow_request)
    db.session.commit()

    return jsonify({'message': 'Follow request sent successfully'}), 201


@follow_bp.route('/request/<string:clerkid>', methods=['PUT'])
@swag_from('./docs/handle_follow_request.yml')
def handle_follow_request(clerkid):
    """
    Endpoint to accept or reject a follow request.
    """
    data = request.get_json()
    follower_clerkid = data.get('follower_clerkid')
    action = data.get('action')  # 'accept' or 'reject'

    if not follower_clerkid or action not in ['accept', 'reject']:
        return jsonify({'error': 'Invalid input'}), 400

    follow_request = Follow.query.filter_by(clerkid=clerkid, follower_clerkid=follower_clerkid).first()

    if not follow_request:
        return jsonify({'error': 'Follow request not found'}), 404

    if action == 'accept':
        follow_request.status = 'accepted'
    elif action == 'reject':
        db.session.delete(follow_request)
        db.session.commit()
        return jsonify({'message': 'Follow request rejected and removed'}), 200

    db.session.commit()
    return jsonify({'message': 'Follow request accepted'}), 200


@follow_bp.route('/followers/<string:clerkid>', methods=['GET'])
@swag_from('./docs/get_followers.yml')
def get_followers(clerkid):
    """
    Endpoint to retrieve the list of followers.
    """
    followers = Follow.query.filter_by(followed_clerkid=clerkid).all()
    follower_list = [{'follower_clerkid': f.follower_clerkid, 'createdAt': f.createdAt} for f in followers]

    return jsonify({'followers': follower_list}), 200


@follow_bp.route('/following/<string:clerkid>', methods=['GET'])
@swag_from('./docs/get_following.yml')
def get_following(clerkid):
    """
    Endpoint to retrieve the list of followed users.
    """
    following = Follow.query.filter_by(follower_clerkid=clerkid).all()
    following_list = [{'followed_clerkid': f.followed_clerkid, 'createdAt': f.createdAt} for f in following]

    return jsonify({'following': following_list}), 200


@follow_bp.route('/unfollow/<string:clerkid>', methods=['DELETE'])
@swag_from('./docs/unfollow.yml')
def unfollow(clerkid):
    """
    Endpoint to unfollow a user.
    """
    data = request.get_json()
    unfollow_id = data.get('unfollow_id')

    if not unfollow_id:
        return jsonify({'error': 'unfollow_id is required'}), 400

    follow = Follow.query.filter_by(follower_clerkid=clerkid, followed_clerkid=unfollow_id).first()

    if not follow:
        return jsonify({'error': 'Follow relationship not found'}), 404

    db.session.delete(follow)
    db.session.commit()

    return jsonify({'message': 'Unfollowed successfully'}), 200


@follow_bp.route('/remove_following/<string:clerkid>', methods=['DELETE'])
@swag_from('./docs/remove_following.yml')
def remove_following(clerkid):
    """
    Endpoint to remove someone from your following list.
    """
    data = request.get_json()
    remove_id = data.get('remove_id')

    if not remove_id:
        return jsonify({'error': 'remove_id is required'}), 400

    follow = Follow.query.filter_by(followed_clerkid=clerkid, follower_clerkid=remove_id).first()

    if not follow:
        return jsonify({'error': 'Follow relationship not found'}), 404

    db.session.delete(follow)
    db.session.commit()

    return jsonify({'message': 'Removed from following successfully'}), 200
