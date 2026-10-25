"""
MicroPython port of the supplied eye-animation sketch.
Target: ESP32 + SSD1306 OLED, 128x64, I2C SDA=21 / SCL=22.
Save this file on the ESP32 as main.py.

Animations included:
  wakeup, reset, move_right_big, move_left_big, blink_long,
  blink_short, happy, sleep, and random eye saccades.

Change DEMO_MODE to False and set MANUAL_ANIMATION to one of the
names above if you want to display one animation repeatedly.
"""

from machine import Pin, I2C
import ssd1306
import time
import random

# ---- OLED setup: keep the working pins for your setup ----
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ---- Reference eye dimensions adapted from the original sketch ----
REF_EYE_HEIGHT = 40
REF_EYE_WIDTH = 40
REF_SPACE_BETWEEN_EYE = 10
REF_CORNER_RADIUS = 10

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

DEMO_MODE = True
MANUAL_ANIMATION = "blink_short"

# Current eye state: [x_center, y_center, width, height]
left_eye = [0, 0, REF_EYE_WIDTH, REF_EYE_HEIGHT]
right_eye = [0, 0, REF_EYE_WIDTH, REF_EYE_HEIGHT]
corner_radius = REF_CORNER_RADIUS


def _inside_round_rect(px, py, x, y, w, h, r):
    """Return True if a pixel lies inside a rounded rectangle."""
    if px < x or px >= x + w or py < y or py >= y + h:
        return False
    r = max(0, min(r, (w - 1) // 2, (h - 1) // 2))
    if r == 0:
        return True

    # Test against the nearest corner-circle only when in a corner zone.
    cx = x + r if px < x + r else (x + w - 1 - r if px >= x + w - r else px)
    cy = y + r if py < y + r else (y + h - 1 - r if py >= y + h - r else py)
    if px < x + r or px >= x + w - r:
        if py < y + r or py >= y + h - r:
            return (px - cx) ** 2 + (py - cy) ** 2 <= r * r
    return True


def draw_filled_round_rect(x, y, w, h, r, color=1):
    """Draw a filled rounded rectangle using standard SSD1306 methods."""
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    x1 = min(SCREEN_WIDTH, x + w)
    y0 = max(0, y)
    y1 = min(SCREEN_HEIGHT, y + h)
    for py in range(y0, y1):
        run_start = None
        for px in range(x0, x1):
            inside = _inside_round_rect(px, py, x, y, w, h, r)
            if inside and run_start is None:
                run_start = px
            elif not inside and run_start is not None:
                oled.hline(run_start, py, px - run_start, color)
                run_start = None
        if run_start is not None:
            oled.hline(run_start, py, x1 - run_start, color)


def draw_filled_triangle(x1, y1, x2, y2, x3, y3, color):
    """Filled triangle scan conversion, using OLED horizontal lines."""
    min_y = max(0, min(y1, y2, y3))
    max_y = min(SCREEN_HEIGHT - 1, max(y1, y2, y3))
    points = ((x1, y1, x2, y2), (x2, y2, x3, y3), (x3, y3, x1, y1))
    for y in range(min_y, max_y + 1):
        intersections = []
        for ax, ay, bx, by in points:
            if ay == by:
                continue
            if min(ay, by) <= y < max(ay, by):
                x = ax + (y - ay) * (bx - ax) / (by - ay)
                intersections.append(int(x))
        if len(intersections) >= 2:
            left = max(0, min(intersections))
            right = min(SCREEN_WIDTH - 1, max(intersections))
            if right >= left:
                oled.hline(left, y, right - left + 1, color)


def draw_eye(eye):
    cx, cy, w, h = eye
    x = int(cx - w // 2)
    y = int(cy - h // 2)
    r = min(corner_radius, max(0, w // 2 - 1), max(0, h // 2 - 1))
    draw_filled_round_rect(x, y, w, h, r, 1)


def draw_frame():
    oled.fill(0)
    draw_eye(left_eye)
    draw_eye(right_eye)
    oled.show()


def reset_eyes(update=True):
    global corner_radius
    left_eye[:] = [
        SCREEN_WIDTH // 2 - REF_EYE_WIDTH // 2 - REF_SPACE_BETWEEN_EYE // 2,
        SCREEN_HEIGHT // 2,
        REF_EYE_WIDTH,
        REF_EYE_HEIGHT,
    ]
    right_eye[:] = [
        SCREEN_WIDTH // 2 + REF_EYE_WIDTH // 2 + REF_SPACE_BETWEEN_EYE // 2,
        SCREEN_HEIGHT // 2,
        REF_EYE_WIDTH,
        REF_EYE_HEIGHT,
    ]
    corner_radius = REF_CORNER_RADIUS
    if update:
        draw_frame()


def blink(speed=12, pause_ms=25):
    global corner_radius
    reset_eyes(False)

    # Close
    for _ in range(3):
        left_eye[3] = max(2, left_eye[3] - speed)
        right_eye[3] = max(2, right_eye[3] - speed)
        left_eye[2] += 3
        right_eye[2] += 3
        corner_radius = min(REF_CORNER_RADIUS, max(1, left_eye[3] // 2))
        draw_frame()
        time.sleep_ms(pause_ms)

    # Open
    for _ in range(3):
        left_eye[3] = min(REF_EYE_HEIGHT, left_eye[3] + speed)
        right_eye[3] = min(REF_EYE_HEIGHT, right_eye[3] + speed)
        left_eye[2] = max(REF_EYE_WIDTH, left_eye[2] - 3)
        right_eye[2] = max(REF_EYE_WIDTH, right_eye[2] - 3)
        corner_radius = min(REF_CORNER_RADIUS, max(1, left_eye[3] // 2))
        draw_frame()
        time.sleep_ms(pause_ms)

    reset_eyes()


def sleep_eyes():
    global corner_radius
    reset_eyes(False)
    left_eye[3] = 2
    right_eye[3] = 2
    left_eye[2] = REF_EYE_WIDTH
    right_eye[2] = REF_EYE_WIDTH
    corner_radius = 0
    draw_frame()


def wakeup():
    global corner_radius
    reset_eyes(False)
    left_eye[3] = 2
    right_eye[3] = 2
    corner_radius = 1
    for h in range(2, REF_EYE_HEIGHT + 1, 2):
        left_eye[3] = h
        right_eye[3] = h
        corner_radius = min(REF_CORNER_RADIUS, max(1, h // 2))
        draw_frame()
        time.sleep_ms(25)


def happy_eye():
    reset_eyes(True)
    offset = REF_EYE_HEIGHT // 2
    for _ in range(10):
        # Mask the lower portions to create cheerful, upward-cornered eyes.
        draw_filled_triangle(
            left_eye[0] - left_eye[2] // 2 - 1,
            left_eye[1] + offset,
            left_eye[0] + left_eye[2] // 2 + 1,
            left_eye[1] + 5 + offset,
            left_eye[0] - left_eye[2] // 2 - 1,
            left_eye[1] + left_eye[3] + offset,
            0,
        )
        draw_filled_triangle(
            right_eye[0] + right_eye[2] // 2 + 1,
            right_eye[1] + offset,
            right_eye[0] - right_eye[2] // 2 - 2,
            right_eye[1] + 5 + offset,
            right_eye[0] + right_eye[2] // 2 + 1,
            right_eye[1] + right_eye[3] + offset,
            0,
        )
        offset -= 2
        oled.show()
        time.sleep_ms(25)
    time.sleep_ms(700)
    reset_eyes()


def saccade(direction_x, direction_y):
    """Quick eye movement, then return to the original position."""
    for _ in range(2):
        for eye in (left_eye, right_eye):
            eye[0] += 8 * direction_x
            eye[1] += 6 * direction_y
            eye[3] = max(12, min(REF_EYE_HEIGHT, eye[3] - 8 if _ == 0 else eye[3] + 8))
        draw_frame()
        time.sleep_ms(35)


def random_saccades():
    reset_eyes()
    for _ in range(8):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        saccade(dx, dy)
        saccade(-dx, -dy)
        time.sleep_ms(60)
    reset_eyes()


def move_big_eye(direction):
    reset_eyes(False)
    movement = 2
    blink_amount = 5

    # Move eyes outward while narrowing them; one eye grows slightly.
    target = right_eye if direction > 0 else left_eye
    for _ in range(3):
        left_eye[0] += movement * direction
        right_eye[0] += movement * direction
        left_eye[3] = max(18, left_eye[3] - blink_amount)
        right_eye[3] = max(18, right_eye[3] - blink_amount)
        target[3] = min(REF_EYE_HEIGHT, target[3] + 1)
        target[2] += 1
        draw_frame()
        time.sleep_ms(35)

    for _ in range(3):
        left_eye[0] += movement * direction
        right_eye[0] += movement * direction
        left_eye[3] = min(REF_EYE_HEIGHT, left_eye[3] + blink_amount)
        right_eye[3] = min(REF_EYE_HEIGHT, right_eye[3] + blink_amount)
        target[3] = min(REF_EYE_HEIGHT, target[3] + 1)
        target[2] += 1
        draw_frame()
        time.sleep_ms(35)

    time.sleep_ms(400)

    # Restore positions and sizes in small steps.
    for _ in range(6):
        left_eye[0] -= movement * direction
        right_eye[0] -= movement * direction
        left_eye[2] += (REF_EYE_WIDTH - left_eye[2]) // max(1, 6 - _)
        right_eye[2] += (REF_EYE_WIDTH - right_eye[2]) // max(1, 6 - _)
        left_eye[3] += (REF_EYE_HEIGHT - left_eye[3]) // max(1, 6 - _)
        right_eye[3] += (REF_EYE_HEIGHT - right_eye[3]) // max(1, 6 - _)
        draw_frame()
        time.sleep_ms(30)

    reset_eyes()


def move_right_big_eye():
    move_big_eye(1)


def move_left_big_eye():
    move_big_eye(-1)


ANIMATIONS = [
    ("wakeup", wakeup),
    ("reset", reset_eyes),
    ("move_right_big", move_right_big_eye),
    ("move_left_big", move_left_big_eye),
    ("blink_long", lambda: (blink(12), time.sleep_ms(700))),
    ("blink_short", lambda: blink(12)),
    ("happy", happy_eye),
    ("sleep", sleep_eyes),
    ("saccade_random", random_saccades),
]


def run_animation(name):
    for animation_name, function in ANIMATIONS:
        if animation_name == name:
            function()
            return
    raise ValueError("Unknown animation: " + name)


# Startup: show sleeping eyes, then wake up.
sleep_eyes()
time.sleep_ms(500)
wakeup()

if DEMO_MODE:
    while True:
        for name, function in ANIMATIONS:
            function()
            time.sleep_ms(250)
else:
    while True:
        run_animation(MANUAL_ANIMATION)
        time.sleep_ms(500)
