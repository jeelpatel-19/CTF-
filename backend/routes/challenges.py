from flask import Blueprint, request, jsonify, render_template_string, make_response
from database import get_db_connection
from auth_utils import token_required, decode_token

challenges_bp = Blueprint('challenges', __name__)

# ── Challenge 5: The Last Layer ─────────────────────────────────────────────
# Flag for Challenge 5 — SSTI exfiltrates this via {{ flag }}
_CH5_FLAG = 'CTF{one_layer_was_never_enough}'
_CH5_TOKEN = 'dev_preview_2026'

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


# ── Challenge 5: The Last Layer — routes integrated into main backend ────────

@challenges_bp.route('/target/last-layer-hub', methods=['GET'])
def target_last_layer_hub():
    """
    Landing page for Challenge 5 "The Last Layer".
    Replaces the standalone app that used to run on port 5005.
    Students navigate here via the target URL shown in the platform.
    """
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CyberQuest Developer Portal</title>
        <style>
            body {
                background: #0b0f19;
                color: #e2e8f0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 80vh;
            }
            .container {
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 12px;
                padding: 40px;
                max-width: 650px;
                width: 100%;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            }
            h1 { color: #10b981; margin-top: 0; font-size: 1.8rem; }
            p { color: #94a3b8; line-height: 1.6; }
            .badge {
                display: inline-block;
                background: rgba(16, 185, 129, 0.1);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 0.85rem;
                margin-top: 15px;
            }
            .code-box {
                background: #0b0f19;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 15px;
                font-family: monospace;
                color: #38bdf8;
                margin: 20px 0;
            }
        </style>
        <script src="/api/challenges/target/last-layer-hub/static/js/app.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>⚙️ CyberQuest Internal Developer Hub</h1>
            <p>Welcome to the staging portal for the CyberQuest internal administration suite.</p>
            <p>System administrators can generate automated diagnostic report previews and monitor infrastructure health.</p>
            <div class="code-box">
                // System Status: Staging Operational v2.4<br>
                // Authorization Level: Standard Client
            </div>
            <div class="badge">Environment: Staging (Restricted Access)</div>
        </div>
    </body>
    </html>
    """
    return html


@challenges_bp.route('/target/last-layer-hub/static/js/app.js', methods=['GET'])
def target_last_layer_js():
    """
    JavaScript file for the Challenge 5 developer hub.
    Contains the deliberately-left TODO comment that reveals the hidden debug endpoint.
    Students find this by inspecting page sources / Network tab.
    """
    js_content = """/**
 * CyberQuest Staging Application Client Logic
 * Version: 2.4.1-build809
 *
 * TODO: Remove legacy debug endpoint before production launch!
 * DEBUG ROUTE: /api/v1/debug_status?token=dev_preview_2026
 */
console.log("CyberQuest Developer Client loaded.");
"""
    return js_content, 200, {'Content-Type': 'application/javascript'}


@challenges_bp.route('/api/v1/debug_status', methods=['GET'])
def ch5_debug_status():
    """
    Challenge 5 — Stage 2: Hidden debug endpoint.
    Returns the access_key and admin_portal path only when the correct token is supplied.
    Token: dev_preview_2026
    """
    token = request.args.get('token', '')
    if token != _CH5_TOKEN:
        return jsonify({
            'error': 'Unauthorized access',
            'message': 'Invalid or missing preview token'
        }), 403

    base_url = get_backend_base_url()
    return jsonify({
        'status': 'healthy',
        'environment': 'staging',
        'admin_portal': '/admin_portal',
        'required_key': _CH5_TOKEN,
        'notice': (
            f'Access {base_url}/admin_portal?access_key={_CH5_TOKEN} '
            'for internal report preview generation.'
        )
    }), 200


@challenges_bp.route('/admin_portal', methods=['GET', 'POST'])
def ch5_admin_portal():
    """
    Challenge 5 — Stage 3 & 4: Admin report preview with intentional SSTI.
    Access requires ?access_key=dev_preview_2026.
    The 'title' parameter is rendered via render_template_string, allowing
    {{ flag }} or {{ 7*7 }} to be evaluated (Jinja2 SSTI).
    Flag is injected into the template context as the 'flag' variable.
    """
    access_key = request.args.get('access_key') or request.form.get('access_key')
    if access_key != _CH5_TOKEN:
        return """
        <!DOCTYPE html>
        <html>
        <head><title>403 Access Denied</title></head>
        <body style="background:#0b0f19;color:#ef4444;font-family:sans-serif;text-align:center;padding-top:100px;">
            <h1>403 Forbidden: Invalid Access Key</h1>
            <p style="color:#94a3b8;">You must supply a valid <code>access_key</code> parameter to access the administrative portal.</p>
        </body>
        </html>
        """, 403

    report_title = request.values.get('title', 'Default Security Summary')

    # Intentionally vulnerable template rendering — the pedagogical point of the challenge.
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin Report Preview — CyberQuest</title>
        <style>
            body {{ background-color: #0b0f19; color: #e2e8f0; font-family: sans-serif; padding: 40px; display: flex; justify-content: center; }}
            .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 30px; max-width: 650px; width: 100%; }}
            h1 {{ color: #10b981; }}
            .preview-area {{ background: #1e293b; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 6px; margin: 20px 0; }}
            form {{ display: flex; gap: 10px; margin-bottom: 20px; }}
            input[type="text"] {{ flex: 1; background: #0b0f19; border: 1px solid #374151; color: #e2e8f0; padding: 10px; border-radius: 6px; }}
            button {{ background: #10b981; color: #000; font-weight: bold; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛡️ Internal Admin Report Preview</h1>
            <p>Enter a custom title to dynamically preview the administrative executive summary header.</p>
            <form method="GET" action="/admin_portal">
                <input type="hidden" name="access_key" value="{_CH5_TOKEN}">
                <input type="text" name="title" placeholder="e.g., Weekly Threat Summary" value="{report_title}">
                <button type="submit">Generate Preview</button>
            </form>
            <div class="preview-area">
                <h3>Report Header Output:</h3>
                <div>{report_title}</div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, flag=_CH5_FLAG)


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

