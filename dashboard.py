import csv
import os
from datetime import datetime
from flask import Flask, render_template_string
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import pandas as pd
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# ─── Thresholds ──────────────────────────────────────────
THRESHOLDS = {
    "temperature": 70.0,   # °C
    "pressure":    4.0,    # bar
    "humidity":    80.0    # %
}

LOG_FILE = "logs/sensor_log.csv"

# ─── Latest values stored in memory ──────────────────────
latest = {
    "temperature": 0.0,
    "pressure":    0.0,
    "humidity":    0.0
}
# ─────────────────────────────────────────────────────────


# ─── HTML Dashboard Page ──────────────────────────────────
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT Gateway Dashboard</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1a1a2e;
            color: white;
            text-align: center;
            padding: 40px;
        }
        h1 { color: #00d4ff; margin-bottom: 40px; }
        .cards {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }
        .card {
            background: #16213e;
            border-radius: 16px;
            padding: 30px 40px;
            min-width: 200px;
            border: 2px solid #0f3460;
            transition: border 0.3s;
        }
        .card.danger { border: 2px solid #ff4444; }
        .label { font-size: 14px; color: #aaa; margin-bottom: 10px; }
        .value { font-size: 48px; font-weight: bold; color: #00d4ff; }
        .value.danger { color: #ff4444; }
        .unit  { font-size: 16px; color: #aaa; margin-top: 6px; }
        .status {
            margin-top: 40px;
            font-size: 13px;
            color: #555;
        }
    </style>
</head>
<body>
    <h1>Industrial IoT Gateway — Live Dashboard</h1>
    <div class="cards">
        <div class="card" id="card-temp">
            <div class="label">Temperature</div>
            <div class="value" id="temp">--</div>
            <div class="unit">°C</div>
        </div>
        <div class="card" id="card-pressure">
            <div class="label">Pressure</div>
            <div class="value" id="pressure">--</div>
            <div class="unit">bar</div>
        </div>
        <div class="card" id="card-humidity">
            <div class="label">Humidity</div>
            <div class="value" id="humidity">--</div>
            <div class="unit">%</div>
        </div>
    </div>
    <div class="status" id="status">Waiting for data...</div>

    <script>
        var socket = io();
        socket.on('sensor_update', function(data) {
            document.getElementById('temp').innerText     = data.temperature;
            document.getElementById('pressure').innerText = data.pressure;
            document.getElementById('humidity').innerText = data.humidity;
            document.getElementById('status').innerText   = 'Last update: ' + data.timestamp;

            // Temperature alert
            toggleDanger('card-temp',      'temp',     data.temperature, {{ thresholds.temperature }});
            toggleDanger('card-pressure',  'pressure', data.pressure,    {{ thresholds.pressure }});
            toggleDanger('card-humidity',  'humidity', data.humidity,    {{ thresholds.humidity }});
        });

        function toggleDanger(cardId, valueId, value, threshold) {
            var card  = document.getElementById(cardId);
            var val   = document.getElementById(valueId);
            if (value >= threshold) {
                card.classList.add('danger');
                val.classList.add('danger');
            } else {
                card.classList.remove('danger');
                val.classList.remove('danger');
            }
        }
    </script>
</body>
</html>
"""


# ─── CSV Logging ──────────────────────────────────────────
def log_to_csv(temperature, pressure, humidity):
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "temperature", "pressure", "humidity"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": temperature,
            "pressure":    pressure,
            "humidity":    humidity
        })


# ─── MQTT Callbacks ───────────────────────────────────────
def on_message(client, userdata, message):
    topic = message.topic
    value = float(message.payload.decode())

    if "temperature" in topic:
        latest["temperature"] = value
    elif "pressure" in topic:
        latest["pressure"] = value
    elif "humidity" in topic:
        latest["humidity"] = value

    # Once all three values received emit to dashboard
    if all(latest.values()):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_to_csv(latest["temperature"],
                   latest["pressure"],
                   latest["humidity"])

        socketio.emit("sensor_update", {
            "temperature": round(latest["temperature"], 1),
            "pressure":    round(latest["pressure"],    2),
            "humidity":    round(latest["humidity"],    1),
            "timestamp":   timestamp
        })


def start_mqtt_listener():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe("factory/sensors/#")
    client.loop_forever()


# ─── Flask Route ──────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML, thresholds=THRESHOLDS)


# ─── Main ─────────────────────────────────────────────────
if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=start_mqtt_listener, daemon=True)
    mqtt_thread.start()
    print("[Dashboard] Running at http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000)