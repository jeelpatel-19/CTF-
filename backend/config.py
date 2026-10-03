import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'cyberquest.db')
STATIC_FILES_DIR = os.path.join(BASE_DIR, 'static', 'challenges')

SECRET_KEY = os.environ.get('SECRET_KEY', 'cyberquest-secret-key-prod-2026')
JWT_SECRET = os.environ.get('JWT_SECRET', 'cyberquest-jwt-secret-key-2026')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
