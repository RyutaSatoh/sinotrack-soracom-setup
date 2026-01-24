# Sinotrack SORACOM Setup Tool

This tool fixes connectivity issues for Sinotrack LTE trackers (specifically those using the **EG915U** chipset) when using **SORACOM** or other data-only SIMs in Japan (or countries without 2G/3G fallback).

## The Problem

Many Sinotrack LTE devices (like ST-901L) shipped with the **Quectel EG915U-LA** module are configured to attempt a "Combined Attach" (Voice + Data) or fallback to 3G/GSM. 

In environments like Japan where:
1.  3G networks are retired (SoftBank 3G ended in 2024).
2.  SIM cards (like SORACOM Plan01s) are Data-only (PS only).

The network rejects the connection request (`+CEER: 5,33 Requested service option not subscribed`), causing the device to stay offline (blinking orange LED forever) and unable to receive SMS commands.

## The Solution

This script connects to the tracker's modem via USB serial port and performs the following:
1.  **Sets LTE Only Mode**: Prevents the modem from scanning for non-existent 2G/3G networks.
2.  **Configures APN Directly**: Writes `soracom.io` and authentication details directly to the modem's non-volatile memory, bypassing the need for SMS configuration.
3.  **Forces Reboot & Re-connection**: Restarts the modem and monitors the connection status until it successfully registers to the network (Roaming or Home).

## Usage

### Prerequisites
*   A Linux machine (Raspberry Pi, PC, etc.)
*   The Sinotrack device connected via USB (MicroUSB port on the PCB or external USB-TTL adapter).
*   Python 3 installed.
*   `pyserial` library (`pip install pyserial`).

### Steps
1.  Connect the device to your computer.
2.  Identify the serial port (e.g., `/dev/ttyUSB2` or `/dev/ttyUSB5`). The script attempts to auto-detect.
3.  Run the script:

```bash
sudo python3 setup_sinotrack_soracom.py
```

4.  Wait for the script to finish. It will display `Success! Network Registered` and the acquired IP address.

## Supported Devices

*   Sinotrack ST-901L (LTE version)
*   Any tracker using **Quectel EG915U** series modules.

## License

MIT
