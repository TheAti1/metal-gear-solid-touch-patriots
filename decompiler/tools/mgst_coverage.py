#!/usr/bin/env python3
"""
Decode a drcov trace from contrib/plugins/drcov_mgst.c into per-function
coverage of MGSTUS, in Ghidra VAs.

    tools/mgst_coverage.py oracle/reports/coverage_<ts>.drcov
    tools/mgst_coverage.py A.drcov B.drcov --out analysis/coverage/run.md
    tools/mgst_coverage.py X.drcov --list-hit     # one executed function per line

What it does, and the checks it makes rather than assumes:

* BB starts in the file are OFFSETS from the module-table base (drcov
  semantics; the plugin writes base 0x1000 = MGSTUS's __TEXT vmaddr). They
  are turned back into absolute VAs, which equal Ghidra VAs on iOS 3 (no
  ASLR), PROVIDED the trace and MGST_REF_EXE are the same binary version.
* Blocks are DEDUPLICATED. The plugin writes one row per translated block,
  and every TB-cache flush retranslates the same code, so the raw row count
  (225,949 in the first real run) overstates coverage by a lot.
* Blocks outside the reference binary's __TEXT are counted and reported, not
  silently dropped. A non-trivial number means the identity gate or the
  version pairing is wrong.
* A function counts as executed if any deduplicated block starts inside
  [its address, next function's address). Byte coverage uses the union of
  block ranges clipped to __TEXT.

Env: MGST_REF_EXE (default v2.3.0 MGSTUS), MGST_FUNCMAP (default
analysis/symbols/function_map.csv - must be the SAME version as the trace).
"""
import argparse
import bisect
import collections
import csv
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import macho  # noqa: E402

REF_EXE = os.environ.get(
    "MGST_REF_EXE",
    os.path.join(ROOT, "work/extracted/Payload/MGSTUS.app/MGSTUS"))
FUNCMAP = os.environ.get(
    "MGST_FUNCMAP", os.path.join(ROOT, "analysis/symbols/function_map.csv"))


def read_drcov(path):
    data = open(path, "rb").read()
    marker = b"BB Table: "
    i = data.index(marker)
    eol = data.index(b"\n", i)
    count = int(data[i + len(marker):eol].split()[0])
    header = data[:i].decode()
    base = None
    for line in header.splitlines():
        if line.startswith("0, "):
            base = int(line.split(",")[1], 16)
    if base is None:
        raise SystemExit("%s: no module row 0 in header" % path)
    body = data[eol + 1:]
    if len(body) != count * 8:
        raise SystemExit("%s: BB table says %d rows, body holds %d bytes (%s)"
                         % (path, count, len(body),
                            "truncated - was QEMU SIGKILLed?"
                            if len(body) < count * 8 else "trailing data"))
    rows = [struct.unpack_from("<IHH", body, k * 8) for k in range(count)]
    return base, [(base + off, size) for off, size, _mod in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("traces", nargs="+")
    ap.add_argument("--out", help="write a markdown report here")
    ap.add_argument("--list-hit", action="store_true",
                    help="print executed function names, one per line")
    a = ap.parse_args()

    m = macho.MachO(REF_EXE)
    text = [s for s in m.segments if s[0] == "__TEXT"][0]
    t_lo, t_hi = text[1], text[1] + text[2]

    with open(FUNCMAP) as f:
        rows = sorted((int(r["address"], 16), r["source_file"], r["function"])
                      for r in csv.DictReader(f))
    faddr = [r[0] for r in rows]

    raw = 0
    blocks = set()
    for t in a.traces:
        _base, bbs = read_drcov(t)
        raw += len(bbs)
        blocks.update(bbs)

    outside = [b for b in blocks if not (t_lo <= b[0] < t_hi)]
    inside = sorted(b for b in blocks if t_lo <= b[0] < t_hi)

    hit = collections.Counter()
    for pc, _sz in inside:
        k = bisect.bisect_right(faddr, pc) - 1
        if k >= 0:
            hit[k] += 1

    # byte coverage: union of block ranges
    covered, cur_lo, cur_hi = 0, None, None
    for pc, sz in inside:
        lo, hi = pc, min(pc + sz, t_hi)
        if cur_hi is None or lo > cur_hi:
            if cur_hi is not None:
                covered += cur_hi - cur_lo
            cur_lo, cur_hi = lo, hi
        else:
            cur_hi = max(cur_hi, hi)
    if cur_hi is not None:
        covered += cur_hi - cur_lo

    if a.list_hit:
        for k in sorted(hit):
            print(rows[k][2])
        return

    by_file = collections.defaultdict(lambda: [0, 0])
    for k, r in enumerate(rows):
        by_file[r[1]][1] += 1
        if k in hit:
            by_file[r[1]][0] += 1

    n_fn, n_hit = len(rows), len(hit)
    lines = [
        "# MGSTUS dynamic coverage",
        "",
        "Traces: " + ", ".join("`%s`" % os.path.relpath(t, ROOT) for t in a.traces),
        "Reference: `%s` (__TEXT 0x%x-0x%x)" % (os.path.relpath(REF_EXE, ROOT), t_lo, t_hi),
        "",
        "| | |", "|---|---|",
        "| raw BB rows | %d |" % raw,
        "| unique blocks | %d |" % len(blocks),
        "| unique blocks outside __TEXT (should be ~0) | %d |" % len(outside),
        "| functions executed | **%d / %d (%.1f%%)** |" % (n_hit, n_fn, 100.0 * n_hit / n_fn),
        "| __TEXT bytes executed | %d / %d (%.1f%%) |" % (covered, t_hi - t_lo,
                                                         100.0 * covered / (t_hi - t_lo)),
        "",
        "## Per source file (executed / total functions)",
        "",
        "| file | executed | total | % |", "|---|---:|---:|---:|",
    ]
    for fn, (h, tot) in sorted(by_file.items(), key=lambda kv: (-kv[1][1], kv[0])):
        lines.append("| %s | %d | %d | %.0f%% |" % (fn, h, tot, 100.0 * h / tot))
    report = "\n".join(lines) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, "w").write(report)
        print("wrote", a.out)
    print("\n".join(lines[:13]))


if __name__ == "__main__":
    main()
