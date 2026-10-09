import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
from database import get_db_connection

def generate_token(user_id, username, role):
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            token = request.cookies.get('auth_token')

        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE id = ?', (payload['user_id'],)).fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'User not found'}), 401

        request.current_user = dict(user)
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            token = request.cookies.get('auth_token')

        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401

        payload = decode_token(token)
        if not payload or payload.get('role') != 'admin':
            return jsonify({'error': 'Admin authorization required'}), 403

        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE id = ?', (payload['user_id'],)).fetchone()
        conn.close()

        if not user or user['role'] != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403

        request.current_user = dict(user)
        return f(*args, **kwargs)
    return decorated
