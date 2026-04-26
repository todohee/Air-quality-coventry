#!/usr/bin/env python3
import argparse
import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt

MQTT_PORT = 1883

def generate_reading(state, mode):
    if mode == 'random':
        temperature = round(random.uniform(18, 30), 1)
        co2 = int(random.uniform(400, 2000))
        water_quality = int(random.uniform(0, 100))
        dust = int(random.uniform(0, 150))
    else:
        co2 = state.get('co2', 600)
        temp = state.get('temperature', 22)
        if mode == 'classroom':
            temp_delta = round(random.uniform(0.1, 0.4), 1)
            co2 += random.randint(5, 30)
            dust_delta = random.randint(2, 8)
            wq_delta = random.randint(-3, 0)
            temp_min, temp_max = 18, 30
        elif mode == 'office':
            temp_delta = round(random.uniform(0.0, 0.2), 1)
            co2 += random.randint(2, 15)
            dust_delta = random.randint(0, 4)
            wq_delta = random.randint(-1, 1)
            temp_min, temp_max = 18, 26
        elif mode == 'ventilated':
            temp_delta = round(random.uniform(-0.3, -0.05), 1)
            co2 -= random.randint(50, 200)
            dust_delta = random.randint(-10, -2)
            wq_delta = random.randint(1, 4)
            temp_min, temp_max = 18, 24
        else:
            temp_delta = round(random.uniform(-0.1, 0.1), 1)
            co2 += random.randint(-10, 20)
            dust_delta = random.randint(-2, 3)
            wq_delta = random.randint(-1, 1)
            temp_min, temp_max = 18, 28
        temperature = round(max(temp_min, min(temp_max, temp + temp_delta)), 1)
        co2 = int(max(400, min(2000, co2)))
        dust = int(max(0, min(150, state.get('dust', 30) + dust_delta)))
        water_quality = int(max(0, min(100, state.get('water_quality', 70) + wq_delta)))
    return {'temperature': temperature, 'co2': co2, 'water_quality': water_quality, 'dust': dust, 'ts': time.time()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensor-id', default='sensor-1')
    parser.add_argument('--mode', choices=['random', 'classroom', 'office', 'ventilated'], default='random')
    parser.add_argument('--interval', type=float, default=5.0)
    parser.add_argument('--broker', default='mosquitto')
    args = parser.parse_args()

    client = mqtt.Client()
    try:
        client.connect(args.broker, MQTT_PORT, 60)
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
            'water_quality': reading['water_quality'],
            'dust': reading['dust'],
            'timestamp': reading['ts']
        }
        client.publish(topic, json.dumps(payload))
        print(f'[{datetime.now().isoformat()}] {payload}')
        time.sleep(args.interval)

if __name__ == '__main__':
    main()