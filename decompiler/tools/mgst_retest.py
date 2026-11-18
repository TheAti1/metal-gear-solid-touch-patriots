#!/usr/bin/env python3
"""Quick re-test of a few functions after a fix (does not touch the ledger).

    tools/mgst_retest.py ADDR [ADDR ...] [--frames-dirs N] [--calls-dirs N]

Runs, for just these functions: the offline per-call diff (all per-call
captures), the frame driver on N mission snapshots, and synthetic calls on N
mission snapshots; prints the verdicts per function and source. Results go
to a scratch dir (MGST_RETEST_DIR, default /tmp/mgst_retest), never to the
recovered/compile result files the ledger reads."""
import argparse
import collections
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("addrs", nargs="+")
    ap.add_argument("--frames-dirs", type=int, default=3)
    ap.add_argument("--calls-dirs", type=int, default=3)
    ap.add_argument("--frames", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    out = os.environ.get("MGST_RETEST_DIR", "/tmp/mgst_retest")
    os.makedirs(out, exist_ok=True)
    snap = os.path.join(ROOT, "tools/mgst_snap.py")
    caps = [d for d in sorted(glob.glob(os.path.join(ROOT, "oracle/reports/snap/*/"))) if "_dump" not in d and "menutour" not in d]
    dumps = sorted(glob.glob(os.path.join(ROOT, "oracle/reports/snap/campaign_??-??_dump")))
    pick = lambda n: [dumps[int(i * (len(dumps) - 1) / max(1, n - 1))] for i in range(n)] if n else []
    runs = []
    if caps:
        runs.append(("offline", [sys.executable, snap, "diff"] + caps + ["--only"] + a.addrs +
                     ["--jobs", str(a.jobs), "--out", out + "/offline.jsonl"]))
    if a.frames_dirs:
        runs.append(("frames", [sys.executable, snap, "frames"] + pick(a.frames_dirs) + ["--only"] + a.addrs +
                     ["--frames", str(a.frames), "--jobs", str(a.jobs), "--out", out + "/frames.jsonl"]))
    if a.calls_dirs:
        runs.append(("calls", [sys.executable, snap, "calls"] + pick(a.calls_dirs) + ["--only"] + a.addrs +
                     ["--per-dir", "1", "--jobs", str(a.jobs), "--out", out + "/calls.jsonl"]))
    res = collections.defaultdict(collections.Counter)
    detail = {}
    for name, cmd in runs:
        f = out + "/%s.jsonl" % name
        if os.path.exists(f):
            os.remove(f)
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(f):
            for l in open(f):
                r = json.loads(l)
                if r["addr"] in a.addrs or int(r["addr"], 16) in {int(x, 16) for x in a.addrs}:
                    res[(r["addr"], r["name"][:50])][name + ":" + r["verdict"]] += 1
                    if r["verdict"] == "fail":
                        detail.setdefault((r["addr"], name), r.get("detail", "")[:200])
    for k, c in sorted(res.items()):
        print("%s %-50s %s" % (k[0], k[1], dict(sorted(c.items()))))
    for k, d in sorted(detail.items()):
        print("  FAIL %s %s: %s" % (k[0], k[1], d))


if __name__ == "__main__":
    main()
