# Sinotrack SORACOM Setup Tool

This toolset helps to connect Sinotrack LTE trackers (EG915U chipset) to SORACOM (Japan/Global) and configure them for Traccar.

## Supported Devices
*   Sinotrack ST-901L (LTE)
*   Devices using **Quectel EG915U** module

## Scripts

All scripts are located in the `scripts/` directory.

### 1. `connect.py` (Essential)
Restores network connectivity by forcing "LTE Only" mode and setting the correct APN.
Use this when the device LED is blinking orange (offline) or after a power loss.

```bash
sudo python3 scripts/connect.py
```

### 2. `config_interval.py`
Sets the reporting interval (ACC ON/OFF) via SORACOM API.
Requires `AUTH_KEY` and `IMSI` configuration inside the script.

```bash
sudo python3 scripts/config_interval.py
```

### 3. `diagnose.py`
Checks the modem status (Signal, Network Registration, Error codes).

```bash
sudo python3 scripts/diagnose.py
```

### 4. `test_send.py`
Forces the modem to send a test packet to the Traccar server directly via TCP.
Useful for debugging network paths.

```bash
sudo python3 scripts/test_send.py
```

## Requirements
*   Python 3
*   `pyserial`
*   `requests`

## License
MIT