from flask import Blueprint, request, jsonify
from config import db
from flasgger import swag_from
from blueprints.chat.models import Chat, Message
from blueprints.projects.models import Project
from blueprints.chat.chat_config import pusher_client
from datetime import datetime, timedelta
from blueprints.auth.models import User

IST_OFFSET = timedelta(hours=5, minutes=30)

chat_bp = Blueprint('chat_bp', __name__)

@swag_from({
    'tags': ['Chat'],
    'summary': 'Create a direct message (DM) room between two users',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user1': {'type': 'string', 'example': 'userA'},
                    'user2': {'type': 'string', 'example': 'userB'}
                },
                'required': ['user1', 'user2']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'DM room created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'room_id': {'type': 'string', 'example': 'dm-userA-userB'}
                }
            }
        },
        400: {
            'description': 'Invalid input',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Missing required fields'}
                }
            }
        }
    }
})
@chat_bp.route('/create-dm', methods=['POST'])
def create_dm():
    data = request.json
    user1, user2 = sorted([data['user1'], data['user2']])  
    room_id = f"dm-{user1}-{user2}"
    
    # Check if DM exists
    existing = Chat.query.filter_by(room_id=room_id).first()
    if existing:
        return jsonify({"room_id": room_id})
        
    # Create new DM
    new_chat = Chat(
        room_id=room_id,
        participants=[user1, user2]
    )
    db.session.add(new_chat)
    db.session.commit()
    
    return jsonify({"room_id": room_id}), 201

@chat_bp.route('/get-messages/<room_id>', methods=['GET'])
@swag_from({
    'tags': ['Chat'],
    'summary': 'Get messages for a chat room',
    'parameters': [
        {
            'name': 'room_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ID of the chat room'
        },
        {
            'name': 'user_id',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'User ID for authorization'
        }
    ],
    'responses': {
        200: {
            'description': 'List of messages',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'sender_id': {'type': 'string'},
                        'content': {'type': 'string'},
                        'timestamp': {'type': 'string'}
                    }
                }
            }
        },
        403: {'description': 'Unauthorized'},
        404: {'description': 'Room not found'}
    }
})
def get_messages(room_id):
    user_id = request.args.get('user_id')
    chat = Chat.query.filter_by(room_id=room_id).first()
    
    if not chat:
        return jsonify({"error": "Room not found"}), 404
    if user_id not in chat.participants:
        return jsonify({"error": "Unauthorized"}), 403
    
    # In get_messages route
    messages = db.session.query(Message, User.name)\
        .join(User, Message.sender_id == User.clerkId)\
        .filter(Message.room_id == room_id)\
        .order_by(Message.created_at.asc())\
        .all()

    # Process results safely
    return jsonify([{
        'sender_id': message.sender_id,
        'sender_name': user_name,
        'content': message.content,
        'timestamp': message.created_at.isoformat()
    } for message, user_name in messages])

@swag_from({
    'tags': ['Chat'],
    'summary': 'Send a message to a chat room',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'room_id': {'type': 'string', 'example': 'dm-userA-userB'},
                    'sender_id': {'type': 'string', 'example': 'userA'},
                    'content': {'type': 'string', 'example': 'Hello, want to team up?'}
                },
                'required': ['room_id', 'sender_id', 'content']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Message sent successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'sent'}
                }
            }
        },
        403: {
            'description': 'Unauthorized access',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Unauthorized'}
                }
            }
        },
        404: {
            'description': 'Room not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Room not found'}
                }
            }
        }
    }
})
@chat_bp.route('/send', methods=['POST'])
def send_message():
    data = request.json
    room_id = data['room_id']
    sender_id = data['sender_id']
    
    # Verify sender has access to room
    chat = Chat.query.filter_by(room_id=room_id).first()
    if not chat:
        return jsonify({"error": "Room not found"}), 404
    if sender_id not in chat.participants:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Save to DB
    new_message = Message(
        room_id=room_id,
        sender_id=sender_id,
        content=data['content']
    )
    db.session.add(new_message)
    db.session.commit()
    
    # Trigger Pusher event
    pusher_client.trigger(room_id, 'new_message', {
        'sender': sender_id,
        'content': data['content'],
        'timestamp': (datetime.utcnow() + IST_OFFSET).isoformat()
    })
    
    return jsonify({"status": "sent"}), 200

