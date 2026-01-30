import serial
import time
import glob
import sys

def find_at_port():
    print("Scanning for AT command port...")
    ports = glob.glob('/dev/ttyUSB*')
    
    if not ports:
        print("No /dev/ttyUSB* ports found.")
        return None

    for port in ports:
        print(f"Trying {port}...", end="", flush=True)
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            ser.flushInput()
            ser.write(b"AT\r\n")
            time.sleep(0.5)
            resp = ser.read(ser.in_waiting).decode(errors='ignore')
            ser.close()
            
            if "OK" in resp:
                print(" OK!")
                return port
            else:
                print(" No response.")
        except:
            print(" Error opening.")
            
    print("Could not find a valid AT port.")
    return None

def send_at(ser, cmd, wait=1):
    print(f"[Send] {cmd}")
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    resp = ser.read(ser.in_waiting).decode(errors='ignore')
    print(f"[Recv] {resp.strip()}")
    return resp

def setup_modem():
    port = find_at_port()
    if not port:
        sys.exit(1)

    print(f"--- Connecting to {port} ---")
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        
        # 1. Basic Setup
        send_at(ser, 'ATE0')
        
        # 2. LTE Only Mode
        print("\n--- Setting LTE Only Mode ---")
        send_at(ser, 'AT+QCFG="nwscanmode",3')
        
        # 3. Disable Sleep (Force Stay Awake)
        # QSCLK=0: Disable sleep mode completely
        print("\n--- Disabling Modem Sleep ---")
        send_at(ser, 'AT+QSCLK=0')
        
        # 4. APN Setup
        print("\n--- Setting APN (SORACOM) ---")
        send_at(ser, 'AT+CGDCONT=1,"IP","soracom.io"')
        send_at(ser, 'AT+QICSGP=1,1,"soracom.io","sora","sora",3')
        
        # 5. Save and Reboot
        print("\n--- Saving & Rebooting ---")
        send_at(ser, 'AT&W')
        ser.write(b'AT+CFUN=1,1\r\n')
        
        print("Reboot command sent. Please wait for the device to restart.")
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_modem()
