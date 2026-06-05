import socket
import struct
import paho.mqtt.client as mqtt

SOCKET_PATH = "/tmp/can_bus.sock"
MQTT_HOST   = "localhost"
MQTT_PORT   = 1883

CAN_FRAME_FORMAT = "HBB8s"  
CAN_FRAME_SIZE   = struct.calcsize(CAN_FRAME_FORMAT)

CAN_ID_ENGINE    = 0x100   
CAN_ID_BODY      = 0x200
CAN_ID_DASHBOARD = 0x300   

def parse_value(data):
    return ((data[0] << 8) | data[1])

def start_can_reader():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        import os
        os.unlink(SOCKET_PATH)
    except FileNotFoundError:
        pass
    sock.bind(SOCKET_PATH)

    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_start()

    print("[CAN Reader] Listening for CAN frames...")

    while True:
        raw = sock.recv(1024)
        if len(raw) < CAN_FRAME_SIZE:
            continue

        id_, dlc, _, data = struct.unpack(CAN_FRAME_FORMAT, raw[:CAN_FRAME_SIZE])
        raw_val = parse_value(data)

        if id_ == CAN_ID_ENGINE:
            temp = raw_val / 10.0
            client.publish("factory/sensors/temperature", temp)
            print(f"[CAN Reader] Temp: {temp} C")

        elif id_ == CAN_ID_BODY:
            humidity = raw_val / 10.0
            client.publish("factory/sensors/humidity", humidity)
            print(f"[CAN Reader] Humidity: {humidity}%")

        elif id_ == CAN_ID_DASHBOARD:
            pressure = raw_val / 100.0
            client.publish("factory/sensors/pressure", pressure)
            print(f"[CAN Reader] Pressure: {pressure} bar")

if __name__ == "__main__":
    start_can_reader()