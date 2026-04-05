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

