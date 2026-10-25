# ESP32 IoT Project — Learning Notes & Checkpoint

> Purpose: A quick restart point for the next session. This document records the working setup, what has been learned, how to resume safely, and the next small tasks.

## 1. Project overview

I am developing IoT projects on a Raspberry Pi 5 using an ESP32 development board and MicroPython.

The first project is controlling the ESP32's onboard blue LED from Python. The LED is connected to **GPIO 2** on this board and can be switched on and off. A `main.py` file was uploaded to the ESP32 so the program runs automatically at startup.

## 2. Hardware and environment

- **Host computer:** Raspberry Pi 5
- **OS:** Debian 13, 64-bit (Raspberry Pi OS)
- **Microcontroller:** ESP32-D0WD-V3, revision 3.1
- **CPU:** Dual-core, up to 240 MHz
- **Flash:** 4 MB
- **USB serial adapter:** Silicon Labs CP210x / CP2102
- **Serial device:** `/dev/ttyUSB0`
- **MicroPython firmware:** `ESP32_GENERIC`, v1.29.0
- **Python on Raspberry Pi:** 3.13.5
- **Git:** 2.47.3
- **esptool:** 5.6.0
- **mpremote environment:** `~/Projects/iot-tools/.venv`
- **Firmware directory:** `~/Projects/iot-tools/firmware`
- **Project directory:** `~/Projects/iot`

Activate the existing Python virtual environment before using `mpremote`:

```bash
source ~/Projects/iot-tools/.venv/bin/activate
```

## 3. What is working

- The ESP32 is detected at `/dev/ttyUSB0`.
- The CP2102 USB-to-UART bridge is recognized by Linux.
- MicroPython v1.29.0 is installed and working.
- The ESP32 REPL has successfully executed Python commands.
- The onboard blue LED works when controlled through GPIO 2:
  - `led.value(1)` turns it on.
  - `led.value(0)` turns it off.
- A blinking program has been saved as `main.py` on the Raspberry Pi and uploaded to the ESP32.
- The ESP32 has been unplugged and reconnected, and the LED began blinking automatically. This confirms startup execution works.
- The project is being edited with `vi`, not `nano`.

**Do not re-erase or reflash the ESP32 as a routine step.** Firmware installation is complete. Only consider firmware recovery if troubleshooting clearly shows it is necessary. Warn before any destructive action and ask for confirmation.

## 4. Important concepts learned

### MicroPython REPL

REPL means Read-Evaluate-Print Loop. It is the interactive prompt where Python commands can be sent directly to the ESP32.

Example:

```python
print("Hello from ESP32!")
```

### GPIO output

GPIO stands for General-Purpose Input/Output. A GPIO pin can be configured as an output to control a component such as an LED.

```python
from machine import Pin

led = Pin(2, Pin.OUT)
led.value(1)  # Set GPIO 2 HIGH; onboard LED turns on on this board.
led.value(0)  # Set GPIO 2 LOW; onboard LED turns off on this board.
```

`Pin.OUT` configures the pin as an output. The `1` and `0` values represent HIGH and LOW. The observed LED behavior confirms that this board's onboard LED is active-high on GPIO 2.

### Timing and loops

```python
from time import sleep

while True:
    led.value(1)
    sleep(1)
    led.value(0)
    sleep(1)
```

- `while True` repeats indefinitely.
- `sleep(1)` pauses for one second.
- Changing the delay to `sleep(0.5)` makes each on/off interval shorter.
- Press **Ctrl+C** in an active REPL to interrupt a running Python loop, when the REPL is accessible.

### `main.py` and startup

MicroPython runs `boot.py` (if present) and then `main.py` during startup. Saving `main.py` on the Raspberry Pi does not automatically update the ESP32. The file must be copied to the ESP32 filesystem.

- Raspberry Pi copy: `~/Projects/iot/main.py`
- ESP32 copy: `:main.py` in `mpremote` commands

The ESP32 keeps its filesystem contents in flash, so the program remains available after power is disconnected.

### `mpremote`

`mpremote` is a command-line utility for communicating with a MicroPython device, accessing its filesystem, running code, and resetting it.

Use commands from the **Raspberry Pi Linux shell**, where the prompt resembles `$`. Do not type Linux commands at the ESP32 Python prompt `>>>`.

## 5. Current project program

The latest intended LED rhythm is a Jingle Bells-style flashing pattern. It uses an active buzzer only as a future possibility; **the buzzer is not connected and is out of scope for now**.

Example current `main.py` rhythm:

