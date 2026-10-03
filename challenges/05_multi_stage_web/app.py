import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__, static_folder='static')

# Define flag
FLAG = "CTF{one_layer_was_never_enough}"

# Ensure isolated flag file exists in app directory
FLAG_FILE = os.path.join(os.path.dirname(__file__), 'flag.txt')
with open(FLAG_FILE, 'w', encoding='utf-8') as f:
    f.write(f"{FLAG}\n")

@app.route('/')
def home():
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
        <script src="/static/js/app.js"></script>
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

@app.route('/static/js/app.js')
def static_js():
    js_content = """
/**
 * CyberQuest Staging Application Client Logic
 * Version: 2.4.1-build809
 * 
 * TODO: Remove legacy debug endpoint before production launch!
 * DEBUG ROUTE: /api/v1/debug_status?token=dev_preview_2026
 */
console.log("CyberQuest Developer Client loaded.");
"""
    return js_content, 200, {'Content-Type': 'application/javascript'}

@app.route('/api/v1/debug_status')
def debug_status():
    token = request.args.get('token', '')
    if token != 'dev_preview_2026':
        return jsonify({'error': 'Unauthorized access', 'message': 'Invalid or missing preview token'}), 403
    
    return jsonify({
        'status': 'healthy',
        'environment': 'staging',
        'admin_portal': '/admin_portal',
        'required_key': 'dev_preview_2026',
        'notice': 'Access /admin_portal?access_key=dev_preview_2026 for internal report preview generation.'
    }), 200

@app.route('/admin_portal', methods=['GET', 'POST'])
def admin_portal():
    access_key = request.args.get('access_key') or request.form.get('access_key')
    if access_key != 'dev_preview_2026':
        return """
        <!DOCTYPE html>
        <html>
        <head><title>403 Access Denied</title></head>
        <body style="background:#0b0f19;color:#ef4444;font-family:sans-serif;text-align:center;padding-top:100px;">
            <h1>403 Forbidden: Invalid Access Key</h1>
            <p style="color:#94a3b8;">You must supply a valid `access_key` parameter to access the administrative portal.</p>
        </body>
        </html>
        """, 403

    report_title = request.values.get('title', 'Default Security Summary')
    
    # Intentionally vulnerable template rendering for report title
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
                <input type="hidden" name="access_key" value="dev_preview_2026">
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
    return render_template_string(template, flag=FLAG)

if __name__ == '__main__':
    print("Starting Isolated Vulnerable Web Application on http://localhost:5005")
    app.run(host='0.0.0.0', port=5005, debug=False)
