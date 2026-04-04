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
