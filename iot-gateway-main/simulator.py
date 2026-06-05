import time
import random
import threading
from pymodbus.datastore import ModbusDeviceContext,ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.server import StartTcpServer


def do_some(context):
    temperature = random.randint(100,800)
    pressure = random.randint(100,800)
    humidity = random.randint(100,800)

    stem = context[0x00]
    stem.setValues(3,0, [temperature,pressure,humidity])
    print(f"[Simulator] Temp: {temperature/10}°C | "
          f"Pressure: {pressure/100} bar | "
          f"Humidity: {humidity/10}%")



def run_simulator():
    block = ModbusSequentialDataBlock(0,[0]*10)
    store = ModbusDeviceContext(hr=block)
    context = ModbusServerContext(devices=store, single=True)

    def keep_updating():
        while True:
            do_some(context)
            time.sleep(2)
        
    thread = threading.Thread(target=keep_updating, daemon=True)
    thread.start()

    print("[Simulator] Starting Modbus TCP server on port 5020...")
    StartTcpServer(context=context, address=("localhost", 5020))

if __name__ == "__main__":
    run_simulator()
        








    