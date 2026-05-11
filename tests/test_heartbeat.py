from fastapi.testclient import TestClient
from services.heartbeat_listener import app

client = TestClient(app)

def test_heartbeat_valid_payload():
    """Prueba que el endpoint reciba payloads válidos y responda 200."""
    payload = {
        "source": "systemd",
        "event_type": "service_failure",
        "message": "tesis-backend failed to start",
        "severity": "critical"
    }
    response = client.post("/heartbeat", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "accepted", "message": "Heartbeat encolado para el Cerebro Técnico"}

def test_heartbeat_missing_source():
    """Prueba que se rechacen requests incompletos."""
    payload = {
        "event_type": "service_failure",
        "message": "tesis-backend failed to start",
        "severity": "critical"
    }
    # fastapi levanta 422 Unprocessable Entity si falta un campo del modelo
    response = client.post("/heartbeat", json=payload)
    assert response.status_code == 422
