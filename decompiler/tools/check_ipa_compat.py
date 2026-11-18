#!/usr/bin/env python3
"""Screen IPAs for oracle compatibility without fully extracting them.

  1. DTSDKName <= 3.1.3.  imgtools/install-ipa.sh (macOS/USB install path)
     treats this as a hard gate. MEASURED FALSE on this project's own oracle
     (offline NAND injection, no USB/lockdown involved): MGST v2.3.0
     (DTSDKName=iphoneos3.2) launches, renders and takes touch input
     identically to a build reporting iphoneos2.0 — see LOG.md 2026-09-28
     "STEP 2 DONE". This binary links no 3.2-only API; the "TOO NEW" verdict
     below is a WARNING worth reading, not proof the IPA cannot run. Confirm
     with a real boot before ruling a version out.
  2. cryptid == 0.  This one IS a hard gate, unrelated to the above: a
     FairPlay-encrypted payload installs and then fails its code-directory
     hash on the first __TEXT page, offline injection or not.

Both are read straight out of the zip, so a 260 MB IPA costs a couple of
seconds rather than a full extraction.
"""
import plistlib
import struct
import sys
import zipfile
from pathlib import Path

DEVICE_OS = (3, 1, 3)
LC_ENCRYPTION_INFO = 0x21


def ver_tuple(s):
    out = []
    for part in str(s).split("."):
        digits = "".join(c for c in part if c.isdigit())
        out.append(int(digits) if digits else 0)
    while len(out) < 3:
        out.append(0)
    return tuple(out[:3])


def read_cryptid(data):
    """cryptid from a thin 32-bit Mach-O, or from the first arch of a FAT."""
    if len(data) < 28:
        return None
    magic = struct.unpack_from(">I", data, 0)[0]
    off = 0
    if magic in (0xCAFEBABE, 0xBEBAFECA):          # FAT: take first slice
        nfat = struct.unpack_from(">I", data, 4)[0]
        if nfat < 1:
            return None
        off = struct.unpack_from(">I", data, 8 + 8)[0]
        if off + 28 > len(data):
            return None
        magic = struct.unpack_from("<I", data, off)[0]

    little = struct.unpack_from("<I", data, off)[0] == 0xFEEDFACE
    if not little:
        return None
    ncmds = struct.unpack_from("<I", data, off + 16)[0]
    p = off + 28
    for _ in range(ncmds):
        if p + 8 > len(data):
            return None
        cmd, size = struct.unpack_from("<II", data, p)
        if cmd == LC_ENCRYPTION_INFO:
            return struct.unpack_from("<I", data, p + 16)[0]
        if size == 0:
            return None
        p += size
    return None      # no LC_ENCRYPTION_INFO at all == not FairPlay


def inspect(path):
    r = {"file": path.name, "size": path.stat().st_size}
    try:
        z = zipfile.ZipFile(path)
    except Exception as e:
        r["error"] = f"not a zip: {e}"
        return r

    names = z.namelist()
    plist_name = next(
        (n for n in names
         if n.count("/") == 2 and n.endswith("Payload/") is False
         and n.endswith("/Info.plist") and n.startswith("Payload/")),
        None)
    if not plist_name:
        plist_name = next((n for n in names if n.endswith("/Info.plist")), None)
    if not plist_name:
        r["error"] = "no Info.plist"
        return r

    try:
        pl = plistlib.loads(z.read(plist_name))
    except Exception as e:
        r["error"] = f"plist parse: {e}"
        return r

    r["bundle"] = pl.get("CFBundleIdentifier")
    r["version"] = pl.get("CFBundleVersion")
    r["sdk"] = pl.get("DTSDKName") or pl.get("DTPlatformVersion")
    r["minos"] = pl.get("MinimumOSVersion")
    r["family"] = pl.get("UIDeviceFamily")

    exe = pl.get("CFBundleExecutable")
    appdir = plist_name.rsplit("/", 1)[0]
    r["exe"] = exe
    bin_name = f"{appdir}/{exe}" if exe else None
    if bin_name and bin_name in names:
        # Header + load commands only; no need for the whole binary.
        with z.open(bin_name) as f:
            head = f.read(200000)
        r["cryptid"] = read_cryptid(head)
    else:
        r["cryptid"] = None
        r["error"] = f"executable {bin_name} not in archive"

    sdkraw = str(r["sdk"] or "")
    sdknum = sdkraw.replace("iphoneos", "").replace("iphonesimulator", "")
    r["sdk_ok"] = bool(sdknum) and ver_tuple(sdknum) <= DEVICE_OS
    r["crypt_ok"] = (r["cryptid"] == 0) or (r["cryptid"] is None)
    # cryptid is the only proven hard gate (see module docstring). An SDK
    # newer than the device is downgraded to a warning, not BLOCKED — measured
    # false for MGST v2.3.0 via offline NAND injection, LOG 2026-09-28.
    r["verdict"] = "RUNS" if r["crypt_ok"] else "BLOCKED (encrypted)"
    if r["crypt_ok"] and not r["sdk_ok"]:
        r["verdict"] = "RUNS (SDK newer than device -- verify by booting)"
    return r


def main():
    paths = []
    for a in sys.argv[1:]:
        p = Path(a)
        paths.extend(sorted(p.rglob("*.ipa")) if p.is_dir() else [p])
    if not paths:
        sys.exit("usage: check_ipa_compat.py <ipa-or-dir> ...")

    print(f"device: iOS {'.'.join(map(str, DEVICE_OS))}  "
          f"(gate = DTSDKName <= device AND cryptid == 0)\n")
    rows = [inspect(p) for p in paths]
    for r in rows:
        print(f"{r['file']}")
        if "error" in r and "bundle" not in r:
            print(f"   ERROR: {r['error']}")
            continue
        print(f"   version {r.get('version')}   "
              f"size {r['size']/2**20:.0f} MiB   family {r.get('family')}")
        print(f"   DTSDKName   {str(r.get('sdk')):<14} "
              f"{'OK' if r['sdk_ok'] else 'TOO NEW'}")
        cid = r.get("cryptid")
        cstr = "absent (not FairPlay)" if cid is None else str(cid)
        print(f"   cryptid     {cstr:<14} "
              f"{'OK' if r['crypt_ok'] else 'ENCRYPTED - unusable'}")
        print(f"   MinimumOS   {str(r.get('minos')):<14} "
              f"(informational only - not the filter)")
        print(f"   => {r['verdict']}\n")

    ok = [r for r in rows if r.get("verdict", "").startswith("RUNS")]
    print(f"{len(ok)}/{len(rows)} can run on the oracle")
    for r in ok:
        print(f"   {r['file']}  (v{r.get('version')}, SDK {r.get('sdk')})")


if __name__ == "__main__":
    main()
