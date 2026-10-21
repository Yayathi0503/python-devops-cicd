import pytest
from app import create_app


@pytest.fixture
def client(tmp_path):
    return create_app({'TESTING': True, 'DATABASE': str(tmp_path / 'tasks.db')}).test_client()


def test_lifecycle(client):
    assert client.get('/health').json == {'status': 'ok'}
    assert client.get('/ready').status_code == 200
    response = client.post('/tasks', json={'title': ' Learn Docker '})
    assert response.status_code == 201
    path = response.headers['Location']
    assert client.get(path).json['title'] == 'Learn Docker'
    assert len(client.get('/tasks').json) == 1
    assert client.patch(path, json={'status': 'done'}).json['status'] == 'done'
    assert client.delete(path).status_code == 204
    assert client.get(path).status_code == 404
    assert client.get('/tasks').json == []


@pytest.mark.parametrize('payload', [{}, [], {'title': ''}, {'title': 1}, {'title': 'x', 'status': []},
    {'title': 'x', 'status': 'invalid'}, {'title': 'x', 'unknown': 1}, {'title': 'x'*201},
    {'title': 'x', 'description': None}])
def test_invalid_input(client, payload):
    assert client.post('/tasks', json=payload).status_code == 400
    assert client.get('/tasks').json == []


def test_bad_json_and_content_type(client):
    assert client.post('/tasks', data='{', content_type='application/json').status_code == 400
    assert client.post('/tasks', data='hello').status_code == 415


def test_missing_and_invalid_update(client):
    assert client.patch('/tasks/999', json={'status': 'done'}).status_code == 404
    assert client.delete('/tasks/999').status_code == 404
    path = client.post('/tasks', json={'title': 'Original'}).headers['Location']
    assert client.patch(path, json={'title': ''}).status_code == 400
    assert client.get(path).json['title'] == 'Original'


def test_data_survives_restart(tmp_path):
    config = {'TESTING': True, 'DATABASE': str(tmp_path / 'persistent.db')}
    create_app(config).test_client().post('/tasks', json={'title': "SQL quote ' is safe"})
    assert create_app(config).test_client().get('/tasks').json[0]['title'] == "SQL quote ' is safe"


def test_metrics(client):
    client.get('/health')
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'task_api_requests_total{method="GET",route="/health",status="200"} 1.0' in response.data
