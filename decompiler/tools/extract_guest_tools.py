#!/usr/bin/env python3
"""Unpack the prebuilt guest-side tools from upstream's macOS release.

    python3 tools/extract_guest_tools.py [zip] [outdir]

defaults: oracle/downloads/iPod-touch-2G-macOS.zip -> oracle/firmware/guest-tools/

WHY: the MBXGLEngine replacement (contrib/it-gles/mbxshim.c) forwards the
guest's GL ES calls to QEMU instead of driving the MBX GPU, which is not
emulated. Without it every GL app hangs its main thread in the stock engine on
its first present (measured on MGST, LOG 2026-09-27 step 1). Building it needs
macOS + the iPhoneOS 3.1.3 SDK, but it is a GUEST binary (armv6 Mach-O), so the
copy upstream ships inside its macOS app works on any host.

The container is `Contents/Resources/device/tools.itblob`, format ITBLOB01 from
contrib/macos-app/ipod-helper.c (blob_pack/blob_unpack): magic(8) rawlen(u32)
clen(u32) then one zlib stream of entries: namelen(u16) name mode(u32) len(u32)
bytes. All little-endian.
"""

import os
import struct
import sys
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
ZIP = os.path.join(PROJECT, "oracle", "downloads", "iPod-touch-2G-macOS.zip")
OUT = os.path.join(PROJECT, "oracle", "firmware", "guest-tools")
MEMBER = "iPod touch.app/Contents/Resources/device/tools.itblob"


def unpack(blob):
    if blob[:8] != b"ITBLOB01":
        raise ValueError("not an ITBLOB01 container")
    rawlen, clen = struct.unpack_from("<II", blob, 8)
    raw = zlib.decompress(blob[16:16 + clen])
    if len(raw) != rawlen:
        raise ValueError("size mismatch after decompression")
    p = 0
    while p + 2 <= len(raw):
        nl = struct.unpack_from("<H", raw, p)[0]
        name = raw[p + 2:p + 2 + nl].decode()
        p += 2 + nl
        mode, ln = struct.unpack_from("<II", raw, p)
        p += 8
        yield name, mode, raw[p:p + ln]
        p += ln


def main():
    zpath = sys.argv[1] if len(sys.argv) > 1 else ZIP
    out = sys.argv[2] if len(sys.argv) > 2 else OUT
    with zipfile.ZipFile(zpath) as z:
        blob = z.read(MEMBER)
    os.makedirs(out, exist_ok=True)
    for name, mode, data in unpack(blob):
        if "/" in name or name.startswith("."):
            raise ValueError("refusing unsafe entry name %r" % name)
        magic, cpu, sub, ftype = struct.unpack_from("<IIII", data, 0)
        dst = os.path.join(out, name)
        with open(dst, "wb") as f:
            f.write(data)
        os.chmod(dst, mode & 0o777)
        print("%-12s %7d bytes  mode %o  mach-o magic %#x cputype %d subtype %d filetype %d"
              % (name, len(data), mode & 0o777, magic, cpu, sub, ftype))


if __name__ == "__main__":
    main()
