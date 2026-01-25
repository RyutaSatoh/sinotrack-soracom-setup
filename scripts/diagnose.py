import serial
import time

def send_at(ser, cmd, wait=1):
    print(f"CMD: {cmd}")
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    resp = ser.read(ser.in_waiting).decode(errors='ignore')
    print(f"RES: {resp.strip()}")
    return resp

try:
    ser = serial.Serial('/dev/ttyUSB5', 115200, timeout=2)
    ser.flushInput()
    
    print("=== Sinotrack Internal Status Report ===")
    
    # 1. Basic HW Check
    send_at(ser, "AT+CPIN?")
    send_at(ser, "AT+CSQ")
    
    # 2. Network Status
    send_at(ser, "AT+CEREG?")
    send_at(ser, "AT+COPS?")
    
    # 3. Connection Settings (Did they persist?)
    # Scan Mode (Should be 3 for LTE Only)
    send_at(ser, 'AT+QCFG="nwscanmode"')
    # APN (Should be soracom.io)
    send_at(ser, "AT+CGDCONT?")
    
    # 4. Error Detail (If registration failed)
    send_at(ser, "AT+CEER")

    ser.close()
    
except Exception as e:
    print(f"Error: {e}")
