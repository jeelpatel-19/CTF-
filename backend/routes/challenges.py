from flask import Blueprint, request, jsonify, render_template_string, make_response
from database import get_db_connection
from auth_utils import token_required, decode_token

challenges_bp = Blueprint('challenges', __name__)

def get_backend_base_url():
    scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
    host = request.headers.get('X-Forwarded-Host', request.host)
    return f"{scheme}://{host}"

def format_challenge_urls(c_dict):
    base_url = get_backend_base_url()
    
    if c_dict.get('target_url'):
        raw_target = c_dict['target_url']
        if raw_target.startswith('http://localhost:5000'):
            c_dict['target_url'] = raw_target.replace('http://localhost:5000', base_url)
        elif raw_target.startswith('/'):
            c_dict['target_url'] = f"{base_url}{raw_target}"

    if c_dict.get('file_url'):
        raw_file = c_dict['file_url']
        if raw_file.startswith('http://localhost:5000'):
            c_dict['file_url'] = raw_file.replace('http://localhost:5000', base_url)
        elif raw_file.startswith('/'):
            c_dict['file_url'] = f"{base_url}{raw_file}"

    return c_dict


@challenges_bp.route('', methods=['GET'])
@challenges_bp.route('/', methods=['GET'])
@token_required
def get_challenges():
    user = request.current_user
    current_user_id = user['id']

    conn = get_db_connection()
    cursor = conn.cursor()

    challenges = cursor.execute('''
        SELECT id, title, description, category, difficulty, points, target_url, file_url, created_at
        FROM challenges ORDER BY points ASC, id ASC
    ''').fetchall()

    solved_ids = set()
    if current_user_id:
        solves = cursor.execute('SELECT challenge_id FROM solves WHERE user_id = ?', (current_user_id,)).fetchall()
        solved_ids = {s['challenge_id'] for s in solves}

    result = []
    for c in challenges:
        c_dict = dict(c)
        c_dict['is_solved'] = c_dict['id'] in solved_ids
        
        # Get hint count
        hint_count = cursor.execute('SELECT COUNT(*) as count FROM hints WHERE challenge_id = ?', (c_dict['id'],)).fetchone()['count']
        c_dict['hint_count'] = hint_count
        c_dict = format_challenge_urls(c_dict)
        result.append(c_dict)

    conn.close()
    return jsonify({'challenges': result}), 200


@challenges_bp.route('/<int:challenge_id>', methods=['GET'])
@token_required
def get_challenge_detail(challenge_id):
    user = request.current_user
    current_user_id = user['id']

    conn = get_db_connection()
    cursor = conn.cursor()

    challenge = cursor.execute('''
        SELECT id, title, description, category, difficulty, points, target_url, file_url, created_at
        FROM challenges WHERE id = ?
    ''', (challenge_id,)).fetchone()

    if not challenge:
        conn.close()
        return jsonify({'error': 'Challenge not found'}), 404

    c_dict = dict(challenge)
    
    # Check solve status
    c_dict['is_solved'] = False
    c_dict['time_taken_seconds'] = None
    if current_user_id:
        solve = cursor.execute('SELECT solved_at, points_earned, time_taken_seconds FROM solves WHERE user_id = ? AND challenge_id = ?', 
                               (current_user_id, challenge_id)).fetchone()
        if solve:
            c_dict['is_solved'] = True
            c_dict['solved_at'] = solve['solved_at']
            c_dict['points_earned'] = solve['points_earned']
            c_dict['time_taken_seconds'] = solve['time_taken_seconds']

    # Server-side challenge start time tracking
    start_rec = cursor.execute(
        'SELECT started_at FROM challenge_starts WHERE user_id = ? AND challenge_id = ?',
        (current_user_id, challenge_id)
    ).fetchone()

    if not start_rec and not c_dict['is_solved']:
        cursor.execute(
            'INSERT INTO challenge_starts (user_id, challenge_id) VALUES (?, ?)',
            (current_user_id, challenge_id)
        )
        conn.commit()
        start_rec = cursor.execute(
            'SELECT started_at FROM challenge_starts WHERE user_id = ? AND challenge_id = ?',
            (current_user_id, challenge_id)
        ).fetchone()

    c_dict['started_at'] = start_rec['started_at'] if start_rec else None

    # Get hints
    hints = cursor.execute('SELECT id, challenge_id, penalty FROM hints WHERE challenge_id = ?', (challenge_id,)).fetchall()
    
    unlocked_hint_ids = set()
    if current_user_id:
        unlocked = cursor.execute('''
            SELECT hint_id FROM user_hints WHERE user_id = ?
        ''', (current_user_id,)).fetchall()
        unlocked_hint_ids = {u['hint_id'] for u in unlocked}

    hint_list = []
    for index, h in enumerate(hints, 1):
        h_dict = {
            'id': h['id'],
            'index': index,
            'penalty': h['penalty'],
            'is_unlocked': h['id'] in unlocked_hint_ids
        }
        if h_dict['is_unlocked']:
            # Fetch hint text if unlocked
            full_hint = cursor.execute('SELECT hint_text FROM hints WHERE id = ?', (h['id'],)).fetchone()
            h_dict['hint_text'] = full_hint['hint_text'] if full_hint else ''
        else:
            h_dict['hint_text'] = None # Hide hint text if not unlocked!

        hint_list.append(h_dict)

    c_dict['hints'] = hint_list
    c_dict = format_challenge_urls(c_dict)
    conn.close()
    return jsonify({'challenge': c_dict}), 200


