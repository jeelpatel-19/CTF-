from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from auth_utils import generate_token, token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters long'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    existing_user = cursor.execute(
        'SELECT id FROM users WHERE username = ? OR email = ?', (username, email)
    ).fetchone()

    if existing_user:
        conn.close()
        return jsonify({'error': 'Username or email already registered'}), 400

    password_hash = generate_password_hash(password)
    cursor.execute(
        'INSERT INTO users (username, email, password_hash, role, points) VALUES (?, ?, ?, ?, ?)',
        (username, email, password_hash, 'user', 0)
    )
    user_id = cursor.lastrowid
    conn.commit()

    user = cursor.execute('SELECT id, username, email, role, points, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    token = generate_token(user['id'], user['username'], user['role'])
    user_dict = dict(user)

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': user_dict
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    account = data.get('account', '').strip() # username or email
    username = data.get('username', '').strip()
    password = data.get('password', '')

    login_identifier = account or username
    if not login_identifier or not password:
        return jsonify({'error': 'Username/email and password are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        'SELECT * FROM users WHERE username = ? OR email = ?', 
        (login_identifier, login_identifier.lower())
    ).fetchone()

    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid username/email or password'}), 401

    token = generate_token(user['id'], user['username'], user['role'])
    user_dict = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role'],
        'points': user['points'],
        'created_at': user['created_at']
    }

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user_dict
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def me():
    user = request.current_user
    conn = get_db_connection()
    cursor = conn.cursor()

    # Recalculate points & solve count
    solves_count = cursor.execute('SELECT COUNT(*) as count FROM solves WHERE user_id = ?', (user['id'],)).fetchone()['count']
    total_challenges = cursor.execute('SELECT COUNT(*) as count FROM challenges').fetchone()['count']
    
    # User rank
    leaderboard = cursor.execute('''
        SELECT id, points FROM users ORDER BY points DESC, id ASC
    ''').fetchall()
    
    rank = 1
    for idx, u in enumerate(leaderboard, 1):
        if u['id'] == user['id']:
            rank = idx
            break

    conn.close()

    user_data = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role'],
        'points': user['points'],
        'solves_count': solves_count,
        'total_challenges': total_challenges,
        'rank': rank,
        'created_at': user['created_at']
    }

    return jsonify({'user': user_data}), 200
