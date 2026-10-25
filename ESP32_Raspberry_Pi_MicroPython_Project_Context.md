# ESP32 + Raspberry Pi 5 + MicroPython

## Project goal

Use a Raspberry Pi 5 as an IoT development workstation to program an ESP32 with MicroPython. The long-term goals are to learn GPIO, sensors, LEDs, Wi-Fi, Bluetooth, and IoT communication, then integrate the ESP32 with Python APIs and an AI assistant.

## Hardware

### Raspberry Pi 5

- OS: Debian GNU/Linux 13 (Trixie), 64-bit
- Architecture: `aarch64`
- Storage: 128 GB microSD card
- Root filesystem: approximately 117 GB total, with approximately 105 GB available at last check

### ESP32

- Chip: `ESP32-D0WD-V3`
- Revision: v3.1
- CPU: dual-core, 240 MHz
- Connectivity: Wi-Fi and Bluetooth
- Flash: 4 MB
- Crystal: 40 MHz
- USB-to-serial adapter: Silicon Labs CP210x UART Bridge
- USB VID:PID: `10c4:ea60`
- Serial device: `/dev/ttyUSB0` (verify if it changes)
- MAC address reported by esptool: `20:9b:a9:70:4a:f4`

The ESP32 is connected to the Raspberry Pi via USB.

## Development environment

A Python virtual environment exists at:

```bash
~/Projects/iot-tools/.venv
```

Activate it with:

```bash
cd ~/Projects/iot-tools
source .venv/bin/activate
```

Firmware directory:

```bash
~/Projects/iot-tools/firmware
```

Tools verified on the Raspberry Pi:

- Python 3.13.5
- Git 2.47.3
- SQLite 3.46.1
- pip 26.2.2
- Thonny
- Geany
- Nano
- Minicom 2.10
- esptool 5.6.0
- pyserial (installed; exact version not recorded)
- `mpremote` was installed or is the next tool to verify with `mpremote --version`

## What has been completed

1. Detected the CP210x USB-to-serial adapter with `lsusb`.
2. Confirmed the ESP32 appears at `/dev/ttyUSB0`.
3. Identified the chip and flash using esptool.
4. Confirmed that `--no-stub flash-id` can read flash information.
5. Learned that `--no-stub erase-flash` fails with `ESP32 ROM does not support function erase_flash`.
6. Used the normal stub flasher successfully to erase the flash.
7. Wrote the MicroPython firmware to address `0x1000`.
8. Confirmed esptool reported `Hash of data verified`.
9. Successfully ran Python commands on the ESP32 REPL.

### Firmware details

- Firmware family: `ESP32_GENERIC`
- Version confirmed at runtime: MicroPython v1.29.0
- Build date shown by the device: 2026-08-24
- Expected local file: `ESP32_GENERIC-20260824-v1.29.0.bin`
- Expected location: `~/Projects/iot-tools/firmware/`
- Reported file size: approximately 1.8 MB
- Official firmware page: https://micropython.org/download/ESP32_GENERIC/

The device reported:

```python
import sys
print(sys.implementation)
# (name='micropython', version=(1, 29, 0, ''), _machine='Generic ESP32 module with ESP32', _mpy=11014, _build='ESP32_GENERIC', _thread='GIL')

print(sys.version)
# 3.4.0; MicroPython v1.29.0 on 2026-08-24

print("Hello from MicroPython on ESP32!")
# Hello from MicroPython on ESP32!
```

**Current confirmed state:** MicroPython is installed and working on the ESP32. Firmware erase and flashing are complete. No LED or sensor program has been completed yet.

## Useful commands

### Activate the environment

```bash
cd ~/Projects/iot-tools
source .venv/bin/activate
```

### Check the connected ESP32 and flash

```bash
python -m esptool --chip esp32 --port /dev/ttyUSB0 --no-stub flash-id
```

### Check chip communication

```bash
python -m esptool --chip esp32 --port /dev/ttyUSB0 chip-id
```

The normal stub flasher worked for `chip-id` and `erase-flash`. Do not add `--no-stub` to erase or write commands on this setup unless there is a specific reason.

### Connect to the MicroPython REPL

```bash
mpremote connect /dev/ttyUSB0
```

At the `>>>` prompt:

```python
import sys
print(sys.implementation)
print(sys.version)
print("Hello from MicroPython on ESP32!")
```

Exit mpremote with `Ctrl+]`.

### Install or verify mpremote

```bash
python -m pip install mpremote
mpremote --version
```

## Important safety notes

- `erase-flash` removes existing firmware and files stored in the ESP32 flash. Do not run it unless replacing those contents is intended.
- Prefer read-only diagnostics before any destructive operation.
- If serial communication fails, check that the device is still `/dev/ttyUSB0` and that no other application is using it.
- If the normal stub flasher fails to connect, capture the complete error before trying repeated flash operations.
- Use firmware intended for the generic ESP32 target and confirm the actual downloaded filename before writing it.
- The verified write command used address `0x1000` and baud rate `115200`.

## Next steps

1. Verify mpremote is installed with `mpremote --version`.
2. Identify whether the development board has a built-in LED. If using an external LED, use an appropriate current-limiting resistor and confirm the GPIO pinout for the exact board.
3. Write and run a minimal GPIO LED blink program.
4. Save a working program as `main.py` on the ESP32 so it runs on startup.
5. Read a sensor.
6. Connect the ESP32 to Wi-Fi.
7. Send data from the ESP32 to the Raspberry Pi.
8. Add MQTT/Mosquitto when useful.
9. Explore integration with a Python API or AI assistant.

## Working approach

Continue from the confirmed state above. Do not repeat the initial hardware setup or reinstall tools already verified. Use the existing virtual environment and serial port unless diagnostics show they have changed. Take small, verifiable steps and explain commands briefly before asking the user to run them.