@challenges_bp.route('/<int:challenge_id>/submit', methods=['POST'])
@token_required
def submit_flag(challenge_id):
    user = request.current_user
    data = request.get_json() or {}
    submitted_flag = data.get('flag', '').strip()

    if not submitted_flag:
        return jsonify({'error': 'Flag cannot be empty'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    challenge = cursor.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()
    if not challenge:
        conn.close()
        return jsonify({'error': 'Challenge not found'}), 404

    # Check if already solved
    existing_solve = cursor.execute(
        'SELECT id FROM solves WHERE user_id = ? AND challenge_id = ?',
        (user['id'], challenge_id)
    ).fetchone()

    if existing_solve:
        conn.close()
        return jsonify({
            'success': False,
            'message': 'You have already solved this challenge!',
            'already_solved': True
        }), 400

    is_correct = (submitted_flag == challenge['flag'].strip())

    # Record submission attempt
    cursor.execute(
        'INSERT INTO submissions (user_id, challenge_id, submitted_flag, is_correct) VALUES (?, ?, ?, ?)',
        (user['id'], challenge_id, submitted_flag, 1 if is_correct else 0)
    )

    if not is_correct:
        conn.commit()
        conn.close()
        return jsonify({
            'success': False,
            'message': '✕ Incorrect flag. Keep investigating!'
        }), 200

    # Calculate net points (Base points - total penalties of unlocked hints for this challenge)
    unlocked_penalties = cursor.execute('''
        SELECT SUM(h.penalty) as total_penalty
        FROM user_hints uh
        JOIN hints h ON uh.hint_id = h.id
        WHERE uh.user_id = ? AND h.challenge_id = ?
    ''', (user['id'], challenge_id)).fetchone()['total_penalty'] or 0

    points_earned = max(0, challenge['points'] - unlocked_penalties)

    # Calculate server-side elapsed time (server_current_time - server_start_time)
    elapsed_row = cursor.execute('''
        SELECT CAST((julianday('now') - julianday(started_at)) * 86400 AS INTEGER) as elapsed
        FROM challenge_starts
        WHERE user_id = ? AND challenge_id = ?
    ''', (user['id'], challenge_id)).fetchone()

    time_taken_seconds = 0
    if elapsed_row and elapsed_row['elapsed'] is not None:
        time_taken_seconds = max(0, elapsed_row['elapsed'])

    # Insert into solves with time_taken_seconds
    cursor.execute(
        'INSERT INTO solves (user_id, challenge_id, points_earned, time_taken_seconds) VALUES (?, ?, ?, ?)',
        (user['id'], challenge_id, points_earned, time_taken_seconds)
    )

    # Update user points
    cursor.execute(
        'UPDATE users SET points = points + ? WHERE id = ?',
        (points_earned, user['id'])
    )

    conn.commit()

    # Get updated user total points
    updated_user = cursor.execute('SELECT points FROM users WHERE id = ?', (user['id'],)).fetchone()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'✓ Correct flag! You earned {points_earned} points.',
        'points_earned': points_earned,
        'total_points': updated_user['points'],
        'time_taken_seconds': time_taken_seconds
    }), 200


