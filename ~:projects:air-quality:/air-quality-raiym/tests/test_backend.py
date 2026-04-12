from fastapi.testclient import TestClient
from unittest.mock import patch
import time

from backend.app.main import app, sensors, on_message

client = TestClient(app)


# original tests

def test_health():
    """Health endpoint returns 200 and status ok."""
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'

def test_sensors_empty():
    """Sensors endpoint returns an empty dict when no data has been received."""
    sensors.clear()
    r = client.get('/sensors')
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


# MQTT message handling tests

def test_on_message_stores_sensor_data():
    """
    Simulates a valid MQTT message arriving on sensors/temperature and verifies
    that on_message correctly parses the JSON payload and stores it under the
    sensor ID extracted from the topic.
    """
    sensors.clear()

    # Build a fake MQTT message object
    class FakeMsg:
        topic = "sensors/temperature"
        payload = b'{"temperature": 22.5, "humidity": 45}'

    on_message(None, None, FakeMsg())

    assert "temperature" in sensors
    assert sensors["temperature"]["temperature"] == 22.5
    assert sensors["temperature"]["humidity"] == 45


def test_on_message_appends_last_seen_timestamp():
    """
    Verifies that on_message adds a last_seen Unix timestamp to every stored
    sensor reading, enabling the dashboard to display when data was last updated.
    """
    sensors.clear()

    class FakeMsg:
        topic = "sensors/co2"
        payload = b'{"co2": 800}'

    before = time.time()
    on_message(None, None, FakeMsg())
    after = time.time()

    assert "last_seen" in sensors["co2"]
    assert before <= sensors["co2"]["last_seen"] <= after


def test_on_message_invalid_json_does_not_crash():
    """
    Verifies that on_message handles malformed payloads gracefully without
    raising an exception or corrupting the sensor store.
    """
    sensors.clear()

    class FakeMsg:
        topic = "sensors/fire"
        payload = b'not valid json'

    try:
        on_message(None, None, FakeMsg())
    except Exception as e:
        assert False, f"on_message raised an exception on bad payload: {e}"

    # store should remain empty, bad message must not be stored
    assert "fire" not in sensors


def test_on_message_missing_sensor_id_falls_back_to_unknown():
    """
    Verifies that if the MQTT topic has no second segment (e.g. just 'sensors'),
    the reading is stored under the key 'unknown' rather than crashing.
    """
    sensors.clear()

    class FakeMsg:
        topic = "sensors"
        payload = b'{"temperature": 19.0}'

    on_message(None, None, FakeMsg())

    assert "unknown" in sensors


def test_sensors_endpoint_returns_stored_data():
    """
    Integration test: injects sensor data directly into the in-memory store and
    confirms the /sensors endpoint returns it correctly, verifying that the
    backend correctly exposes MQTT-received data to the frontend dashboard.
    """
    sensors.clear()
    sensors["water"] = {"water_quality": "good", "last_seen": time.time()}

    r = client.get('/sensors')
    assert r.status_code == 200
    data = r.json()
    assert "water" in data
    assert data["water"]["water_quality"] == "good"


def test_sensors_endpoint_reflects_multiple_sensors():
    """
    Verifies that when multiple sensors have published data, the /sensors
    endpoint returns all of them, confirming the wildcard sensors/# subscription
    correctly aggregates readings from different sensor types.
    """
    sensors.clear()
    sensors["temperature"] = {"temperature": 21.0, "last_seen": time.time()}
    sensors["co2"]         = {"co2": 650,          "last_seen": time.time()}
    sensors["dust"]        = {"dust": 12.3,         "last_seen": time.time()}

    r = client.get('/sensors')
    data = r.json()

    assert "temperature" in data
    assert "co2" in data
    assert "dust" in data


def test_on_message_overwrites_stale_sensor_data():
    """
    Verifies that when a sensor publishes a new reading, the updated value
    replaces the previous one in the store rather than accumulating duplicates.
    """
    sensors.clear()

    class FakeMsg1:
        topic = "sensors/temperature"
        payload = b'{"temperature": 20.0}'

    class FakeMsg2:
        topic = "sensors/temperature"
        payload = b'{"temperature": 25.0}'

    on_message(None, None, FakeMsg1())
    on_message(None, None, FakeMsg2())

    assert sensors["temperature"]["temperature"] == 25.0
    assert len([k for k in sensors if k == "temperature"]) == 1
