import os
import struct
import time
import base64
from werkzeug.security import generate_password_hash
from database import init_db, get_db_connection
from config import STATIC_FILES_DIR
from PIL import Image, ImageDraw

CHALLENGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'challenges'))

def generate_challenge_files():
    os.makedirs(STATIC_FILES_DIR, exist_ok=True)

    # 1. Challenge 02 — The Silent Image (silent_image.jpg)
    img_static_path = os.path.join(STATIC_FILES_DIR, 'silent_image.jpg')
    img = Image.new('RGB', (600, 350), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([20, 20, 580, 330], outline=(16, 185, 129), width=3)
    draw.text((40, 40), "CYBERQUEST FORENSIC REPOSITORY #9042", fill=(16, 185, 129))
    draw.text((40, 80), "Status: Unmodified Media File", fill=(148, 163, 184))
    draw.text((40, 120), "Suspect: Unknown", fill=(148, 163, 184))
    
    img.save(img_static_path, "JPEG", quality=90)

    # Inject EXIF COM (comment) marker containing flag
    with open(img_static_path, 'rb') as f:
        content = f.read()
    
    exif_comment = b"EXIF UserComment: CTF{metadata_speaks}"
    com_len = len(exif_comment) + 2
    com_marker = b'\xff\xfe' + struct.pack('>H', com_len) + exif_comment

    if content.startswith(b'\xff\xd8'):
        new_content = content[:2] + com_marker + content[2:]
        with open(img_static_path, 'wb') as f:
            f.write(new_content)
            
    ch2_dir = os.path.join(CHALLENGES_DIR, '02_silent_image')
    os.makedirs(ch2_dir, exist_ok=True)
    with open(os.path.join(ch2_dir, 'silent_image.jpg'), 'wb') as f:
        with open(img_static_path, 'rb') as orig_f:
            f.write(orig_f.read())
    print(f"Generated Challenge 2 resource: {img_static_path}")

    # 2. Challenge 05 — The Last Layer (last_layer.txt)
    # Layer 1 Base64 payload points to Challenge 5 debug endpoint
    layer1_b64 = base64.b64encode(b"http://localhost:5005/api/v1/debug_status?token=dev_preview_2026").decode('utf-8')
    ch5_content = f"""CYBERQUEST RECOVERY ARTIFACT #7701
===================================
TRANSMISSION DATA LAYER 1:

{layer1_b64}
"""
    last_layer_path = os.path.join(STATIC_FILES_DIR, 'last_layer.txt')
    with open(last_layer_path, 'w', encoding='utf-8') as f:
        f.write(ch5_content)

    ch5_dir = os.path.join(CHALLENGES_DIR, '05_the_last_layer')
    os.makedirs(ch5_dir, exist_ok=True)
    with open(os.path.join(ch5_dir, 'last_layer.txt'), 'w', encoding='utf-8') as f:
        f.write(ch5_content)
    print(f"Generated Challenge 5 resource: {last_layer_path}")


def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Seed Default Admin User
    admin_email = 'admin@cyberquest.local'
    existing_admin = cursor.execute('SELECT id FROM users WHERE email = ?', (admin_email,)).fetchone()
    if not existing_admin:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, points)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', admin_email, generate_password_hash('AdminPass123!'), 'admin', 0))
        print("Created default admin user (admin / AdminPass123!)")

    # Re-seed exact 5 challenges
    cursor.execute('DELETE FROM hints')
    cursor.execute('DELETE FROM challenges')
    
    challenges = [
        {
            'title': 'THE FORGOTTEN HEADER',
            'category': 'Web Security',
            'difficulty': 'Easy',
            'points': 100,
            'description': 'The server gives you everything you need, but not in the page.\n\nSomething important is travelling with every response.\n\nFind the hidden value and submit the flag.',
            'learning_objective': 'Learn how to inspect HTTP response headers using browser Developer Tools or cURL.',
            'flag': 'CTF{header_was_never_empty}',
            'target_url': 'http://localhost:5000/api/challenges/target/forgotten-header',
            'file_url': None,
            'hints': [
                {'hint_text': 'A browser receives more than what your eyes can see.', 'penalty': 15}
            ]
        },
        {
            'title': 'THE SILENT IMAGE',
            'category': 'Forensics',
            'difficulty': 'Easy',
            'points': 150,
            'description': 'Everyone sees the same picture.\n\nBut the picture remembers something that the viewer does not.\n\nFind what was left behind.',
            'learning_objective': 'Examine file properties and embedded metadata attributes in downloaded media files.',
            'flag': 'CTF{metadata_speaks}',
            'target_url': None,
            'file_url': '/static/challenges/silent_image.jpg',
            'hints': [
                {'hint_text': "Pictures have memories too. Some memories aren't visible.", 'penalty': 25}
            ]
        },
        {
            'title': 'BROKEN ACCESS',
            'category': 'Web Security',
            'difficulty': 'Hard',
            'points': 200,
            'description': 'You are allowed to see your own room.\n\nBut the door accepts a number instead of a key.\n\nHow far does that number take you?',
            'learning_objective': 'Understand broken access control and identifier-based authorization flaws.',
            'flag': 'CTF{numbers_are_not_permissions}',
            'target_url': 'http://localhost:5000/api/challenges/target/room?user_id=101',
            'file_url': None,
            'hints': [
                {'hint_text': 'If changing one small thing changes who you are looking at, ask who is actually checking the lock.', 'penalty': 30}
            ]
        },
        {
            'title': 'THE HIDDEN PARAMETER',
            'category': 'Web Security',
            'difficulty': 'Hard',
            'points': 250,
            'description': 'The page tells you almost nothing.\n\nPerhaps it was never designed to tell everyone everything.',
            'learning_objective': 'Discover unlinked application parameters through reconnaissance and source code analysis.',
            'flag': 'CTF{the_parameter_was_always_there}',
            'target_url': 'http://localhost:5000/api/challenges/target/hidden-param',
            'file_url': None,
            'hints': [
                {'hint_text': 'Developers sometimes leave doors for themselves. The door may not have a handle.', 'penalty': 40}
            ]
        },
        {
            'title': 'THE LAST LAYER',
            'category': 'Web Security',
            'difficulty': 'Hard',
            'points': 300,
            'description': "One layer gives you a clue.\n\nThe clue gives you another layer.\n\nStop when you think you've reached the end—but ask yourself why it was called the last layer.",
            'learning_objective': 'Execute a multi-stage security assessment combining file analysis, API discovery, and template injection.',
            'flag': 'CTF{one_layer_was_never_enough}',
            'target_url': 'http://localhost:5005',
            'file_url': '/static/challenges/last_layer.txt',
            'hints': [
                {'hint_text': "When something looks meaningless, don't immediately assume it is encrypted. Sometimes the first lock is only there to hide the second.", 'penalty': 50}
            ]
        }
    ]

    for c in challenges:
        cursor.execute('''
            INSERT INTO challenges (title, description, category, difficulty, points, flag, target_url, file_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (c['title'], c['description'], c['category'], c['difficulty'], c['points'], c['flag'], c['target_url'], c['file_url']))
        
        c_id = cursor.lastrowid
        for h in c['hints']:
            cursor.execute('''
                INSERT INTO hints (challenge_id, hint_text, penalty)
                VALUES (?, ?, ?)
            ''', (c_id, h['hint_text'], h['penalty']))
        print(f"Seeded challenge: {c['title']} ({c['points']} pts)")

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == '__main__':
    generate_challenge_files()
    seed_database()
