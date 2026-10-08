"""SQLite operations for the Lab 5 user management app."""
import sqlite3
from contextlib import closing
from pathlib import Path

DATABASE = Path(__file__).resolve().with_name('database.db')


def connect_to_db(database=DATABASE):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def create_db_table(database=DATABASE):
    with closing(connect_to_db(database)) as conn, conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            country TEXT NOT NULL
        )''')


def insert_user(user, database=DATABASE):
    with closing(connect_to_db(database)) as conn, conn:
        cur = conn.execute(
            'INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)',
            (user['name'], user['email'], user['phone'], user['address'], user['country']))
        row = conn.execute('SELECT * FROM users WHERE user_id = ?', (cur.lastrowid,)).fetchone()
        return dict(row)


def get_users(database=DATABASE):
    with closing(connect_to_db(database)) as conn:
        return [dict(row) for row in conn.execute('SELECT * FROM users ORDER BY user_id')]


def get_user_by_id(user_id, database=DATABASE):
    with closing(connect_to_db(database)) as conn:
        row = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        return dict(row) if row else {}


def update_user(user, database=DATABASE):
    with closing(connect_to_db(database)) as conn, conn:
        conn.execute('''UPDATE users SET name = ?, email = ?, phone = ?,
            address = ?, country = ? WHERE user_id = ?''',
            (user['name'], user['email'], user['phone'], user['address'], user['country'], user['user_id']))
        row = conn.execute('SELECT * FROM users WHERE user_id = ?', (user['user_id'],)).fetchone()
        return dict(row) if row else {}


def delete_user(user_id, database=DATABASE):
    with closing(connect_to_db(database)) as conn, conn:
        cur = conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        return {'status': 'User deleted successfully'} if cur.rowcount else {}


if __name__ == '__main__':
    create_db_table()
    print(f'User table ready in {DATABASE}')
