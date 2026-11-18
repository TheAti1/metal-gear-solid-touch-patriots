#!/usr/bin/env python3
"""Drive the oracle from wherever it is to "MGST is the foreground app".

    mgst_launch.py            # wake, unlock, find MGST, launch it
    mgst_launch.py --shot X   # ...and save the final frame to X

Every step is verified from the framebuffer rather than assumed, because the
device is not a reliable state machine here: it display-sleeps on its own, the
digitizer does not come back until a hardware button is pressed, and a tap sent
to a sleeping digitizer is silently dropped. Blind tap sequences appear to work
and then land somewhere unintended - a repeated slide-to-unlock, for instance,
lands on an icon and opens "Edit Home Screen" instead.

This exists so `mgst_probe.py` has a defined starting state: its VA->PA
translation reads whichever user process is current, so "MGST is foreground" is
a precondition for every measurement, not a nicety.
"""

import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "oracle", "qemu-ios", "imgtools"))
from itqmp import QMP, shot_ppm  # noqa: E402

try:
    from PIL import Image
except ImportError:
    sys.exit("needs Pillow: pip install --user pillow")

QMP_SOCK = os.environ.get("MGST_QMP", "/tmp/mgst-ipod.sock")
ICON_XY = (40, 60)        # MGSTouch, first slot on home screen page 2
SLIDE = (60, 427, 295, 427)


def grab(q, tmp="/tmp/mgst-launch.ppm"):
    return Image.open(shot_ppm(q, tmp, 1)).convert("RGB")


def colors(im, box):
    return len(set(im.crop(box).getdata()))


def is_dark(im):
    return colors(im, (0, 0, 320, 480)) <= 2


def has_dock(im):
    # The home-screen dock is full of colourful icons; the lock screen's
    # slider is flat grey. Pixel totals alone cannot tell the two apart.
    return colors(im, (0, 400, 320, 470)) > 3000


def has_statusbar(im):
    # SpringBoard shows the grey status bar; MGST runs fullscreen without it.
    return colors(im, (0, 0, 320, 18)) > 20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot")
    ap.add_argument("--sock", default=QMP_SOCK)
    a = ap.parse_args()
    q = QMP(a.sock)

    # 1. wake. The digitizer stays asleep until a hardware button is pressed,
    #    so this is not optional even when the panel is already lit.
    for _ in range(3):
        q.home(); time.sleep(2)
        if not is_dark(grab(q)):
            break
    else:
        sys.exit("screen stayed dark after three Home presses")
    print("awake")

    # 2. unlock, re-checking between attempts so we never slide a home screen
    for i in range(5):
        if has_dock(grab(q)):
            print("unlocked"); break
        q.home(); time.sleep(2)
        q.swipe(*SLIDE); time.sleep(3)
    else:
        sys.exit("still locked after five attempts")

    # 3. MGST lives on page 2; page 1 is the stock apps
    q.swipe(280, 250, 40, 250, steps=14, dwell=0.03); time.sleep(2.5)

    # 4. Launch, and confirm by the only signal that actually proves it:
    #    MGSTUS owning TTBR0.
    #
    #    "the status bar went away" is NOT proof and must not be used. A
    #    display-asleep screen is uniformly black, so it has no status bar
    #    either - that false positive reported MGST as foreground while the
    #    panel was off and SpringBoard held the CPU, and every measurement
    #    taken afterwards described the wrong process. Pixels cannot answer
    #    "which process is running"; the page tables can.
    sys.path.insert(0, HERE)
    from mgst_probe import Probe  # noqa: E402
    probe = Probe(q=q)          # share this connection; QMP serves one client

    for i in range(3):
        q.tap(*ICON_XY); time.sleep(6)
        ok, msg, n = probe.wait_for_context(tries=40, delay=0.25)
        if ok:
            print("MGST confirmed running (%s; caught on poll %d)" % (msg, n))
            if a.shot:
                grab(q).save(a.shot); print("frame ->", a.shot)
            return 0
        print("tap %d: %s" % (i + 1, msg))
    sys.exit("MGST never became the scheduled process - it is not running")


if __name__ == "__main__":
    sys.exit(main())
