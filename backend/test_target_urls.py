import sys
sys.path.insert(0, 'backend')
from app import app
from database import init_db
from seed import seed_database

def test_target_urls():
    init_db()
    seed_database()

    with app.test_client() as client:
        # Register & Login test user
        res = client.post('/api/auth/register', json={'username': 'urltest', 'email': 'urltest@example.com', 'password': 'Password123!'})
        data = res.get_json()
        if 'token' in data:
            token = data['token']
        else:
            login_res = client.post('/api/auth/login', json={'account': 'urltest', 'password': 'Password123!'})
            token = login_res.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}

        # Fetch first challenge ID
        list_res = client.get('/api/challenges', headers=headers)
        first_id = list_res.get_json()['challenges'][0]['id']

        # 1. Local Request (Host: localhost:5000)
        local_res = client.get(f'/api/challenges/{first_id}', headers=headers)
        assert local_res.status_code == 200
        local_chal = local_res.get_json()['challenge']
        print("[LOCAL DEV CHECK] target_url:", local_chal['target_url'])
        assert 'localhost' in local_chal['target_url']
        print("[PASS] Local development target URL correctly uses localhost!")

        # 2. Production Request (X-Forwarded-Host: cyberquest-backend-ar9r.onrender.com, X-Forwarded-Proto: https)
        prod_headers = {
            'Authorization': f'Bearer {token}',
            'X-Forwarded-Host': 'cyberquest-backend-ar9r.onrender.com',
            'X-Forwarded-Proto': 'https'
        }
        prod_res = client.get(f'/api/challenges/{first_id}', headers=prod_headers)
        assert prod_res.status_code == 200
        prod_chal = prod_res.get_json()['challenge']
        print("[PRODUCTION CHECK] target_url:", prod_chal['target_url'])
        assert prod_chal['target_url'].startswith('https://cyberquest-backend-ar9r.onrender.com')
        print("[PASS] Production target URL correctly uses https://cyberquest-backend-ar9r.onrender.com!")

        # Cleanup
        from database import get_db_connection
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE username = 'urltest'")
        conn.commit()
        conn.close()

        print("\n[SUCCESS] ALL TARGET URL PRODUCTION/LOCAL TESTS PASSED PERFECTLY!")

if __name__ == '__main__':
    test_target_urls()
