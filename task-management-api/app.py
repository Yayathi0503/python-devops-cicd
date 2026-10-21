import os
import sqlite3
import time
from pathlib import Path

from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(DATABASE=os.environ.get('DATABASE_PATH', 'data/tasks.db'), MAX_CONTENT_LENGTH=16384)
    app.config.update(config or {})
    registry = CollectorRegistry()
    requests_total = Counter('task_api_requests_total', 'HTTP responses', ['method', 'route', 'status'], registry=registry)
    request_seconds = Histogram('task_api_request_seconds', 'Request duration', ['route'], registry=registry)

    @app.before_request
    def begin_request():
        g.started_at = time.perf_counter()

    @app.after_request
    def record_request(response):
        if request.path != '/metrics':
            route = request.url_rule.rule if request.url_rule else 'unmatched'
            requests_total.labels(request.method, route, str(response.status_code)).inc()
            request_seconds.labels(route).observe(time.perf_counter() - g.started_at)
        return response

    @app.get('/metrics')
    def metrics():
        return app.response_class(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'], timeout=10)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        connection = g.pop('db', None)
        if connection is not None:
            connection.close()

    with app.app_context():
        db().execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'todo',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        db().commit()

    def find(task_id):
        from flask import abort
        row = db().execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if row is None:
            abort(404, description='Task not found')
        return dict(row)

    def validate(partial=False):
        from flask import abort
        data = request.get_json()
        if not isinstance(data, dict) or not data:
            abort(400, description='Provide a non-empty JSON object')
        if set(data) - {'title', 'description', 'status'}:
            abort(400, description='Unknown task field')
        if not partial and 'title' not in data:
            abort(400, description='title is required')
        if 'title' in data:
            if not isinstance(data['title'], str) or not 1 <= len(data['title'].strip()) <= 200:
                abort(400, description='title must contain 1 to 200 characters')
            data['title'] = data['title'].strip()
        if 'description' in data and (not isinstance(data['description'], str) or len(data['description']) > 2000):
            abort(400, description='description must be text of at most 2000 characters')
        if 'status' in data and data['status'] not in ('todo', 'in_progress', 'done'):
            abort(400, description='status must be todo, in_progress, or done')
        return data

    @app.errorhandler(HTTPException)
    def error_response(error):
        return jsonify(error=error.description), error.code

    @app.get('/')
    def index():
        return jsonify(project='Task Management API', endpoints=['/health', '/ready', '/tasks'])

    @app.get('/health')
    def health():
        return jsonify(status='ok')

    @app.get('/ready')
    def ready():
        db().execute('SELECT 1 FROM tasks LIMIT 1')
        return jsonify(status='ready')

    @app.get('/tasks')
    def list_tasks():
        return jsonify([dict(row) for row in db().execute('SELECT * FROM tasks ORDER BY id')])

    @app.post('/tasks')
    def create_task():
        data = validate()
        cursor = db().execute('INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)',
                              (data['title'], data.get('description', ''), data.get('status', 'todo')))
        db().commit()
        return jsonify(find(cursor.lastrowid)), 201, {'Location': f'/tasks/{cursor.lastrowid}'}

    @app.get('/tasks/<int:task_id>')
    def get_task(task_id):
        return jsonify(find(task_id))

    @app.patch('/tasks/<int:task_id>')
    def update_task(task_id):
        task = find(task_id)
        task.update(validate(partial=True))
        db().execute('UPDATE tasks SET title=?, description=?, status=? WHERE id=?',
                     (task['title'], task['description'], task['status'], task_id))
        db().commit()
        return jsonify(find(task_id))

    @app.delete('/tasks/<int:task_id>')
    def delete_task(task_id):
        find(task_id)
        db().execute('DELETE FROM tasks WHERE id=?', (task_id,))
        db().commit()
        return '', 204

    return app
