#!/usr/bin/env python3
"""Probe the structure of the paired .al / .rl resource files.

DWUtilities exposes readAnimeData/readRectData, getPartsNun/getPartsData,
getKomaData ("koma" = animation frame), getMaxFrame and getPackImageWH, so
.al is an animation list and .rl a rect list. There are 102 of each, pairing
1:1 by basename. This script tests the header hypothesis against every file
rather than generalising from one sample.
"""
import struct
from collections import Counter
from pathlib import Path

APP = Path("work/extracted/Payload/MGSTUS.app")


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def s16(b, o):
    return struct.unpack_from("<h", b, o)[0]


def probe(ext):
    files = sorted(APP.glob(f"*{ext}"))
    print(f"\n{'='*66}\n{ext}  ({len(files)} files)\n{'='*66}")
    fits = Counter()
    rows = []
    for p in files:
        b = p.read_bytes()
        n = len(b)
        a, c = u16(b, 0), u16(b, 2)
        body = n - 4
        # Does "first header word = record count" hold, and with what stride?
        stride = body / a if a else 0
        exact = (a and body % a == 0)
        fits[(round(stride, 2) if exact else "non-integer")] += 1
        rows.append((p.name, n, a, c, stride if exact else None))
    print("header[0] as record count -> implied stride:")
    for k, v in fits.most_common():
        print(f"   stride {k:<14} {v} files")
    print("\nsample:")
    print(f"  {'file':<12}{'size':>6}{'hdr0':>6}{'hdr1':>6}{'stride':>9}")
    for name, n, a, c, st in rows[:14]:
        print(f"  {name:<12}{n:>6}{a:>6}{c:>6}{str(st):>9}")
    return rows


def dump_records(path, stride, nrec):
    b = path.read_bytes()
    print(f"\n--- {path.name}  ({len(b)} bytes, {nrec} x {stride}B records) ---")
    print(f"header: {u16(b,0)}, {u16(b,2)}")
    for i in range(min(nrec, 8)):
        o = 4 + i * stride
        rec = b[o:o + stride]
        us = [u16(rec, j) for j in range(0, len(rec) - 1, 2)]
        ss = [s16(rec, j) for j in range(0, len(rec) - 1, 2)]
        print(f"  [{i}] u16={us}")
        print(f"      s16={ss}")


def main():
    al = probe(".al")
    rl = probe(".rl")

    # Deep look at a matched pair where the stride is unambiguous.
    for name, n, a, c, st in al:
        if st == 16.0:
            dump_records(APP / name, 16, a)
            rlp = APP / (name[:-3] + ".rl")
            brl = rlp.read_bytes()
            arl = u16(brl, 0)
            if arl and (len(brl) - 4) % arl == 0:
                dump_records(rlp, (len(brl) - 4) // arl, arl)
            break

    # Are the two header words always equal? Are al/rl headers matched?
    same_hdr = sum(1 for nm, n, a, c, st in al if a == c)
    print(f"\n.al files where hdr0 == hdr1: {same_hdr}/{len(al)}")
    pair_match = 0
    for nm, n, a, c, st in al:
        brl = (APP / (nm[:-3] + ".rl")).read_bytes()
        if u16(brl, 0) == a:
            pair_match += 1
    print(f".al/.rl pairs with identical hdr0: {pair_match}/{len(al)}")


if __name__ == "__main__":
    main()
