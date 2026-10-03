from flask import Blueprint, jsonify, request
from database import get_db_connection
from auth_utils import decode_token

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('', methods=['GET'])
@leaderboard_bp.route('/', methods=['GET'])
def get_leaderboard():
    token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    
    current_user_id = None
    if token:
        payload = decode_token(token)
        if payload:
            current_user_id = payload.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query player users with their total solved challenges count and total points
    users_data = cursor.execute('''
        SELECT u.id, u.username, u.points, u.role, u.created_at,
               (SELECT COUNT(*) FROM solves s WHERE s.user_id = u.id) as solves_count
        FROM users u
        WHERE u.role != 'admin'
        ORDER BY u.points DESC, solves_count DESC, u.id ASC
    ''').fetchall()

    leaderboard = []
    for rank, u in enumerate(users_data, 1):
        u_dict = {
            'rank': rank,
            'id': u['id'],
            'username': u['username'],
            'points': u['points'],
            'solves_count': u['solves_count'],
            'is_current_user': (u['id'] == current_user_id)
        }
        leaderboard.append(u_dict)

    conn.close()
    return jsonify({'leaderboard': leaderboard}), 200
