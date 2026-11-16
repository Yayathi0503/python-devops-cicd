"""Smoke-test the built image on an ephemeral loopback port; retain failure logs."""
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.ci'
CID = STATE / 'container.id'


def docker(*args, **kwargs):
    return subprocess.run(['docker', *args], check=True, text=True, **kwargs)


def cleanup():
    if CID.exists():
        container = CID.read_text().strip()
        if container:
            # Only remove this build's recorded container, never other jobs' resources.
            result = subprocess.run(['docker', 'rm', '-f', container], text=True,
                                    capture_output=True)
            if result.returncode and 'No such container' not in result.stderr:
                raise RuntimeError(result.stderr.strip())
        CID.unlink()


def smoke():
    STATE.mkdir(exist_ok=True)
    cleanup()
    image = (STATE / 'image.id').read_text().strip()
    try:
        docker('run', '--detach', '--cidfile', str(CID),
               '--publish', '127.0.0.1::8080', image)
        container = CID.read_text().strip()
        info = json.loads(docker('inspect', container, capture_output=True).stdout)[0]
        port = info['NetworkSettings']['Ports']['8080/tcp'][0]['HostPort']
        base = f'http://127.0.0.1:{port}'
        deadline = time.monotonic() + 60
        while True:
            try:
                with urlopen(base + '/ready', timeout=2) as response:
                    if response.status == 200:
                        break
            except (URLError, TimeoutError, ConnectionError):
                pass
            if time.monotonic() >= deadline:
                raise RuntimeError('Container did not become ready within 60 seconds')
            time.sleep(1)
        subprocess.run([sys.executable, str(ROOT / 'task-management-api' / 'smoke_test.py'),
                        base], check=True)
    finally:
        if CID.exists() and CID.read_text().strip():
            result = subprocess.run(['docker', 'logs', CID.read_text().strip()],
                                    text=True, capture_output=True)
            (STATE / 'container.log').write_text(result.stdout + result.stderr,
                                                  encoding='utf-8')
        cleanup()


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('smoke', 'cleanup'):
        raise SystemExit('Usage: python scripts/jenkins_container.py smoke|cleanup')
    smoke() if sys.argv[1] == 'smoke' else cleanup()
