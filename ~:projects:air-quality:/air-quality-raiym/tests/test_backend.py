from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'

def test_sensors_empty():
    r = client.get('/sensors')
    assert r.status_code == 200
    assert isinstance(r.json(), dict)
