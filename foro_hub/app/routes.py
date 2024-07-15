# app/routes.py

from flask import Blueprint, request, jsonify
from app.models import Topic
from app import db

bp = Blueprint('main', __name__)

@bp.route('/topics', methods=['POST'])
def create_topic():
    data = request.get_json()
    if not all(k in data for k in ('title', 'message', 'status', 'author', 'course')):
        return jsonify({'error': 'Missing fields'}), 400
    
    existing_topic = Topic.query.filter_by(title=data['title'], message=data['message']).first()
    if existing_topic:
        return jsonify({'error': 'Topic already exists'}), 400
    
    topic = Topic(
        title=data['title'],
        message=data['message'],
        status=data['status'],
        author=data['author'],
        course=data['course']
    )
    db.session.add(topic)
    db.session.commit()
    return jsonify({'message': 'Topic created'}), 201

@bp.route('/topics', methods=['GET'])
def get_topics():
    topics = Topic.query.all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'message': t.message,
        'created_at': t.created_at,
        'status': t.status,
        'author': t.author,
        'course': t.course
    } for t in topics]), 200

@bp.route('/topics/<int:id>', methods=['PUT'])
def update_topic(id):
    data = request.get_json()
    topic = Topic.query.get(id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    if not all(k in data for k in ('title', 'message', 'status', 'author', 'course')):
        return jsonify({'error': 'Missing fields'}), 400
    
    topic.title = data['title']
    topic.message = data['message']
    topic.status = data['status']
    topic.author = data['author']
    topic.course = data['course']
    db.session.commit()
    return jsonify({'message': 'Topic updated'}), 200

@bp.route('/topics/<int:id>', methods=['DELETE'])
def delete_topic(id):
    topic = Topic.query.get(id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    db.session.delete(topic)
    db.session.commit()
    return jsonify({'message': 'Topic deleted'}), 200








# app/routes.py

import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app.models import Topic
from app import db, config

bp = Blueprint('main', __name__)

# Funciones de autenticación

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Aquí deberías verificar las credenciales del usuario (esto es un ejemplo)
    if username == 'user' and password == 'pass':
        token = jwt.encode({
            'sub': username,
            'exp': datetime.utcnow() + timedelta(seconds=config.Config.JWT_EXPIRATION_DELTA)
        }, config.Config.JWT_SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# Middleware de autenticación
from functools import wraps
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 403
        try:
            jwt.decode(token, config.Config.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

@bp.route('/topics', methods=['POST'])
@token_required
def create_topic():
    data = request.get_json()
    if not all(k in data for k in ('title', 'message', 'status', 'author', 'course')):
        return jsonify({'error': 'Missing fields'}), 
