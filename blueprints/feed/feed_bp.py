from flask import Blueprint, request, jsonify
from config import db
from blueprints.projects.models import Project
from blueprints.auth.models import User
from flasgger import swag_from
from blueprints.feed.models import FeedRequestProject, FeedRequestPerson

feed_bp = Blueprint('feed_bp', __name__)

# Route to send a feed request
@swag_from({
    'tags': ['Feed Requests'],
    'summary': 'Send a feed request',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'request_type': {'type': 'string', 'enum': ['project', 'person'], 'required': True},
                    'sender_clerkId': {'type': 'string', 'required': True},
                    'receiver_clerkId': {'type': 'string', 'required': True},
                    'project_id': {'type': 'integer'},  # Required if request_type is 'project'
                    'message': {'type': 'string'}
                },
                'required': ['request_type', 'sender_clerkId', 'receiver_clerkId']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Feed request sent successfully'
        },
        '400': {
            'description': 'Invalid input'
        },
        '404': {
            'description': 'User or Project not found'
        }
    }
})
@feed_bp.route('/send_request', methods=['POST'])
def send_request():
    data = request.get_json()
    request_type = data.get('request_type')
    sender_clerkId = data.get('sender_clerkId')
    receiver_clerkId = data.get('receiver_clerkId')
    message = data.get('message', '')

    sender = User.query.filter_by(clerkId=sender_clerkId).first()
    receiver = User.query.filter_by(clerkId=receiver_clerkId).first()

    if not sender or not receiver:
        return jsonify({"message": "Sender or receiver not found"}), 404

    if request_type == 'project':
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"message": "project_id is required for project requests"}), 400
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404
        feed_request = FeedRequestProject(
            project_id=project_id,
            clerkid_sender=sender_clerkId,
            clerkid_receiver=receiver_clerkId,
            message=message
        )
    elif request_type == 'person':
        feed_request = FeedRequestPerson(
            clerkid_sender=sender_clerkId,
            clerkid_receiver=receiver_clerkId,
            message=message
        )
    else:
        return jsonify({"message": "Invalid request_type"}), 400

    db.session.add(feed_request)
    db.session.commit()
    return jsonify({"message": "Feed request sent successfully"}), 201

# Route to get feed requests by receiver's clerkId
@swag_from({
    'tags': ['Feed Requests'],
    'summary': 'Get feed requests for a receiver',
    'parameters': [
        {
            'name': 'receiver_clerkId',
            'in': 'path',
            'required': True,
            'type': 'string'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of feed requests',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'project_id': {'type': 'integer'},
                        'clerkid_sender': {'type': 'string'},
                        'clerkid_receiver': {'type': 'string'},
                        'message': {'type': 'string'},
                        'created_at': {'type': 'string'},
                        'status': {'type': 'string'}
                    }
                }
            }
        },
        '404': {
            'description': 'Receiver not found'
        }
    }
})
@feed_bp.route('/get_requests/<string:receiver_clerkId>', methods=['GET'])
def get_requests(receiver_clerkId):
    receiver = User.query.filter_by(clerkId=receiver_clerkId).first()
    if not receiver:
        return jsonify({"message": "Receiver not found"}), 404

    project_requests = FeedRequestProject.query.filter_by(clerkid_receiver=receiver_clerkId).all()
    person_requests = FeedRequestPerson.query.filter_by(clerkid_receiver=receiver_clerkId).all()

    requests = [req.to_dict() for req in project_requests] + [req.to_dict() for req in person_requests]
    return jsonify(requests), 200

# Route to get feed requests by sender's clerkId
@swag_from({
    'tags': ['Feed Requests'],
    'summary': 'Get feed requests for a sender',
    'parameters': [
        {
            'name': 'sender_clerkId',
            'in': 'path',
            'required': True,
            'type': 'string'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of feed requests',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'project_id': {'type': 'integer'},
                        'clerkid_sender': {'type': 'string'},
                        'clerkid_receiver': {'type': 'string'},
                        'message': {'type': 'string'},
                        'created_at': {'type': 'string'},
                        'status': {'type': 'string'}
                    }
                }
            }
        },
        '404': {
            'description': 'Sender not found'
        }
    }
})
@feed_bp.route('/get_my_requests/<string:sender_clerkId>', methods=['GET'])
def get_requests_by_sender(sender_clerkId):
    sender = User.query.filter_by(clerkId=sender_clerkId).first()
    if not sender:
        return jsonify({"message": "Sender not found"}), 404

    project_requests = FeedRequestProject.query.filter_by(clerkid_sender=sender_clerkId).all()
    person_requests = FeedRequestPerson.query.filter_by(clerkid_sender=sender_clerkId).all()

    requests = [req.to_dict() for req in project_requests] + [req.to_dict() for req in person_requests]
    return jsonify(requests), 200

# Route to approve or reject a feed request
@swag_from({
    'tags': ['Feed Requests'],
    'summary': 'Approve or reject a feed request',
    'parameters': [
        {
            'name': 'request_id',
            'in': 'path',
            'required': True,
            'type': 'integer'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'request_type': {'type': 'string', 'enum': ['project', 'person'], 'required': True},
                    'status': {'type': 'string', 'enum': ['approved', 'rejected'], 'required': True}
                },
                'required': ['request_type', 'status']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Feed request status updated successfully'
        },
        '400': {
            'description': 'Invalid status or request_type'
        },
        '404': {
            'description': 'Feed request not found'
        }
    }
})
@feed_bp.route('/update_request/<int:request_id>', methods=['PUT'])
def update_request(request_id):
    data = request.get_json()
    request_type = data.get('request_type')
    status = data.get('status')

    if status not in ['approved', 'rejected']:
        return jsonify({"message": "Invalid status"}), 400

    if request_type == 'project':
        feed_request = FeedRequestProject.query.get(request_id)
    elif request_type == 'person':
        feed_request = FeedRequestPerson.query.get(request_id)
    else:
        return jsonify({"message": "Invalid request_type"}), 400

    if not feed_request:
        return jsonify({"message": "Feed request not found"}), 404

    feed_request.status = status
    db.session.commit()
    return jsonify({"message": "Feed request status updated successfully"}), 200