@challenges_bp.route('/target/forgotten-header', methods=['GET'])
def target_forgotten_header():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CyberQuest Secure Gateway</title>
        <style>
            body { background: #0b0f19; color: #e2e8f0; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 40px; max-width: 500px; text-align: center; }
            h1 { color: #10b981; margin-bottom: 10px; }
            p { color: #94a3b8; line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🌐 CyberQuest Secure Gateway</h1>
            <p>Welcome to the main entry point. All incoming client connections are logged and verified by network edge servers.</p>
            <p style="color: #64748b; font-size: 0.9rem; margin-top: 20px;">Notice: Visible content contains public metadata only.</p>
        </div>
    </body>
    </html>
    """
    resp = make_response(render_template_string(html_content))
    resp.headers['X-Secret-Flag'] = 'CTF{header_was_never_empty}'
    return resp


@challenges_bp.route('/target/room', methods=['GET'])
def target_room():
    user_id = request.args.get('user_id', '101').strip()
    
    if user_id == '102':
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Supervisor Vault #102</title>
            <style>
                body { background: #0b0f19; color: #e2e8f0; font-family: sans-serif; padding: 40px; display: flex; justify-content: center; }
                .card { background: #111827; border: 1px solid #10b981; border-radius: 12px; padding: 30px; max-width: 600px; width: 100%; }
                h1 { color: #10b981; }
                .secret-box { background: #0d1322; border: 1px solid #374151; padding: 15px; font-family: monospace; color: #38bdf8; margin-top: 15px; border-radius: 6px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🔑 Room #102 — Supervisor Vault</h1>
                <p>Welcome, Administrator. Access granted to privileged supervisor logs.</p>
                <div class="secret-box">
                    Vault Confidential Code: CTF{numbers_are_not_permissions}
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_content)
    else:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Guest Room #{user_id}</title>
            <style>
                body {{ background: #0b0f19; color: #e2e8f0; font-family: sans-serif; padding: 40px; display: flex; justify-content: center; }}
                .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 30px; max-width: 600px; width: 100%; }}
                h1 {{ color: #3b82f6; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🚪 Room #{user_id} — Guest Quarters</h1>
                <p>Status: Occupied by Guest User #{user_id}.</p>
                <p style="color: #94a3b8;">Standard guest environment. No administrative keys stored in this location.</p>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_content)


@challenges_bp.route('/target/hidden-param', methods=['GET'])
def target_hidden_param():
    debug_param = request.args.get('debug', '').strip().lower()
    
    if debug_param in ['true', '1']:
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Internal Diagnostic Output</title>
            <style>
                body { background: #0b0f19; color: #e2e8f0; font-family: monospace; padding: 40px; display: flex; justify-content: center; }
                .card { background: #111827; border: 1px solid #f59e0b; border-radius: 12px; padding: 30px; max-width: 650px; width: 100%; }
                h1 { color: #f59e0b; }
                .flag-box { background: #0d1322; border-left: 4px solid #10b981; padding: 15px; color: #10b981; font-weight: bold; margin-top: 15px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🛠️ DEBUG DIAGNOSTIC MODE INITIALIZED</h1>
                <p>// Developer override parameter active.</p>
                <p>// Outputting system secrets dump...</p>
                <div class="flag-box">
                    FLAG: CTF{the_parameter_was_always_there}
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_content)
    else:
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>System Status Portal</title>
            <style>
                body { background: #0b0f19; color: #e2e8f0; font-family: sans-serif; padding: 40px; display: flex; justify-content: center; }
                .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 30px; max-width: 600px; width: 100%; }
                h1 { color: #10b981; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>⚙️ Infrastructure Status Portal</h1>
                <p>All core services operational. System health: 100%.</p>
                <p style="color: #64748b; font-size: 0.9rem;">Public client interface mode active.</p>
            </div>
            <!-- Developer Notice: Legacy status flags requiring debug overrides are inactive by default. -->
        </body>
        </html>
        """
        return render_template_string(html_content)

