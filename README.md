# Industrial IoT Gateway & Live Monitoring System

A complete IIoT pipeline simulating a real factory floor  from PLC sensor data collection 
to live web dashboard monitoring using Modbus TCP, MQTT, and OPC UA protocols.

## Tech Stack
Python, Modbus TCP, FreeRTOS (CAN Bus), MQTT, OPC UA, Flask, SocketIO, pymodbus, paho-mqtt, pandas, Mosquitto

## What It Does
- Simulates a PLC generating live sensor data (temperature, pressure, humidity) via Modbus TCP.
- A CAN Bus network is simulated in C using FreeRTOS, where 3 virtual car computer nodes (Engine, Body Control, and Dashboard) each run     as independent tasks and send sensor data at different intervals — just like real automotive hardware.
- Gateway reads from both Modbus and CAN and translates to MQTT (cloud) and OPC UA (SCADA).
- Live web dashboard displays real-time readings with automatic red alerts on threshold breach.
- Logs every reading to a CSV file with timestamps for historical analysis.

## Dashboard Preview
![Dashboard](dashboard.png)

## MQTT Live Feed
![MQTT](mqtt.png)


## Features
- Dual protocol support  Modbus TCP and CAN Bus.
- FreeRTOS-based CAN simulation running 3 concurrent ECU tasks on PC (no hardware needed).
- Real-time MQTT publishing and OPC UA updates on every sensor read.
- Live web dashboard with auto red alerts on threshold breach.
- CSV data logging with timestamps.
- Easily extendable swap simulator for real PLC or CAN hardware.

## How to Run

**Install dependencies:**
```bash
pip install pymodbus paho-mqtt opcua flask flask-socketio pandas cryptography
```

**Open 3 terminals and run in order:**
```bash
# Terminal 1
python simulator.py

# Terminal 2
python gateway.py

# Terminal 3
python dashboard.py
```

**Then open browser at:**
http://localhost:5000


