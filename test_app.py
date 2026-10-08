"""Verify real SQLite persistence and the lab's five HTTP endpoints."""
import importlib.util
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path


class UserAPITests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('app'), 'The Flask app must exist')
        from app import create_app
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'test.db'
        self.app = create_app(self.path)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.user = dict(name='John Doe', email='john.doe@example.com',
                         phone='067765434567', address='John Doe Street, Innsbruck',
                         country='Austria')

    def test_crud_persists_then_removes_the_user(self):
        self.assertEqual(self.client.get('/api/users').json, [])
        result = self.client.post('/api/users/add', json=self.user)
        self.assertEqual(result.status_code, 201)
        created = result.json
        self.assertIsInstance(created['user_id'], int)
        self.assertEqual({k: created[k] for k in self.user}, self.user)
        uid = created['user_id']
        self.assertEqual(self.client.get('/api/users').json, [created])
        self.assertEqual(self.client.get(f'/api/users/{uid}').json, created)
        from app import create_app
        self.assertEqual(create_app(self.path).test_client().get('/api/users').json, [created])
        changed = dict(created, phone='031234567', country='Lebanon', address='Beirut')
        result = self.client.put('/api/users/update', json=changed)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, changed)
        with closing(sqlite3.connect(self.path)) as conn:
            self.assertEqual(conn.execute('SELECT country FROM users WHERE user_id = ?', (uid,)).fetchone()[0], 'Lebanon')
        result = self.client.delete(f'/api/users/delete/{uid}')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, {'status': 'User deleted successfully'})
        self.assertEqual(self.client.get('/api/users').json, [])
        self.assertEqual(self.client.get(f'/api/users/{uid}').status_code, 404)

    def test_invalid_input_is_rejected_without_inserting(self):
        for body in ({}, [], dict(self.user, name=''), dict(self.user, phone=123)):
            with self.subTest(body=body):
                self.assertEqual(self.client.post('/api/users/add', json=body).status_code, 400)
        self.assertEqual(self.client.get('/api/users').json, [])

    def test_unknown_users_and_invalid_ids(self):
        self.assertEqual(self.client.get('/api/users/999').status_code, 404)
        self.assertEqual(self.client.delete('/api/users/delete/999').status_code, 404)
        self.assertEqual(self.client.put('/api/users/update', json=dict(self.user, user_id=999)).status_code, 404)
        for uid in (True, 0, '1'):
            self.assertEqual(self.client.put('/api/users/update', json=dict(self.user, user_id=uid)).status_code, 400)

    def test_sql_parameters_preserve_literal_quotes(self):
        body = dict(self.user, name="O'Connor'); DROP TABLE users; --")
        result = self.client.post('/api/users/add', json=body)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(self.client.get('/api/users').json[0]['name'], body['name'])

    def test_json_content_type_and_cors(self):
        self.assertEqual(self.client.post('/api/users/add', data='not JSON').status_code, 415)
        result = self.client.get('/api/users', headers={'Origin': 'http://localhost:3000'})
        self.assertEqual(result.mimetype, 'application/json')
        self.assertEqual(result.headers['Access-Control-Allow-Origin'], 'http://localhost:3000')


if __name__ == '__main__':
    unittest.main(verbosity=2)
