"""Run against a live API: python smoke_test.py http://localhost:8080."""
import json
import sys
from urllib.request import Request, urlopen

base = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8080').rstrip('/')


def call(path, method='GET', body=None):
    data = None if body is None else json.dumps(body).encode()
    request = Request(base + path, data=data, method=method, headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=10) as response:
        content = response.read()
        return response.status, json.loads(content) if content else None


assert call('/ready') == (200, {'status': 'ready'})
status, task = call('/tasks', 'POST', {'title': 'Automated smoke test'})
assert status == 201
path = f"/tasks/{task['id']}"
try:
    assert call(path)[1]['title'] == 'Automated smoke test'
    assert call(path, 'PATCH', {'status': 'done'})[1]['status'] == 'done'
    assert any(item['id'] == task['id'] for item in call('/tasks')[1])
finally:
    assert call(path, 'DELETE')[0] == 204
print(f'PASS: readiness and create/read/update/list/delete at {base}')