# Join Open Group (Modified)
@chat_bp.route('/join-open-group', methods=['POST'])
def join_open_group():
    data = request.json
    user_id = data.get('user_id')
    topic_slug = data.get('topic_slug')
    
    if not user_id or not topic_slug:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Use explicit locking to prevent race conditions
        group = Chat.query.filter_by(room_id=f"open-{topic_slug}").with_for_update().first()
        if not group:
            return jsonify({"error": "Group not found"}), 404
        
        # Initialize if null
        if group.participants is None:
            group.participants = []
        
        # Check if user already in group
        if user_id not in group.participants:
            group.add_participant(user_id)
            db.session.commit()
        
        # Refresh the object to get current state
        db.session.refresh(group)
        
        return jsonify({
            'room_id': group.room_id,
            'topic': group.topic,
            'participant_count': len(group.participants),
            'participants': group.participants
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Leave Open Group
@chat_bp.route('/leave-open-group', methods=['POST'])
@swag_from({
    'tags': ['Chat'],
    'summary': 'Leave an open group',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'user_id': {
                    'type': 'string',
                    'example': 'user_123'
                },
                'topic_slug': {
                    'type': 'string',
                    'example': 'web-development'
                }
            },
            'required': ['user_id', 'topic_slug']
        }
    }],
    'responses': {
        200: {
            'description': 'Successfully left group',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Missing required fields',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Group not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def leave_open_group():
    data = request.json
    user_id = data.get('user_id')
    topic_slug = data.get('topic_slug')
    
    if not user_id or not topic_slug:
        return jsonify({"error": "Missing required fields"}), 400
    
    group = Chat.query.filter_by(room_id=f"open-{topic_slug}").first()
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    if user_id in group.participants:
        group.participants.remove(user_id)
        db.session.commit()
    
    return jsonify({"status": "left"}), 200

@chat_bp.route('/project-chat/create/<int:project_id>', methods=['POST'])
def create_project_chat(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    # Check if chat already exists
    existing_chat = Chat.query.filter_by(room_id=project.chat_room_id).first()
    if existing_chat:
        return jsonify({"room_id": existing_chat.room_id}), 200
    
    new_chat = Chat(
        room_id=project.chat_room_id,
        is_group=True,
        participants=[project.clerkId]
    )
    db.session.add(new_chat)
    db.session.commit()
    
    return jsonify({"room_id": new_chat.room_id}), 201

@swag_from({
    'tags': ['Project Chat'],
    'summary': 'Invite user to project chat',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'project_id': {'type': 'integer', 'example': 1},
                    'requester_id': {'type': 'string', 'example': 'userA'},
                    'target_id': {'type': 'string', 'example': 'userB'}
                },
                'required': ['project_id', 'requester_id', 'target_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User added to project chat',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'added'}
                }
            }
        },
        403: {
            'description': 'Unauthorized',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Unauthorized'}
                }
            }
        },
        404: {
            'description': 'Project or chat not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Project not found'}
                }
            }
        }
    }
})
@chat_bp.route('/project-chat/add', methods=['POST'])
def project_chat_invite():
    data = request.json
    project_id = data.get('project_id')
    requester_id = data.get('requester_id')
    target_id = data.get('target_id')
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    if project.clerkId != requester_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    chat = Chat.query.filter_by(room_id=project.chat_room_id).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    
    if target_id not in chat.participants:
        # Create a new list to ensure SQLAlchemy detects the change
        participants = list(chat.participants)
        participants.append(target_id)
        chat.participants = participants
        
        # Mark the field as modified
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(chat, 'participants')
        
        db.session.commit()
    
    return jsonify({
        "status": "added",
        "participants": chat.participants  # Return updated list for debugging
    }), 200

@chat_bp.route('/project-chat/auto-create/<int:project_id>', methods=['POST'])
@swag_from({
    'tags': ['Project Chat'],
    'summary': 'Auto-create project chat room',
    'parameters': [
        {
            'name': 'project_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        },
        {
            'name': 'clerkId',
            'in': 'query',
            'type': 'string',
            'required': True
        }
    ],
    'responses': {
        201: {'description': 'Chat created'},
        400: {'description': 'Already exists'},
        403: {'description': 'Unauthorized'}
    }
})
def auto_create_project_chat(project_id):
    project = Project.query.get(project_id)
    user_id = request.args.get('clerkId')
    
    if not project:
        return jsonify({"error": "Project not found"}), 404
    if project.clerkId != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    if project.chat:
        return jsonify({"warning": "Chat already exists"}), 400
        
    # Chat will be automatically created via SQLAlchemy event
    return jsonify({
        "message": "Chat will be created automatically",
        "chat_room_id": project.chat_room_id
    }), 201

@swag_from({
    'tags': ['Project Chat'],
    'summary': 'Remove user from project chat',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'project_id': {'type': 'integer', 'example': 1},
                    'requester_id': {'type': 'string', 'example': 'owner1'},
                    'target_id': {'type': 'string', 'example': 'user1'}
                },
                'required': ['project_id', 'requester_id', 'target_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User removed from project chat',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'removed'}
                }
            }
        },
        403: {
            'description': 'Unauthorized',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Unauthorized'}
                }
            }
        },
        404: {
            'description': 'Project or chat not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Project not found'}
                }
            }
        }
    }
})
@chat_bp.route('/project-chat/kick', methods=['POST'])
def project_chat_kick():
    data = request.json
    project_id = data.get('project_id')
    requester_id = data.get('requester_id')
    target_id = data.get('target_id')
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    if project.clerkId != requester_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    chat = Chat.query.filter_by(room_id=project.chat_room_id).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    
    if target_id in chat.participants:
        # Create a new list to ensure SQLAlchemy detects the change
        participants = list(chat.participants)
        participants.remove(target_id)
        chat.participants = participants
        
        # Mark the field as modified
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(chat, 'participants')
        
        db.session.commit()
    
    return jsonify({
        "status": "removed",
        "participants": chat.participants  # Return updated list for debugging
    }), 200