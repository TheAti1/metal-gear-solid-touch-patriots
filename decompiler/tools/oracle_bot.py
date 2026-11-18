#!/usr/bin/env python3
"""Crude aim/fire bot for MGST on the oracle: sweep the sight, tap to fire.

    oracle_bot.py SECONDS [--frames DIR]

Used only to drive execution for coverage (step 5), not to play well.
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle_input as oi  # noqa: E402


def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 60
    frames = sys.argv[sys.argv.index("--frames") + 1] if "--frames" in sys.argv else None
    if frames:
        os.makedirs(frames, exist_ok=True)
    q = oi.QMP(oi.QMP_SOCK)
    size = (480, 320)
    t0, n = time.time(), 0
    while time.time() - t0 < secs:
        x1, x2 = random.randint(60, 420), random.randint(60, 420)
        y1, y2 = random.randint(60, 260), random.randint(60, 260)
        oi.drag(q, x1, y1, x2, y2, size=size, steps=4)
        for _ in range(2):
            oi.tap(q, x2, y2, size=size)
            time.sleep(0.15)
        n += 1
        if frames and n % 8 == 0:
            oi.frame(q).save(os.path.join(frames, "f%04d.png" % n))
    print("bot done: %d sweeps in %.0fs" % (n, time.time() - t0))


if __name__ == "__main__":
    main()
