import sqlite3
import os
from config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Challenges Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            points INTEGER NOT NULL,
            flag TEXT NOT NULL,
            target_url TEXT,
            file_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Hints Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            hint_text TEXT NOT NULL,
            penalty INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE
        )
    ''')

    # User Hints (Unlocked hints)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_hints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            hint_id INTEGER NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (hint_id) REFERENCES hints (id) ON DELETE CASCADE,
            UNIQUE(user_id, hint_id)
        )
    ''')

    # Solves Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            points_earned INTEGER NOT NULL,
            time_taken_seconds INTEGER,
            solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE,
            UNIQUE(user_id, challenge_id)
        )
    ''')

    # Migration: Add time_taken_seconds to solves if missing
    cursor.execute("PRAGMA table_info(solves)")
    solves_columns = [col['name'] for col in cursor.fetchall()]
    if 'time_taken_seconds' not in solves_columns:
        cursor.execute("ALTER TABLE solves ADD COLUMN time_taken_seconds INTEGER")

    # Challenge Starts Table (Server-side challenge start time tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenge_starts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE,
            UNIQUE(user_id, challenge_id)
        )
    ''')

    # Submissions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            submitted_flag TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
