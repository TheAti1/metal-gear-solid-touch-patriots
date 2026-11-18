#!/usr/bin/env python3
"""Convert Apple CgBI ("iPhone-optimized") PNGs back to standard PNG.

Xcode runs shipped PNGs through a modified pngcrush that produces a format
only CoreGraphics understands. Four differences from standard PNG:

  1. A proprietary `CgBI` chunk is inserted before IHDR.
  2. IDAT holds a RAW deflate stream - no zlib header, no adler32 checksum.
  3. Channel order is BGRA, not RGBA.
  4. Colour is PREMULTIPLIED by alpha.

This matters more than it sounds. A standard decoder reads IHDR fine and
reports correct dimensions, so nothing looks broken - but the pixels come out
wrong. On Android that surfaced as a completely black screen with a
successful-looking texture-load log, which is a miserable thing to debug from
the symptom end.

427 of 760 PNGs in this bundle are CgBI; the rest are already standard, so
detection is per-file rather than assumed.
"""
import argparse
import struct
import sys
import zlib
from pathlib import Path

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def chunks(data):
    """Yield (type, payload) for each chunk after the signature."""
    off = len(PNG_SIG)
    while off + 8 <= len(data):
        (length,) = struct.unpack_from(">I", data, off)
        ctype = data[off + 4:off + 8]
        payload = data[off + 8:off + 8 + length]
        yield ctype, payload
        off += 12 + length          # length + type + payload + crc


def is_cgbi(data):
    if not data.startswith(PNG_SIG):
        return False
    for ctype, _ in chunks(data):
        if ctype == b"CgBI":
            return True
        if ctype == b"IHDR":
            return False            # CgBI always precedes IHDR
    return False


def unfilter(raw, width, height, bpp):
    """Reverse the per-scanline PNG filters. Standard algorithm; CgBI does not
    change it, only what the resulting bytes mean."""
    stride = width * bpp
    out = bytearray(stride * height)
    pos = 0
    for y in range(height):
        ft = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        prev = out[(y - 1) * stride:y * stride] if y else bytearray(stride)

        if ft == 0:
            pass
        elif ft == 1:                                   # Sub
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ft == 2:                                   # Up
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ft == 3:                                   # Average
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ft == 4:                                   # Paeth
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 0xFF
        else:
            raise ValueError(f"bad filter type {ft} on row {y}")

        out[y * stride:(y + 1) * stride] = line
    return bytes(out)


def convert(data):
    """CgBI PNG bytes -> standard RGBA PNG bytes."""
    from PIL import Image

    width = height = depth = ctype_val = None
    idat = bytearray()
    for ctype, payload in chunks(data):
        if ctype == b"IHDR":
            width, height, depth, ctype_val = struct.unpack(">IIBB", payload[:10])
        elif ctype == b"IDAT":
            idat += payload
        elif ctype == b"IEND":
            break

    if width is None:
        raise ValueError("no IHDR")
    if depth != 8 or ctype_val != 6:
        # Every CgBI file in this bundle is 8-bit RGBA. Refuse anything else
        # rather than silently mangling it.
        raise ValueError(f"unsupported CgBI variant: depth={depth} colour={ctype_val}")

    # Raw deflate: no zlib wrapper, hence wbits=-15.
    raw = zlib.decompressobj(-zlib.MAX_WBITS).decompress(bytes(idat))
    px = bytearray(unfilter(raw, width, height, 4))

    # BGRA -> RGBA, and undo premultiplication.
    for i in range(0, len(px), 4):
        b, g, r, a = px[i], px[i + 1], px[i + 2], px[i + 3]
        if a and a != 255:
            r = min(255, (r * 255 + a // 2) // a)
            g = min(255, (g * 255 + a // 2) // a)
            b = min(255, (b * 255 + a // 2) // a)
        px[i], px[i + 1], px[i + 2], px[i + 3] = r, g, b, a

    img = Image.frombytes("RGBA", (width, height), bytes(px))
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="PNG files or directories")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="only report how many are CgBI")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        path = Path(p)
        files.extend(sorted(path.rglob("*.png")) if path.is_dir() else [path])

    cg = [f for f in files if is_cgbi(f.read_bytes())]
    print(f"{len(cg)} of {len(files)} are CgBI")
    if args.check:
        return

    ok = fail = 0
    for f in cg:
        try:
            out = convert(f.read_bytes())
            if args.in_place:
                f.write_bytes(out)
            ok += 1
        except Exception as e:
            print(f"  FAILED {f.name}: {e}", file=sys.stderr)
            fail += 1
    print(f"converted {ok}, failed {fail}")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
