from flask import Blueprint, jsonify, request
from database import get_db_connection
from auth_utils import token_required

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('', methods=['GET'])
@leaderboard_bp.route('/', methods=['GET'])
@token_required
def get_leaderboard():
    user = request.current_user
    current_user_id = user['id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query player users with their total solved challenges count, total points, and total solve time
    users_data = cursor.execute('''
        SELECT u.id, u.username, u.points, u.role, u.created_at,
               (SELECT COUNT(*) FROM solves s WHERE s.user_id = u.id) as solves_count,
               (SELECT COALESCE(SUM(s.time_taken_seconds), 0) FROM solves s WHERE s.user_id = u.id) as total_solve_time
        FROM users u
        WHERE u.role != 'admin'
        ORDER BY u.points DESC, total_solve_time ASC, solves_count DESC, u.id ASC
    ''').fetchall()

    leaderboard = []
    for rank, u in enumerate(users_data, 1):
        u_dict = {
            'rank': rank,
            'id': u['id'],
            'username': u['username'],
            'points': u['points'],
            'solves_count': u['solves_count'],
            'total_solve_time': u['total_solve_time'],
            'is_current_user': (u['id'] == current_user_id)
        }
        leaderboard.append(u_dict)

    conn.close()
    return jsonify({'leaderboard': leaderboard}), 200
