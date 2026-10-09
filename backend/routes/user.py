from flask import Blueprint, jsonify, request
from database import get_db_connection
from auth_utils import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard():
    user = request.current_user
    conn = get_db_connection()
    cursor = conn.cursor()

    # User details
    user_info = cursor.execute(
        'SELECT id, username, email, points, role, created_at FROM users WHERE id = ?',
        (user['id'],)
    ).fetchone()

    # Total stats
    total_challenges = cursor.execute('SELECT COUNT(*) as count FROM challenges').fetchone()['count']
    total_solves = cursor.execute('SELECT COUNT(*) as count FROM solves WHERE user_id = ?', (user['id'],)).fetchone()['count']
    remaining_challenges = max(0, total_challenges - total_solves)

    # Rank
    all_users = cursor.execute('''
        SELECT u.id, u.points,
               (SELECT COALESCE(SUM(s.time_taken_seconds), 0) FROM solves s WHERE s.user_id = u.id) as total_solve_time
        FROM users u
        WHERE u.role != 'admin'
        ORDER BY u.points DESC, total_solve_time ASC, u.id ASC
    ''').fetchall()
    rank = 1
    for idx, u in enumerate(all_users, 1):
        if u['id'] == user['id']:
            rank = idx
            break

    # Recent solves activity
    recent_activity = cursor.execute('''
        SELECT s.id, s.points_earned, s.solved_at, c.id as challenge_id, c.title, c.category, c.difficulty
        FROM solves s
        JOIN challenges c ON s.challenge_id = c.id
        WHERE s.user_id = ?
        ORDER BY s.solved_at DESC
        LIMIT 5
    ''', (user['id'],)).fetchall()

    # Recommended unsolved challenges (up to 3)
    recommended = cursor.execute('''
        SELECT id, title, description, category, difficulty, points
        FROM challenges
        WHERE id NOT IN (SELECT challenge_id FROM solves WHERE user_id = ?)
        ORDER BY points ASC, id ASC
        LIMIT 3
    ''', (user['id'],)).fetchall()

    conn.close()

    return jsonify({
        'user': dict(user_info),
        'stats': {
            'points': user_info['points'],
            'solved_count': total_solves,
            'total_challenges': total_challenges,
            'remaining_count': remaining_challenges,
            'rank': rank
        },
        'recent_activity': [dict(a) for a in recent_activity],
        'recommended_challenges': [dict(r) for r in recommended]
    }), 200
