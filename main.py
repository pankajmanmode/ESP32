
from machine import Pin
from time import sleep

led = Pin(2, Pin.OUT)

# Jingle Bells rhythm: (flash duration, pause)
# Longer flashes represent longer notes.
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

    # Brief pause before the next performance
    sleep(1)
