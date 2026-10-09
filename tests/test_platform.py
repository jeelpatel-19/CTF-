import unittest
import os
import sys
import json
import base64
import struct

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

from app import app
from database import init_db, get_db_connection
from seed import generate_challenge_files, seed_database
from config import STATIC_FILES_DIR

class TestCyberQuestPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        generate_challenge_files()
        seed_database()
        cls.client = app.test_client()
        app.testing = True

        # Authenticate as admin first — /api/challenges requires a valid token
        admin_login = cls.client.post('/api/auth/login', json={'account': 'admin', 'password': 'AdminPass123!'})
        cls.admin_token = json.loads(admin_login.data)['token']
        cls.admin_headers = {'Authorization': f'Bearer {cls.admin_token}'}

        # Fetch actual dynamic challenge IDs from API
        res = cls.client.get('/api/challenges', headers=cls.admin_headers)
        cls.challenges = json.loads(res.data)['challenges']
        cls.ch_map = {c['title']: c['id'] for c in cls.challenges}


    def test_01_health_check(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'healthy')

    def test_02_empty_leaderboard_initially(self):
        # Admin clears all player users to start fresh test
        admin_login = self.client.post('/api/auth/login', json={'account': 'admin', 'password': 'AdminPass123!'})
        admin_token = json.loads(admin_login.data)['token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        self.client.delete('/api/admin/users/clear-players', headers=admin_headers)

        # Verify public leaderboard is completely empty (no dummy users)
        lb_res = self.client.get('/api/leaderboard', headers=admin_headers)
        self.assertEqual(lb_res.status_code, 200)
        lb_data = json.loads(lb_res.data)['leaderboard']
        self.assertEqual(len(lb_data), 0)

    def test_03_real_player_flow_and_leaderboard(self):
        # Register a real test player
        reg_res = self.client.post('/api/auth/register', json={
            'username': 'real_player_one',
            'email': 'real_player_one@cyberquest.local',
            'password': 'PlayerPassword123!'
        })
        self.assertEqual(reg_res.status_code, 201)
        user_info = json.loads(reg_res.data)['user']
        token = json.loads(reg_res.data)['token']
        headers = {'Authorization': f'Bearer {token}'}

        # 1. Initial score must be 0
        self.assertEqual(user_info['points'], 0)

        # 2. Leaderboard shows new player with 0 points
        lb_res = self.client.get('/api/leaderboard', headers=headers)
        self.assertEqual(lb_res.status_code, 200)
        lb_data = json.loads(lb_res.data)['leaderboard']
        self.assertEqual(len(lb_data), 1)
        self.assertEqual(lb_data[0]['username'], 'real_player_one')
        self.assertEqual(lb_data[0]['points'], 0)

        # 3. Solve Challenge 1
        ch1_id = self.ch_map['THE FORGOTTEN HEADER']
        sub_res = self.client.post(f'/api/challenges/{ch1_id}/submit', headers=headers, json={'flag': 'CTF{header_was_never_empty}'})
        self.assertEqual(sub_res.status_code, 200)
        self.assertTrue(json.loads(sub_res.data)['success'])

        # 4. Verify points updated to 100 on leaderboard
        lb_res_after = self.client.get('/api/leaderboard', headers=headers)
        lb_data_after = json.loads(lb_res_after.data)['leaderboard']
        self.assertEqual(lb_data_after[0]['points'], 100)
        self.assertEqual(lb_data_after[0]['solves_count'], 1)

    def test_04_challenge_1_forgotten_header(self):
        res = self.client.get('/api/challenges/target/forgotten-header')
        self.assertEqual(res.status_code, 200)
        header_val = res.headers.get('X-Secret-Flag')
        self.assertEqual(header_val, 'CTF{header_was_never_empty}')
        self.assertNotIn(b'CTF{header_was_never_empty}', res.data)

    def test_05_challenge_2_silent_image(self):
        res = self.client.get('/static/challenges/silent_image.jpg')
        self.assertEqual(res.status_code, 200)
        content = res.data
        self.assertIn(b'CTF{metadata_speaks}', content)

    def test_06_challenge_3_broken_access(self):
        res_101 = self.client.get('/api/challenges/target/room?user_id=101')
        self.assertEqual(res_101.status_code, 200)
        self.assertNotIn(b'CTF{numbers_are_not_permissions}', res_101.data)

        res_102 = self.client.get('/api/challenges/target/room?user_id=102')
        self.assertEqual(res_102.status_code, 200)
        self.assertIn(b'CTF{numbers_are_not_permissions}', res_102.data)

    def test_07_challenge_4_hidden_parameter(self):
        res_normal = self.client.get('/api/challenges/target/hidden-param')
        self.assertEqual(res_normal.status_code, 200)
        self.assertNotIn(b'CTF{the_parameter_was_always_there}', res_normal.data)

        res_debug = self.client.get('/api/challenges/target/hidden-param?debug=true')
        self.assertEqual(res_debug.status_code, 200)
        self.assertIn(b'CTF{the_parameter_was_always_there}', res_debug.data)

    def test_08_challenge_5_the_last_layer(self):
        """Full multi-stage walkthrough for Challenge 5 — The Last Layer."""

        # ── Stage 1: Download the artifact file ──────────────────────────────
        res_file = self.client.get('/static/challenges/last_layer.txt')
        self.assertEqual(res_file.status_code, 200)
        content = res_file.data.decode('utf-8')
        self.assertIn('CYBERQUEST RECOVERY ARTIFACT', content)

        # Decode the Base64 Layer 1 payload from the artifact
        import base64, re
        # Require at least one letter in the match to avoid the ===... separator line
        b64_match = re.search(r'([A-Za-z][A-Za-z0-9+/=]{19,})', content)
        self.assertIsNotNone(b64_match, "No Base64 payload found in last_layer.txt")
        decoded = base64.b64decode(b64_match.group(1)).decode('utf-8')
        # Must NOT point at the old standalone server
        self.assertNotIn('localhost:5005', decoded, "Clue still references localhost:5005!")
        self.assertIn('/api/challenges/target/last-layer-hub', decoded)

        # ── Stage 2: Developer hub landing page ──────────────────────────────
        res_hub = self.client.get('/api/challenges/target/last-layer-hub')
        self.assertEqual(res_hub.status_code, 200)
        self.assertIn(b'CyberQuest Internal Developer Hub', res_hub.data)
        self.assertIn(b'app.js', res_hub.data)

        # ── Stage 3: JavaScript file exposes the hidden debug route ──────────
        res_js = self.client.get('/api/challenges/target/last-layer-hub/static/js/app.js')
        self.assertEqual(res_js.status_code, 200)
        self.assertIn(b'DEBUG ROUTE', res_js.data)
        self.assertIn(b'/api/v1/debug_status?token=dev_preview_2026', res_js.data)

        # ── Stage 4a: Debug endpoint — invalid token returns 403 ─────────────
        res_debug_bad = self.client.get('/api/challenges/api/v1/debug_status?token=wrong')
        self.assertEqual(res_debug_bad.status_code, 403)

        # ── Stage 4b: Debug endpoint — correct token reveals admin_portal ────
        res_debug_ok = self.client.get(
            '/api/challenges/api/v1/debug_status?token=dev_preview_2026'
        )
        self.assertEqual(res_debug_ok.status_code, 200)
        debug_data = res_debug_ok.get_json()
        self.assertEqual(debug_data.get('status'), 'healthy')
        self.assertIn('admin_portal', debug_data)
        self.assertIn('dev_preview_2026', debug_data.get('notice', ''))

        # ── Stage 5a: Admin portal — missing access key returns 403 ──────────
        res_portal_bad = self.client.get('/api/challenges/admin_portal')
        self.assertEqual(res_portal_bad.status_code, 403)

        # ── Stage 5b: Admin portal — valid access key shows the form ─────────
        res_portal_ok = self.client.get(
            '/api/challenges/admin_portal?access_key=dev_preview_2026'
        )
        self.assertEqual(res_portal_ok.status_code, 200)
        self.assertIn(b'Internal Admin Report Preview', res_portal_ok.data)
        self.assertIn(b'Default Security Summary', res_portal_ok.data)

        # ── Stage 6a: SSTI proof — {{ 7 * 7 }} renders 49 ───────────────────
        res_ssti_math = self.client.get(
            '/api/challenges/admin_portal?access_key=dev_preview_2026&title=%7B%7B+7+*+7+%7D%7D'
        )
        self.assertEqual(res_ssti_math.status_code, 200)
        self.assertIn(b'49', res_ssti_math.data)

        # ── Stage 6b: {{ flag }} exfiltrates the real flag ───────────────────
        res_ssti_flag = self.client.get(
            '/api/challenges/admin_portal?access_key=dev_preview_2026&title=%7B%7B+flag+%7D%7D'
        )
        self.assertEqual(res_ssti_flag.status_code, 200)
        self.assertIn(b'CTF{one_layer_was_never_enough}', res_ssti_flag.data)

    def test_09_admin_user_management(self):
        admin_login = self.client.post('/api/auth/login', json={'account': 'admin', 'password': 'AdminPass123!'})
        self.assertEqual(admin_login.status_code, 200)
        admin_token = json.loads(admin_login.data)['token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        # Register temp user
        temp_reg = self.client.post('/api/auth/register', json={
            'username': 'user_to_delete',
            'email': 'user_to_delete@cyberquest.local',
            'password': 'Password123!'
        })
        self.assertEqual(temp_reg.status_code, 201)
        temp_user_id = json.loads(temp_reg.data)['user']['id']

        # Delete temp user
        del_res = self.client.delete(f'/api/admin/users/{temp_user_id}', headers=admin_headers)
        self.assertEqual(del_res.status_code, 200)

        # Login deleted user fails
        login_deleted = self.client.post('/api/auth/login', json={'account': 'user_to_delete', 'password': 'Password123!'})
        self.assertEqual(login_deleted.status_code, 401)

        # Clear all players
        clear_res = self.client.delete('/api/admin/users/clear-players', headers=admin_headers)
        self.assertEqual(clear_res.status_code, 200)

        # Leaderboard is 0 players
        lb_res = self.client.get('/api/leaderboard', headers=admin_headers)
        lb_data = json.loads(lb_res.data)['leaderboard']
        self.assertEqual(len(lb_data), 0)

        # Admin login preserved
        admin_relogin = self.client.post('/api/auth/login', json={'account': 'admin', 'password': 'AdminPass123!'})
        self.assertEqual(admin_relogin.status_code, 200)

if __name__ == '__main__':
    unittest.main()
