#!/usr/bin/env python3
"""Parsers for the .al (animation) and .rl (rect) resource formats.

Transcribed from the decompiled loaders, not inferred from hexdumps:
  DWUtilities readAnimeData:: @ 0x22f5c   -> .al
  DWUtilities readRectData::  @ 0x23190  -> .rl

Both are nested and variable-length. An earlier guess that they were flat
16-byte records fit ~55% of files by coincidence and was wrong; that is why
43 .rl files "did not divide evenly".

.al                                  .rl
  int16 frameCount                     int16 groupCount
  int16 unk                            int16 unk
  frameCount x:                        groupCount x:
    int16 partCount                      int16 itemCount
    int16 unk                            itemCount x:
    partCount x:                           int16 rect[7]   (stride 0x0e)
      int16 part[6]  (stride 0x0c)

Field meanings, from cross-referencing 000.al/000.rl:
  .al part = [rectIndex, ?, offsetX, offsetY, ?, ?]   offsets are signed
  .rl item = [textureId, x, y, w, h, ?, ?]            a texture-atlas rect

The parsers are validated by exact consumption: a correct structural reading
consumes every byte of all 204 files with none left over.
"""
import json
import struct
import sys
from pathlib import Path

APP = Path("work/extracted/Payload/MGSTUS.app")


class Reader:
    def __init__(self, data):
        self.d = data
        self.o = 0

    def s16(self):
        v, = struct.unpack_from("<h", self.d, self.o)
        self.o += 2
        return v

    def remaining(self):
        return len(self.d) - self.o


def parse_al(data):
    """Animation list: frames of parts referencing .rl rects."""
    r = Reader(data)
    frame_count = r.s16()
    unk = r.s16()
    frames = []
    for _ in range(frame_count):
        part_count = r.s16()
        f_unk = r.s16()
        parts = [[r.s16() for _ in range(6)] for _ in range(part_count)]
        frames.append({"unk": f_unk, "parts": parts})
    return {"frameCount": frame_count, "unk": unk, "frames": frames}, r.remaining()


def parse_rl(data):
    """Rect list: groups of texture-atlas rectangles."""
    r = Reader(data)
    group_count = r.s16()
    unk = r.s16()
    groups = []
    for _ in range(group_count):
        item_count = r.s16()
        items = [[r.s16() for _ in range(7)] for _ in range(item_count)]
        groups.append({"items": items})
    return {"groupCount": group_count, "unk": unk, "groups": groups}, r.remaining()


def main():
    dump = "--dump" in sys.argv
    outdir = Path("recovered/data")
    if dump:
        outdir.mkdir(parents=True, exist_ok=True)

    total = clean = 0
    bad = []
    for ext, fn in ((".al", parse_al), (".rl", parse_rl)):
        files = sorted(APP.glob(f"*{ext}"))
        for p in files:
            total += 1
            try:
                parsed, left = fn(p.read_bytes())
            except struct.error as e:
                bad.append((p.name, f"truncated: {e}"))
                continue
            if left != 0:
                bad.append((p.name, f"{left} trailing bytes"))
                continue
            clean += 1
            if dump:
                (outdir / (p.name + ".json")).write_text(
                    json.dumps(parsed, separators=(",", ":")))

    print(f"parsed cleanly : {clean}/{total}")
    if bad:
        print(f"\nFAILED ({len(bad)}):")
        for n, why in bad[:20]:
            print(f"  {n}: {why}")
        sys.exit(1)
    print("every file consumed exactly — structure confirmed")

    # Show a worked example so the field layout is inspectable.
    al, _ = parse_al((APP / "000.al").read_bytes())
    rl, _ = parse_rl((APP / "000.rl").read_bytes())
    print("\n000.al  frames:")
    for i, f in enumerate(al["frames"]):
        print(f"  frame[{i}] unk={f['unk']} parts={f['parts']}")
    print("000.rl  groups:")
    for i, g in enumerate(rl["groups"]):
        print(f"  group[{i}] items={g['items']}")


if __name__ == "__main__":
    main()