```python
from machine import Pin
from time import sleep

led = Pin(2, Pin.OUT)

# Each pair is (LED-on duration, pause after it), in seconds.
rhythm = [
    (0.25, 0.08), (0.25, 0.08), (0.50, 0.18),
    (0.25, 0.08), (0.25, 0.08), (0.50, 0.18),
    (0.25, 0.08), (0.25, 0.08), (0.25, 0.08),
    (0.25, 0.08), (0.75, 0.25),

    (0.25, 0.08), (0.25, 0.08), (0.25, 0.08),
    (0.25, 0.08), (0.25, 0.08), (0.25, 0.08),
    (0.25, 0.08), (0.25, 0.08), (0.50, 0.18),

    (0.25, 0.08), (0.25, 0.08), (0.25, 0.08),
    (0.25, 0.08), (0.50, 0.18),
    (0.25, 0.08), (0.25, 0.08), (0.75, 0.50),
]

while True:
    for on_time, pause in rhythm:
        led.on()
        sleep(on_time)
        led.off()
        sleep(pause)

    sleep(1)
```

This is a rhythm-inspired LED pattern, not an exact musical transcription. An active buzzer generally produces a fixed tone and is not ideal for playing a melody with changing pitches. Do not wire the unidentified buzzer until its voltage/current needs and a safe drive circuit are established.

## 6. How to resume the project

### A. Activate the environment

```bash
source ~/Projects/iot-tools/.venv/bin/activate
```

### B. Confirm the project file exists

```bash
ls -l ~/Projects/iot/main.py
cat ~/Projects/iot/main.py
```

### C. Confirm the serial device is detected

```bash
mpremote connect list
```

Expected to include `/dev/ttyUSB0` and the Silicon Labs CP210x/CP2102 bridge.

### D. Upload the current program

Run from the Raspberry Pi shell:

```bash
mpremote connect /dev/ttyUSB0 fs cp ~/Projects/iot/main.py :main.py
```

### E. Reset the ESP32

```bash
mpremote connect /dev/ttyUSB0 reset
```

The LED should run the program stored as `main.py`.

### F. Verify persistence

If needed, disconnect USB power, wait a few seconds, reconnect it, and check that the LED pattern starts without issuing a command.

## 7. Troubleshooting notes

### `could not enter raw repl`

This means `mpremote` could not switch the device into its raw REPL. A running startup loop, a stale serial session, or serial communication timing can contribute.

Try in this order:

1. Close any other serial terminal or program using `/dev/ttyUSB0`.
2. If in the MicroPython REPL, press **Ctrl+C** to interrupt the running loop, then **Ctrl+]** to exit `mpremote`.
3. Retry the upload command.
4. If the device is responsive, try `mpremote connect /dev/ttyUSB0 soft-reset`.
5. If needed, run `mpremote connect /dev/ttyUSB0 repl` and inspect any startup error.

Do not erase flash or reinstall firmware for this error alone.

### `device ... may be in use by another program`

Check for a process using the port:

```bash
sudo fuser -v /dev/ttyUSB0
```

No output means `fuser` did not identify a process; it does not prove every possible serial conflict is impossible. Check for open serial terminals and retry.

### `SyntaxError` after a command like `mpremote ...`

Check which prompt is active:

- `raspberrypi@raspberrypi:... $` — Raspberry Pi Linux shell; run `mpremote` commands here.
- `>>>` — Python REPL on the ESP32; enter Python code here, not Linux commands.

### LED stops after a reset

Reconnect to the REPL and inspect any error. Confirm the local `main.py` contents and upload it again if appropriate. A soft or hardware reset does not erase the ESP32 filesystem.

## 8. Git checkpoint

Keep the source file and this checkpoint document in the Git repository. Suggested filenames:

- `main.py` — MicroPython application
- `README.md` — short project overview and setup
- `docs/ESP32_CHECKPOINT.md` — this detailed learning and resume note

Before committing, check the repository state:

```bash
cd ~/Projects/iot
git status
```

Example commit message:

```text
feat: add ESP32 LED rhythm pattern
```

Only commit after verifying the actual changes and ensuring the repository is initialized and the intended remote is configured.

## 9. Next learning steps

Proceed one small task at a time:

1. Improve LED patterns and learn how to change timing values.
2. Learn GPIO input using a push button.
3. Learn basic electrical safety, voltage levels, current limits, and resistors.
4. Connect a suitable sensor and read its values.
5. Connect the ESP32 to Wi-Fi.
6. Explore MQTT and communication with the Raspberry Pi.
7. Add a buzzer only after identifying its specifications and selecting a safe circuit.

## 10. Working preferences

- Use beginner-friendly, incremental steps with short explanations.
- Use `vi` for editing.
- Use the existing virtual environment and `/dev/ttyUSB0`, unless diagnostics indicate otherwise.
- Prefer read-only diagnostics before changes.
- Never erase flash or reflash firmware without explaining the consequences and getting confirmation.
- Explain what each command does, not just what to copy and paste.

---
**Checkpoint status:** MicroPython works; GPIO 2 LED control works; `main.py` starts automatically; LED rhythm project is the current focus; buzzer postponed.
