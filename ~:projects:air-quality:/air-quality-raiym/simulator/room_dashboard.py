import json
import threading
import pygame
import paho.mqtt.client as mqtt

# -------------------------------
# Initialize Pygame
# -------------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Room Air Monitor")

# Colors
BG       = (18, 18, 24)
WHITE    = (220, 220, 220)
RED      = (255, 80, 80)
BLUE     = (80, 140, 255)
GREEN    = (80, 220, 120)
ORANGE   = (255, 165, 60)
GRAY     = (60, 60, 70)
DK_GRAY  = (35, 35, 45)

font_big   = pygame.font.SysFont("Arial", 42, bold=True)
font_med   = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 20)

# -------------------------------
# Global sensor data
# -------------------------------
sensor_data = {
    "temperature": None,
    "co2": None,
    "water_quality": None,
    "dust": None,
}
last_seen = "No data yet"

# -------------------------------
# MQTT
# -------------------------------
def on_connect(client, userdata, flags, rc):
    print("MQTT connected, rc=", rc)
    client.subscribe("sensors/#")

def on_message(client, userdata, message):
    global last_seen
    try:
        payload = json.loads(message.payload.decode())
        for key in sensor_data:
            if key in payload:
                sensor_data[key] = payload[key]
        import time
        last_seen = __import__('datetime').datetime.now().strftime("%H:%M:%S")
    except Exception as e:
        print("Parse error:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect("localhost", 1883, 60)
    threading.Thread(target=client.loop_forever, daemon=True).start()
except Exception as e:
    print("MQTT connect failed:", e)

# -------------------------------
# Drawing helpers
# -------------------------------
def get_status(key, value):
    if value is None:
        return "—", GRAY
    if key == "temperature":
        if 18 <= value <= 26: return "GOOD", GREEN
        if value > 30:        return "POOR", RED
        return "MODERATE", ORANGE
    if key == "co2":
        if value <= 800:  return "GOOD", GREEN
        if value <= 1200: return "MODERATE", ORANGE
        return "POOR", RED
    if key == "water_quality":
        if value >= 60:  return "GOOD", GREEN
        if value >= 30:  return "MODERATE", ORANGE
        return "POOR", RED
    if key == "dust":
        if value <= 35:  return "GOOD", GREEN
        if value <= 75:  return "MODERATE", ORANGE
        return "POOR", RED
    return "—", GRAY

def draw_bar(label, key, value, unit, max_val, color, y):
    # Label + value
    text = font_med.render(f"{label}: {f'{value:.1f}' if value is not None else '—'} {unit}", True, WHITE)
    screen.blit(text, (50, y))
    # Background bar
    pygame.draw.rect(screen, GRAY, (50, y + 35, 400, 28), border_radius=6)
    # Filled bar
    if value is not None:
        fill = max(0, min(400, int((value / max_val) * 400)))
        pygame.draw.rect(screen, color, (50, y + 35, fill, 28), border_radius=6)
    # Status badge
    status_text, status_color = get_status(key, value)
    badge = font_small.render(status_text, True, status_color)
    screen.blit(badge, (465, y + 38))

# -------------------------------
# Main loop
# -------------------------------
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Title
    title = font_big.render("Room Air Quality Monitor", True, WHITE)
    screen.blit(title, (50, 25))

    # Last seen
    ls = font_small.render(f"Last update: {last_seen}", True, (130, 130, 150))
    screen.blit(ls, (50, 78))

    # Bars
    t = sensor_data["temperature"]
    draw_bar("Temperature (°C)", "temperature", t,         "°C",    40,    RED,    120)
    draw_bar("CO₂ (ppm)",        "co2",         sensor_data["co2"],          "ppm",   2000,  BLUE,   230)
    draw_bar("Water Quality",    "water_quality",sensor_data["water_quality"],"",     100,   GREEN,  340)
    draw_bar("Dust (µg/m³)",     "dust",        sensor_data["dust"],         "µg/m³", 150,   ORANGE, 450)

    # Overall status circle
    vals = [v for v in sensor_data.values() if v is not None]
    statuses = [get_status(k, v)[0] for k, v in sensor_data.items() if v is not None]
    if "POOR" in statuses:       overall, oc = "POOR",     RED
    elif "MODERATE" in statuses: overall, oc = "MODERATE", ORANGE
    elif statuses:               overall, oc = "GOOD",     GREEN
    else:                        overall, oc = "—",        GRAY

    pygame.draw.circle(screen, DK_GRAY, (670, 270), 100)
    pygame.draw.circle(screen, oc,      (670, 270), 100, 6)
    pygame.draw.line(screen, oc, (630, 270), (710, 270), 4)
    ov_text = font_med.render(overall, True, oc)
    screen.blit(ov_text, (670 - ov_text.get_width() // 2, 330))

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
