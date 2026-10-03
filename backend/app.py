import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from config import SECRET_KEY, STATIC_FILES_DIR
from database import init_db
from seed import seed_database, generate_challenge_files

from routes.auth import auth_bp
from routes.challenges import challenges_bp
from routes.hints import hints_bp
from routes.user import user_bp
from routes.leaderboard import leaderboard_bp
from routes.admin import admin_bp

app = Flask(__name__, static_folder=STATIC_FILES_DIR)
app.config['SECRET_KEY'] = SECRET_KEY

# Enable CORS for frontend cross-origin requests
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register API blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(challenges_bp, url_prefix='/api/challenges')
app.register_blueprint(hints_bp, url_prefix='/api/hints')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Static file downloads for challenge resources
@app.route('/static/challenges/<path:filename>')
def serve_challenge_file(filename):
    return send_from_directory(STATIC_FILES_DIR, filename, as_attachment=True)

# Health Check Route
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'CyberQuest API', 'version': '1.0.0'})

if __name__ == '__main__':
    # Initialize DB & Seed files automatically on startup if needed
    init_db()
    generate_challenge_files()
    seed_database()
    
    print("Starting CyberQuest Flask Backend Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
