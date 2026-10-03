from flask import Blueprint, jsonify, request
from database import get_db_connection
from auth_utils import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def admin_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    total_users = cursor.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_challenges = cursor.execute('SELECT COUNT(*) as count FROM challenges').fetchone()['count']
    total_submissions = cursor.execute('SELECT COUNT(*) as count FROM submissions').fetchone()['count']
    total_solves = cursor.execute('SELECT COUNT(*) as count FROM solves').fetchone()['count']

    solve_rate = round((total_solves / total_submissions * 100), 1) if total_submissions > 0 else 0.0

    conn.close()
    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_challenges': total_challenges,
            'total_submissions': total_submissions,
            'total_solves': total_solves,
            'solve_rate': solve_rate
        }
    }), 200


@admin_bp.route('/challenges', methods=['GET'])
@admin_required
def admin_get_challenges():
    conn = get_db_connection()
    cursor = conn.cursor()

    challenges = cursor.execute('SELECT * FROM challenges ORDER BY id DESC').fetchall()
    result = []
    for c in challenges:
        c_dict = dict(c)
        hints = cursor.execute('SELECT * FROM hints WHERE challenge_id = ?', (c['id'],)).fetchall()
        c_dict['hints'] = [dict(h) for h in hints]
        c_dict['solves_count'] = cursor.execute('SELECT COUNT(*) as count FROM solves WHERE challenge_id = ?', (c['id'],)).fetchone()['count']
        result.append(c_dict)

    conn.close()
    return jsonify({'challenges': result}), 200


@admin_bp.route('/challenges', methods=['POST'])
@admin_required
def admin_create_challenge():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    category = data.get('category', '').strip()
    difficulty = data.get('difficulty', '').strip()
    points = data.get('points', 0)
    flag = data.get('flag', '').strip()
    target_url = data.get('target_url', '').strip() or None
    file_url = data.get('file_url', '').strip() or None
    hints_data = data.get('hints', [])

    if not title or not description or not category or not difficulty or not flag:
        return jsonify({'error': 'Title, description, category, difficulty, and flag are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO challenges (title, description, category, difficulty, points, flag, target_url, file_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, category, difficulty, points, flag, target_url, file_url))

    challenge_id = cursor.lastrowid

    for h in hints_data:
        hint_text = h.get('hint_text', '').strip()
        penalty = h.get('penalty', 0)
        if hint_text:
            cursor.execute('''
                INSERT INTO hints (challenge_id, hint_text, penalty)
                VALUES (?, ?, ?)
            ''', (challenge_id, hint_text, penalty))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Challenge created successfully', 'challenge_id': challenge_id}), 201


@admin_bp.route('/challenges/<int:challenge_id>', methods=['PUT'])
@admin_required
def admin_update_challenge(challenge_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    cursor = conn.cursor()

    existing = cursor.execute('SELECT id FROM challenges WHERE id = ?', (challenge_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({'error': 'Challenge not found'}), 404

    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    category = data.get('category', '').strip()
    difficulty = data.get('difficulty', '').strip()
    points = data.get('points', 0)
    flag = data.get('flag', '').strip()
    target_url = data.get('target_url', '').strip() or None
    file_url = data.get('file_url', '').strip() or None

    cursor.execute('''
        UPDATE challenges
        SET title = ?, description = ?, category = ?, difficulty = ?, points = ?, flag = ?, target_url = ?, file_url = ?
        WHERE id = ?
    ''', (title, description, category, difficulty, points, flag, target_url, file_url, challenge_id))

    # Optional hints update
    if 'hints' in data:
        cursor.execute('DELETE FROM hints WHERE challenge_id = ?', (challenge_id,))
        for h in data['hints']:
            hint_text = h.get('hint_text', '').strip()
            penalty = h.get('penalty', 0)
            if hint_text:
                cursor.execute('''
                    INSERT INTO hints (challenge_id, hint_text, penalty)
                    VALUES (?, ?, ?)
                ''', (challenge_id, hint_text, penalty))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Challenge updated successfully'}), 200


@admin_bp.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@admin_required
def admin_delete_challenge(challenge_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM challenges WHERE id = ?', (challenge_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Challenge deleted successfully'}), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def admin_get_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    users = cursor.execute('''
        SELECT u.id, u.username, u.email, u.role, u.points, u.created_at,
               (SELECT COUNT(*) FROM solves s WHERE s.user_id = u.id) as solves_count
        FROM users u ORDER BY u.id ASC
    ''').fetchall()

    conn.close()
    return jsonify({'users': [dict(u) for u in users]}), 200


@admin_bp.route('/submissions', methods=['GET'])
@admin_required
def admin_get_submissions():
    conn = get_db_connection()
    cursor = conn.cursor()

    submissions = cursor.execute('''
        SELECT sub.id, sub.submitted_flag, sub.is_correct, sub.submitted_at,
               u.username, c.title as challenge_title
        FROM submissions sub
        JOIN users u ON sub.user_id = u.id
        JOIN challenges c ON sub.challenge_id = c.id
        ORDER BY sub.submitted_at DESC
        LIMIT 50
    ''').fetchall()

    conn.close()
    return jsonify({'submissions': [dict(s) for s in submissions]}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    current_admin = request.current_user
    if user_id == current_admin['id']:
        return jsonify({'error': 'You cannot delete your own admin account.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    target_user = cursor.execute('SELECT id, username, role FROM users WHERE id = ?', (user_id,)).fetchone()
    if not target_user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    if target_user['role'] == 'admin':
        conn.close()
        return jsonify({'error': 'Protected admin accounts cannot be deleted.'}), 400

    # Delete user (foreign key ON DELETE CASCADE handles dependent tables)
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': f"User '{target_user['username']}' deleted successfully"}), 200


@admin_bp.route('/users/clear-players', methods=['DELETE', 'POST'])
@admin_required
def admin_clear_all_players():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete all non-admin player accounts
    cursor.execute("DELETE FROM users WHERE role != 'admin'")
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()

    return jsonify({
        'message': 'All registered player accounts cleared successfully',
        'cleared_count': deleted_count
    }), 200

