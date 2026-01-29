#!/usr/bin/env bash
set -e
PROJECT_DIR="$(pwd)"
echo "Creating scaffold in $PROJECT_DIR"

# README
cat > README.md <<'README'
# Air Quality Monitoring — Student Project Scaffold

This repository is a starter scaffold for an air-quality monitoring project that uses software-based sensor simulation and MQTT.

Quick start
1. Start Mosquitto (Docker Compose):
   docker compose up -d

2. Create a Python virtual environment and install backend dependencies:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt

3. Run the backend:
   cd backend
   uvicorn app.main:app --reload --port 8000

4. Run simulator(s):
   python3 simulator/simulator.py --sensor-id sensor-1 --mode classroom --interval 2

5. Open the dashboard in your browser:
   http://localhost:8000/

README
# docker-compose and mosquitto config
cat > docker-compose.yml <<'DC'
version: '3.8'
services:
  mosquitto:
    image: eclipse-mosquitto:2.0
    ports:
      - '1883:1883'
      - '9001:9001'
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log
DC

mkdir -p mosquitto/config mosquitto/data mosquitto/log
cat > mosquitto/config/mosquitto.conf <<'MC'
listener 1883
allow_anonymous true

listener 9001
protocol websockets
allow_anonymous true
MC

# backend
mkdir -p backend/app/backend_static backend/app/static
cat > backend/requirements.txt <<'REQ'
fastapi==0.95.2
uvicorn[standard]==0.22.0
paho-mqtt==1.6.1
requests==2.31.0
pytest==7.4.0
REQ

cat > backend/app/main.py <<'PY'
import asyncio
import json
import time
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC = "sensors/#"

app = FastAPI(title="Air Quality Backend")

# in-memory store
sensors: Dict[str, Dict] = {}

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("MQTT connected with result code", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except Exception:
        print("Invalid payload", msg.payload)
        return
    topic_parts = msg.topic.split("/")
    sensor_id = topic_parts[1] if len(topic_parts) > 1 else "unknown"
    payload["last_seen"] = time.time()
    sensors[sensor_id] = payload

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    def _run_mqtt():
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as e:
            print("MQTT connect failed:", e)
            return
        mqtt_client.loop_forever()
    loop.run_in_executor(None, _run_mqtt)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/sensors")
async def get_sensors():
    return JSONResponse(content=sensors)

app.mount("/static", StaticFiles(directory="./static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    with open("./static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
PY

cat > backend/app/static/index.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Air Quality Dashboard</title>
  <style>
    body { font-family: system-ui, -apple-system, Roboto, Arial; padding: 20px }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f4f4f4; text-align: left }
  </style>
</head>
<body>
  <h1>Air Quality — Live</h1>
  <p>Data is simulated and sent via MQTT by simulator programs.</p>
  <table id="tbl">
    <thead>
      <tr><th>Sensor ID</th><th>Temperature (°C)</th><th>CO₂ (ppm)</th><th>Humidity (%)</th><th>Last seen</th></tr>
    </thead>
    <tbody></tbody>
  </table>

  <script>
    async function fetchAndRender(){
      try {
        const res = await fetch('/sensors');
        const data = await res.json();
        const tbody = document.querySelector('#tbl tbody');
        tbody.innerHTML = '';
        Object.keys(data).forEach(id => {
          const row = data[id];
          const tr = document.createElement('tr');
          const temp = row.temperature ?? '-';
          const co2 = row.co2 ?? '-';
          const hum = row.humidity ?? '-';
          const last = row.last_seen ? new Date(row.last_seen * 1000).toLocaleTimeString() : '-';
          tr.innerHTML = `<td>${id}</td><td>${temp}</td><td>${co2}</td><td>${hum}</td><td>${last}</td>`;
          tbody.appendChild(tr);
        })
      } catch (e){
        console.error(e);
      }
    }
    fetchAndRender();
    setInterval(fetchAndRender, 2000);
  </script>
</body>
</html>
HTML

# simulator
mkdir -p simulator
cat > simulator/simulator.py <<'SIM'
#!/usr/bin/env python3
import argparse
import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def generate_reading(state, mode):
    if mode == 'random':
        temperature = round(random.uniform(18, 30), 1)
        co2 = int(random.uniform(400, 2000))
        humidity = int(random.uniform(30, 80))
    else:
        temperature = round(state.get('temperature', 22) + random.uniform(-0.2, 0.3), 1)
        temperature = max(18, min(30, temperature))
        co2 = state.get('co2', 600)
        if mode == 'classroom':
            co2 += random.randint(5, 30)
        elif mode == 'office':
            co2 += random.randint(2, 15)
        elif mode == 'ventilated':
            co2 -= random.randint(50, 200)
        else:
            co2 += random.randint(-10, 20)
        co2 = int(max(400, min(2000, co2)))
        humidity = int(max(30, min(80, state.get('humidity', 45) + random.randint(-1, 2))))
    return {'temperature': temperature, 'co2': co2, 'humidity': humidity, 'ts': time.time()}

def main():
    parser = argparse.ArgumentParser(description='Simulate environmental sensor publishing to MQTT')
    parser.add_argument('--sensor-id', default='sensor-1')
    parser.add_argument('--mode', choices=['random','classroom','office','ventilated'], default='random')
    parser.add_argument('--interval', type=float, default=5.0)
    args = parser.parse_args()

    client = mqtt.Client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print('Failed to connect to MQTT broker:', e)
        return

    state = {}
    topic = f'sensors/{args.sensor_id}'
    print(f'Publishing to {topic} every {args.interval}s (mode={args.mode})')
    while True:
        reading = generate_reading(state, args.mode)
        state.update(reading)
        payload = {
            'temperature': reading['temperature'],
            'co2': reading['co2'],
            'humidity': reading['humidity'],
            'timestamp': reading['ts']
        }
        client.publish(topic, json.dumps(payload))
        print(f'[{datetime.now().isoformat()}] {payload}')
        time.sleep(args.interval)

if __name__ == '__main__':
    main()
SIM
chmod +x simulator/simulator.py

# tests
mkdir -p tests
cat > tests/test_backend.py <<'TST'
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
TST

# .gitignore and LICENSE
cat > .gitignore <<'GI'
.venv/
__pycache__/
*.pyc
.env
node_modules/
.DS_Store
GI

cat > LICENSE <<'L'
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
L

echo "Scaffold created in $PROJECT_DIR"
ls -la
