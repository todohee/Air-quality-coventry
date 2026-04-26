import asyncio
import json
import time
from typing import Dict
import os
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = "sensors/#"

app = FastAPI(title="Air Quality Backend")

# base directory for resolving static files reliably
base_dir = Path(__file__).resolve().parent
log = logging.getLogger("air-quality")

# control whether the app attempts to connect to MQTT on startup
ENABLE_MQTT = os.getenv("ENABLE_MQTT", "true").lower() in ("1", "true", "yes")

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
    if not ENABLE_MQTT:
        log.info("MQTT startup disabled by ENABLE_MQTT env var")
        return
    loop = asyncio.get_event_loop()
    def _run_mqtt():
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as e:
            log.warning("MQTT connect failed: %s", e)
            return
        mqtt_client.loop_forever()
    loop.run_in_executor(None, _run_mqtt)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/sensors")
async def get_sensors():
    return JSONResponse(content=sensors)

if (base_dir / "static").exists():
    app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    index_path = base_dir / "static" / "index.html"
    if index_path.exists():
        with index_path.open("r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<html><body><h1>Air Quality Backend</h1><p>No UI installed.</p></body></html>")
 