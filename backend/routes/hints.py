from flask import Blueprint, jsonify, request
from database import get_db_connection
from auth_utils import token_required

hints_bp = Blueprint('hints', __name__)

@hints_bp.route('/<int:hint_id>/unlock', methods=['POST'])
@token_required
def unlock_hint(hint_id):
    user = request.current_user
    conn = get_db_connection()
    cursor = conn.cursor()

    hint = cursor.execute('SELECT * FROM hints WHERE id = ?', (hint_id,)).fetchone()
    if not hint:
        conn.close()
        return jsonify({'error': 'Hint not found'}), 404

    # Check if challenge is already solved
    solved = cursor.execute(
        'SELECT id FROM solves WHERE user_id = ? AND challenge_id = ?',
        (user['id'], hint['challenge_id'])
    ).fetchone()

    # Check if hint is already unlocked
    unlocked = cursor.execute(
        'SELECT id FROM user_hints WHERE user_id = ? AND hint_id = ?',
        (user['id'], hint_id)
    ).fetchone()

    if not unlocked:
        cursor.execute(
            'INSERT INTO user_hints (user_id, hint_id) VALUES (?, ?)',
            (user['id'], hint_id)
        )
        conn.commit()

    conn.close()

    return jsonify({
        'message': 'Hint unlocked successfully',
        'hint_id': hint_id,
        'hint_text': hint['hint_text'],
        'penalty': hint['penalty']
    }), 200
