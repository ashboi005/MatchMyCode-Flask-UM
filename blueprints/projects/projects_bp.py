from flask import Blueprint, request, jsonify
from config import db
from blueprints.projects.models import Project
from blueprints.auth.models import User
from flasgger import swag_from

projects_bp = Blueprint('projects_bp', __name__)

@swag_from({
    'tags': ['Projects'],
    'summary': 'Create a new project',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clerkId': {'type': 'string'},
                    'name': {'type': 'string'},
                    'title': {'type': 'string'},
                    'short_description': {'type': 'string'},
                    'big_description': {'type': 'string'},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'progress': {'type': 'integer'},
                    'duration': {'type': 'string'},
                    'goals': {'type': 'string'},
                    'skills_required': {'type': 'array', 'items': {'type': 'string'}},
                    'project_status': {'type': 'string', 'enum': ['open', 'closed']},
                    'project_links': {'type': 'array', 'items': {'type': 'string'}}
                },
                'required': ['clerkId', 'name', 'title', 'short_description', 'big_description']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Project created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        '400': {
            'description': 'Invalid input',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
@projects_bp.route('/create_project', methods=['POST'])
def create_project():
    data = request.get_json()
    
    try:
        # Check required fields
        required = ['clerkId', 'name', 'title', 'short_description', 'big_description']
        if not all(field in data for field in required):
            return jsonify({"error": "Missing required fields"}), 400

        # Start transaction
        db.session.begin()

        # Verify user exists
        user = User.query.filter_by(clerkId=data['clerkId']).first()
        if not user:
            db.session.rollback()
            return jsonify({"error": "User not found"}), 404

        # Create project
        new_project = Project(
            clerkId=data['clerkId'],
            name=data['name'],
            title=data['title'],
            short_description=data['short_description'],
            big_description=data['big_description'],
            tags=data.get('tags', []),
            progress=data.get('progress', 0),
            duration=data.get('duration', ""),
            goals=data.get('goals', ""),
            skills_required=data.get('skills_required', []),
            project_status=data.get('project_status', 'open'),
            project_links=data.get('project_links', [])
        )
        
        db.session.add(new_project)
        db.session.commit()
        return jsonify({"message": "Project created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@swag_from({
    'tags': ['Projects'],
    'summary': 'Update an existing project',
    'parameters': [
        {
            'name': 'project_id',
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
                    'title': {'type': 'string'},
                    'short_description': {'type': 'string'},
                    'big_description': {'type': 'string'},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'progress': {'type': 'integer'},
                    'duration': {'type': 'string'},
                    'goals': {'type': 'string'},
                    'skills_required': {'type': 'array', 'items': {'type': 'string'}},
                    'project_status': {'type': 'string', 'enum': ['open', 'closed']},
                    'project_links': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Project updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        '404': {
            'description': 'Project not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
@projects_bp.route('/update_project/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json()
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    project.title = data.get('title', project.title)
    project.short_description = data.get('short_description', project.short_description)
    project.big_description = data.get('big_description', project.big_description)
    project.tags = data.get('tags', project.tags)
    project.progress = data.get('progress', project.progress)
    project.duration = data.get('duration', project.duration)
    project.goals = data.get('goals', project.goals)
    project.skills_required = data.get('skills_required', project.skills_required)
    project.project_status = data.get('project_status', project.project_status)
    project.project_links = data.get('project_links', project.project_links)
    
    db.session.commit()
    return jsonify({"message": "Project updated successfully"}), 200

@swag_from({
    'tags': ['Projects'],
    'summary': 'Delete a project',
    'parameters': [
        {
            'name': 'project_id',
            'in': 'path',
            'required': True,
            'type': 'integer'
        }
    ],
    'responses': {
        '200': {
            'description': 'Project deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        '404': {
            'description': 'Project not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
@projects_bp.route('/delete_project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted successfully"}), 200

@swag_from({
    'tags': ['Projects'],
    'summary': 'Get all projects for a specific user',
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
            'description': 'List of user projects',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'clerkId': {'type': 'string'},
                        'name': {'type': 'string'},
                        'title': {'type': 'string'},
                        'short_description': {'type': 'string'},
                        'big_description': {'type': 'string'},
                        'tags': {'type': 'array', 'items': {'type': 'string'}},
                        'progress': {'type': 'integer'},
                        'duration': {'type': 'string'},
                        'goals': {'type': 'string'},
                        'skills_required': {'type': 'array', 'items': {'type': 'string'}},
                        'project_status': {'type': 'string'},
                        'project_links': {'type': 'array', 'items': {'type': 'string'}}
                    }
                }
            }
        }
    }
})
@projects_bp.route('/get_user_projects/<string:clerkId>', methods=['GET'])
def get_user_projects(clerkId):
    projects = Project.query.filter_by(clerkId=clerkId).all()
    return jsonify([project.to_dict() for project in projects]), 200

@swag_from({
    'tags': ['Projects'],
    'summary': 'Get all open projects for the feed',
    'responses': {
        '200': {
            'description': 'List of open projects',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'clerkId': {'type': 'string'},
                        'name': {'type': 'string'},
                        'title': {'type': 'string'},
                        'short_description': {'type': 'string'},
                        'big_description': {'type': 'string'},
                        'tags': {'type': 'array', 'items': {'type': 'string'}},
                        'progress': {'type': 'integer'},
                        'duration': {'type': 'string'},
                        'goals': {'type': 'string'},
                        'skills_required': {'type': 'array', 'items': {'type': 'string'}},
                        'project_status': {'type': 'string'},
                        'project_links': {'type': 'array', 'items': {'type': 'string'}}
                    }
                }
            }
        }
    }
})
@projects_bp.route('/feed_projects', methods=['GET'])
def feed_projects():
    open_projects = Project.query.filter_by(project_status='open').all()
    return jsonify([project.to_dict() for project in open_projects]), 200

@swag_from({
    'tags': ['Projects'],
    'summary': 'Search projects by tags or skills',
    'parameters': [
        {
            'name': 'tags',
            'in': 'query',
            'type': 'string',
            'description': 'Tag to filter projects'
        },
        {
            'name': 'skills_required',
            'in': 'query',
            'type': 'string',
            'description': 'Skill required to filter projects'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of searched projects',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'clerkId': {'type': 'string'},
                        'name': {'type': 'string'},
                        'title': {'type': 'string'},
                        'short_description': {'type': 'string'},
                        'big_description': {'type': 'string'},
                        'tags': {'type': 'array', 'items': {'type': 'string'}},
                        'progress': {'type': 'integer'},
                        'duration': {'type': 'string'},
                        'goals': {'type': 'string'},
                        'skills_required': {'type': 'array', 'items': {'type': 'string'}},
                        'project_status': {'type': 'string'},
                        'project_links': {'type': 'array', 'items': {'type': 'string'}}
                    }
                }
            }
        }
    }
})
@projects_bp.route('/search_projects', methods=['GET'])
def search_projects():
    tags = request.args.get('tags')
    skills = request.args.get('skills_required')
    query = Project.query

    if tags:
        query = query.filter(Project.tags.contains([tags]))
    if skills:
        query = query.filter(Project.skills_required.contains([skills]))

    projects = query.all()
    return jsonify([project.to_dict() for project in projects]), 200

@swag_from({
    'tags': ['Projects'],
    'summary': 'Get project by ID',
    'parameters': [
        {
            'name': 'project_id',
            'in': 'path',
            'required': True,
            'type': 'integer'
        }
    ],
    'responses': {
        '200': {
            'description': 'Project details',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'clerkId': {'type': 'string'},
                    'name': {'type': 'string'},
                    'title': {'type': 'string'},
                    'short_description': {'type': 'string'},
                    'big_description': {'type': 'string'},
                    'tags': {'type': 'array', 'items': {'type': 'string'}},
                    'progress': {'type': 'integer'},
                    'duration': {'type': 'string'},
                    'goals': {'type': 'string'},
                    'skills_required': {'type': 'array', 'items': {'type': 'string'}},
                    'project_status': {'type': 'string'},
                    'project_links': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        },
        '404': {
            'description': 'Project not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
@projects_bp.route('/get_project/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project.to_dict()), 200

