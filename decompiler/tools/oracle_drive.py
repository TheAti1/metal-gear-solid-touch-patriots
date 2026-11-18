#!/usr/bin/env python3
"""Minimal tap driver for memory-injected coverage runs (LOG STEP 5).

    oracle_drive.py SECONDS FRAMEDIR

Pair with tools/mgst_gdb.py (mgst-godmode / mgst-autohit / mgst-stage): the
injected state makes every shot hit and Snake unkillable, so this only
presses READY, taps to fire, presses NEXT, and saves one frame per cycle.
It STOPS as soon as the title menu (green power icon) is on screen, so it
never taps its way into the "?"/web links or other apps.
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle_input as oi  # noqa: E402

SIZE = (480, 320)


def retry(fn, *a, **kw):
    """gdb breakpoint handling pauses the VM for a moment; QMP input fails then."""
    for i in range(10**9):        # wait as long as it takes: mgst_difftest.py pauses the VM per test
        try:
            return fn(*a, **kw)
        except RuntimeError as e:
            if "not running" not in str(e):
                raise
            time.sleep(0.2)
    raise RuntimeError("VM stayed stopped")
FIRE = [(240, 130), (160, 110), (320, 110), (200, 190), (290, 190), (240, 80), (120, 160), (360, 160)]


def is_ready(im):
    return all(im.getpixel(p) == (255, 255, 255) for p in ((240, 90), (240, 100), (100, 180), (380, 180)))


def is_title(im):
    g = [im.getpixel(p) for p in ((50, 160), (110, 160))]
    return all(px[1] > 180 and px[0] < 120 and px[2] < 120 for px in g)


def is_ios_ui(im):
    """iOS status-bar strip down the left edge of the landscape frame (light
    grey, ~231,238,241) - Mail/Safari/iPod/Settings; MGST never draws it."""
    return all(min(im.getpixel((4, y))) > 200 for y in (100, 160, 300))


def main():
    total, out = float(sys.argv[1]), sys.argv[2]
    os.makedirs(out, exist_ok=True)
    q = oi.QMP(oi.QMP_SOCK)
    t0, n, foreign = time.time(), 0, 0
    while time.time() - t0 < total:
        im = retry(oi.frame, q)
        im.save(os.path.join(out, "c%04d.png" % n))
        n += 1
        foreign = foreign + 1 if is_ios_ui(im) else 0
        if foreign >= 3:
            print("not in MGST for 3 frames (iOS UI) after %d cycles - stopping" % n)
            return
        if is_title(im):
            print("title menu reached after %d cycles - stopping" % n)
            return
        if is_ready(im):
            retry(oi.tap, q, 460, 300, size=SIZE)
            time.sleep(3)
            continue
        for x, y in random.sample(FIRE, 5):
            retry(oi.tap, q, x, y, size=SIZE)
            time.sleep(0.25)
        if n % 6 == 0:
            retry(oi.tap, q, 40, 40, size=SIZE)       # REX weapon switch / harmless elsewhere
        retry(oi.tap, q, 425, 300, size=SIZE)          # NEXT on story pages
        retry(oi.tap, q, 440, 253, size=SIZE)          # NEXT on the result screen (never SAVE & EXIT at left)
        time.sleep(1)
    print("drive done: %d cycles" % n)


if __name__ == "__main__":
    main()
