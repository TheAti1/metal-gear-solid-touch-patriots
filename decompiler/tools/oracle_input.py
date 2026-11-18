#!/usr/bin/env python3
"""Drive MGST's touch input on the running oracle, in DISPLAYED-frame pixels.

    oracle_input.py orient 3            accelerometer: 1 portrait, 3 landscape (Home right)
    oracle_input.py tap X Y             short tap (fires / presses a button)
    oracle_input.py drag X1 Y1 X2 Y2    drag (moves the in-game sight)
    oracle_input.py shot out.png        screendump (480x320 when landscape)

Everything here was measured on 2026-09-27/28 (LOG step 4c):

* TAPS MUST BE SHORT. The game counts a tap only if the finger lifts within 5
  frames of touching down (-[MyEAGLView getTouchOut:]: touch_time < 5). At the
  emulated ~16-20 fps, itqmp's default 120 ms hold plus event latency often
  misses that; a 30 ms hold lands at touch_time == 1 (read at touchesEnded).
* COORDINATES FOLLOW THE DISPLAY. After the game rotates (accel-orientation 3),
  QEMU's screendump is 480x320 and the LCD's absolute-pointer handler takes the
  host position as a fraction of THAT frame, then rotates it to the portrait
  panel itself. So a point (X, Y) on the screenshot is sent as X/(W-1), Y/(H-1).
  itqmp.move scales by 319/479 (portrait), hence the conversion below.
* ORIENTATION PAUSES THE GAME. Held upright (the emulator's default), MGST opens
  its pause/OPTIONS menu; gameplay needs `orient 3`.
* CONTROLS: drag anywhere to move the sight (drag delta ~= sight delta), tap to
  fire -- Snake rises from cover and shoots at the sight.
"""

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "oracle", "qemu-ios", "imgtools"))
from itqmp import QMP, shot_ppm, move  # noqa: E402

try:
    from PIL import Image
except ImportError:
    sys.exit("needs Pillow: pip install --user pillow")

QMP_SOCK = os.environ.get("MGST_QMP", "/tmp/mgst-ipod.sock")
TAP_HOLD = 0.03


def frame(q, path="/tmp/oracle_input_frame.ppm"):
    return Image.open(shot_ppm(q, path, 1)).convert("RGB")


def to_host(q, X, Y, size=None):
    """Displayed-frame pixel -> the (x, y) itqmp expects (portrait 320x480 scale)."""
    W, H = size or frame(q).size
    return X * 319 / (W - 1), Y * 479 / (H - 1)


def tap(q, X, Y, size=None, hold=TAP_HOLD):
    q.tap(*to_host(q, X, Y, size), hold=hold)


def drag(q, X1, Y1, X2, Y2, size=None, steps=10, dt=0.04):
    size = size or frame(q).size
    move(q, *to_host(q, X1, Y1, size))
    time.sleep(0.05)
    q.cmd("input-send-event", events=[{"type": "btn", "data": {"down": True, "button": "left"}}])
    for i in range(1, steps + 1):
        move(q, *to_host(q, X1 + (X2 - X1) * i / steps, Y1 + (Y2 - Y1) * i / steps, size))
        time.sleep(dt)
    time.sleep(0.1)
    q.cmd("input-send-event", events=[{"type": "btn", "data": {"down": False, "button": "left"}}])


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    q = QMP(QMP_SOCK)
    if a[0] == "orient":
        q.cmd("qom-set", path="/machine", property="accel-orientation", value=int(a[1]))
    elif a[0] == "tap":
        tap(q, float(a[1]), float(a[2]))
    elif a[0] == "drag":
        drag(q, *map(float, a[1:5]))
    elif a[0] == "shot":
        im = frame(q)
        im.save(a[1])
        print(a[1], im.size)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
