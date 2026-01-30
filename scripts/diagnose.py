import serial
import time
import glob
import sys

def find_at_port():
    ports = glob.glob('/dev/ttyUSB*')
    for port in ports:
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            ser.write(b"AT\r\n")
            if b"OK" in ser.read(100): return port
            ser.close()
        except: pass
    return None

def send_at(ser, cmd):
    print(f"CMD: {cmd}")
    ser.write((cmd + "\r\n").encode())
    time.sleep(1)
    resp = ser.read(ser.in_waiting).decode(errors='ignore')
    print(f"RES: {resp.strip()}")
    return resp

try:
    port = find_at_port()
    if not port:
        print("No AT port found.")
        sys.exit(1)
        
    ser = serial.Serial(port, 115200, timeout=2)
    print("=== Power Saving Status Report ===")
    send_at(ser, "ATE0")
    send_at(ser, "AT+QSCLK?")  # Sleep control
    send_at(ser, "AT+CPSMS?")  # PSM setting
    send_at(ser, "AT+CEDRXS?") # eDRX setting
    send_at(ser, "AT+QPSMEXT?") # Quectel PSM extended
    send_at(ser, "AT+QPSMS?")   # Quectel PSM 
    ser.close()
    
except Exception as e:
    print(f"Error: {e}")
