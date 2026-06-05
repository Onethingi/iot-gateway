import time
from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt
from opcua import Server

MODBUS_HOST = "localhost"
MODBUS_PORT = 5020

MQTT_HOST = "localhost"
MQTT_PORT = 1883

POLL_INTERVAL = 2

def setup_mqtt():
    client = mqtt.Client()
    client.connect(MQTT_HOST,MQTT_PORT)
    client.loop_start()
    return client

def setup_opcua():
    server = Server()
    server.set_endpoint("opc.tcp://localhost:4840")
    server.set_server_name("IoT")
    register = server.register_namespace("IoT Gateway")
    objects = server.get_objects_node()
    sensors = objects.add_object(register,"Sensors")

    temp_node = sensors.add_variable(register, "Temperature",0.0)
    pressure_node = sensors.add_variable(register, "Pressure",0.0)
    humidity_node = sensors.add_variable(register, "Humidity",0.0)
    temp_node.set_writable()
    pressure_node.set_writable()
    humidity_node.set_writable()
    server.start()
    return server, temp_node,pressure_node,humidity_node

def read_modbus(mody):
    results  = mody.read_holding_registers(0, count=3)
    if results.isError():
        return None
    
    raw = results.registers
    Temperature = raw[0]/10.0
    Pressure = raw[1]/100.0
    Humidity = raw[2]/10.0

    return Temperature,Pressure,Humidity

def publish_mqtt(set_mod,Temperature,Pressure,Humidity):
    set_mod.publish("factory/sensors/temperature", Temperature)
    set_mod.publish("factory/sensors/pressure", Pressure)
    set_mod.publish("factory/sensors/humidity", Humidity)

def update_opc(temp_node,pressure_node,humidity_node,Temperature,Pressure,Humidity):
    temp_node.set_value(Temperature)
    pressure_node.set_value(Pressure)
    humidity_node.set_value(Humidity)


def run_sim():
    modbus_cl = ModbusTcpClient(MODBUS_HOST,port=MODBUS_PORT)
    modbus_cl.connect()

    set_mod = setup_mqtt()

    server,temp_node,pressure_node,humidity_node = setup_opcua()

    try:
        while True:
            data = read_modbus(modbus_cl)
            if data :
                Temperature,Pressure,Humidity = data
                publish_mqtt(set_mod,Temperature,Pressure,Humidity)
                update_opc(temp_node,pressure_node,humidity_node,Temperature,Pressure,Humidity)
                time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        server.stop
        set_mod.loop_stop()
        modbus_cl.close()


if __name__ == "__main__":
    run_sim()









