"""The five Flask REST endpoints specified in Lab 5."""
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import database as db

FIELDS = ('name', 'email', 'phone', 'address', 'country')


def create_app(database_path=db.DATABASE):
    app = Flask(__name__)
    app.config['DATABASE'] = str(database_path)
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    db.create_db_table(database_path)

    def read_user(require_id=False):
        user = request.get_json()
        if not isinstance(user, dict):
            return None, (jsonify(error='The JSON body must be an object'), 400)
        if any(not isinstance(user.get(key), str) or not user[key].strip() for key in FIELDS):
            return None, (jsonify(error='name, email, phone, address and country must be nonempty strings'), 400)
        if require_id and (type(user.get('user_id')) is not int or user['user_id'] <= 0):
            return None, (jsonify(error='user_id must be a positive integer'), 400)
        return user, None

    @app.get('/api/users')
    def api_get_users():
        return jsonify(db.get_users(app.config['DATABASE']))

    @app.get('/api/users/<int:user_id>')
    def api_get_user(user_id):
        user = db.get_user_by_id(user_id, app.config['DATABASE'])
        return jsonify(user) if user else (jsonify(error='User not found'), 404)

    @app.post('/api/users/add')
    def api_add_user():
        user, error = read_user()
        if error is not None:
            return error
        return jsonify(db.insert_user(user, app.config['DATABASE'])), 201

    @app.put('/api/users/update')
    def api_update_user():
        user, error = read_user(require_id=True)
        if error is not None:
            return error
        updated = db.update_user(user, app.config['DATABASE'])
        return jsonify(updated) if updated else (jsonify(error='User not found'), 404)

    @app.delete('/api/users/delete/<int:user_id>')
    def api_delete_user(user_id):
        result = db.delete_user(user_id, app.config['DATABASE'])
        return jsonify(result) if result else (jsonify(error='User not found'), 404)

    @app.errorhandler(HTTPException)
    def json_http_error(error):
        return jsonify(error=error.description), error.code

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000, debug=False)
