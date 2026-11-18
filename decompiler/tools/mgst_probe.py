#!/usr/bin/env python3
"""Live memory probe for MGST running on the QEMU iPod touch oracle.

The dynamic half of the RE setup: Ghidra tells you what the code *should* do,
this tells you what it *is* doing, addressed in the SAME address space so the
two are directly comparable. A Ghidra address pasted here is the address read.

    mgst_probe.py context                 # are we looking at MGST right now?
    mgst_probe.py read 0x60b54 64         # hexdump a Ghidra VA
    mgst_probe.py sym getDrawPosY         # symbol -> VA, and is it resident?
    mgst_probe.py coverage                # which functions have EXECUTED
    mgst_probe.py watch 0x69000 64        # poll a VA and show what changes

HOW THE ADDRESS TRANSLATION WORKS, and why it is trustworthy
------------------------------------------------------------
QEMU's `gva2gpa` walks the guest's own ARM page tables, so a guest virtual
address becomes a physical one and `pmemsave` reads it out. No USB, no
debugger, no libimobiledevice - which matters here because iOS 3.1.3's
lockdownd speaks SSLv3 and OpenSSL 3.x removed it, so the entire
libimobiledevice path is dead on this host (see LOG 2026-09-22).

iOS 3.1.3 predates ASLR (introduced in 4.3), so a Ghidra VA is the runtime VA
with no slide to subtract - PROVIDED Ghidra and the guest are looking at the
SAME BINARY. They are not automatically: MGST's segment layout differs per
version (v2.3.0's __TEXT is 0x68000 bytes, v2.1.0's is 0x6d000, v1.0.0's is
0x54000 - measured, see LOG 2026-09-27 AUDIT finding A). A whole session's
worth of "coverage" and "sym" output was silently wrong on 2026-09-22/23
because this file hardcoded v2.1.0's segment sizes while `function_map.csv`
(from `tools/build_function_map.py`, which reads `work/extracted` = v2.3.0)
describes v2.3.0's addresses. **Fixed below: the segment layout is read from
whichever binary MGST_REF_EXE names, every run, instead of hardcoded.**

DEFAULT VERSION: v2.3.0 (`oracle/state/ipa-extract-v230/`). This is the actual
port target, it is what Ghidra/`function_map.csv` already describe, and as of
2026-09-28 it is confirmed to launch, render and take input on the oracle
(NAND `oracle/firmware/nand-mgst-v230`) - so the default here needs no
translation against Ghidra's addresses. Point `MGST_REF_EXE` at
`ipa-extract/` (v2.1.0, NAND `nand-mgst-v210`) or `ipa-extract-v1/` (v1.0.0,
NAND `nand-mgst-v1`) for historical/comparison work on those NANDs - and pass
the matching `--funcmap` (see `tools/build_function_map.py --exe ... --out
...` to generate one; only v2.3.0's is checked in as the default
`function_map.csv`, since it's the one that stays in sync with the Ghidra
project).

THREE CAVEATS, each of which will bite silently if ignored
-----------------------------------------------------------
1. `gva2gpa` resolves against the CURRENT CPU context (TTBR0 on ARM). That
   still points at the last-active *user* process even while the CPU sits in
   the kernel - which is most of the time on an idle device, and is why this
   works at all. But if another app becomes foreground, these VAs silently
   resolve into THAT process instead, and you get plausible garbage. Every
   read here is therefore gated on `check_context()`, which verifies the
   Mach-O header of MGSTUS is at VA 0x1000. Do not remove that check.

2. "Unmapped" does NOT mean "does not exist". iOS demand-pages the executable,
   so a page reads Unmapped until the code on it has actually run. That is a
   feature: it is exactly what makes `coverage` work.

3. A read is not atomic with the guest. Use --freeze to `stop` the VM for the
   duration and `cont` afterwards when you need a consistent snapshot of a
   structure larger than a word.
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "oracle", "qemu-ios", "imgtools"))
sys.path.insert(0, HERE)
from itqmp import QMP  # noqa: E402
from macho import MachO  # noqa: E402

QMP_SOCK = os.environ.get("MGST_QMP", "/tmp/mgst-ipod.sock")

# v2.3.0 is the confirmed-runnable port target as of 2026-09-28 and what
# function_map.csv/Ghidra already describe - see the module docstring.
DEFAULT_REF_EXE = os.path.join(
    PROJECT, "oracle", "state", "ipa-extract-v230",
    "Payload", "MGSTUS.app", "MGSTUS")
DEFAULT_FUNCMAP = os.path.join(PROJECT, "analysis", "symbols", "function_map.csv")

PAGE = 0x1000


def _ref_exe_path():
    exe = os.environ.get("MGST_REF_EXE") or DEFAULT_REF_EXE
    if not os.path.exists(exe):
        sys.exit("MGST_REF_EXE not found: %s\n"
                  "  (extract the IPA first, or set MGST_REF_EXE to point at "
                  "a MGSTUS binary)" % exe)
    return exe


def _mgst_header(n=32):
    with open(_ref_exe_path(), "rb") as f:
        return f.read(n)


def _text_data_segments():
    """(TEXT_VA, TEXT_SIZE, DATA_VA, DATA_VMSIZE) read from MGST_REF_EXE's own
    load commands - NOT hardcoded, because they differ per version (see module
    docstring). Getting this wrong doesn't error; it silently walks the wrong
    address range and produces plausible-looking nonsense, which is exactly
    what happened here once already."""
    m = MachO(_ref_exe_path())
    segs = {name: (vmaddr, vmsize) for name, vmaddr, vmsize, *_ in m.segments}
    if "__TEXT" not in segs or "__DATA" not in segs:
        sys.exit("MGST_REF_EXE has no __TEXT/__DATA segment - not a MGSTUS binary?")
    return segs["__TEXT"] + segs["__DATA"]


TEXT_VA, TEXT_SIZE, DATA_VA, DATA_VMSIZE = _text_data_segments()


class Probe:
    def __init__(self, sock=QMP_SOCK, freeze=False, q=None):
        # Accept an existing connection. QEMU's QMP socket serves ONE client at
        # a time, so a caller that already holds a connection (mgst_launch.py,
        # driving taps) must hand it over rather than open a second one - the
        # second connect simply blocks until the QMP read timeout fires, which
        # surfaces as an unrelated-looking TimeoutError deep in itqmp.
        self.q = q if q is not None else QMP(sock)
        self.freeze = freeze

    def hmp(self, cmd):
        return self.q.cmd("human-monitor-command", **{"command-line": cmd})

    def __enter__(self):
        if self.freeze:
            self.q.cmd("stop")
        return self

    def __exit__(self, *exc):
        if self.freeze:
            try:
                self.q.cmd("cont")
            except Exception:
                pass

    # ---------------------------------------------------------------- memory
    def va2pa(self, va):
        """Guest virtual -> guest physical, or None if the page is not resident."""
        out = self.hmp("gva2gpa %s" % hex(va))
        m = re.search(r"gpa:\s*(0x[0-9a-fA-F]+)", out)
        return int(m.group(1), 16) if m else None

    def read_phys(self, pa, size):
        tmp = tempfile.mktemp(prefix="mgstprobe.", suffix=".bin")
        try:
            self.q.cmd("pmemsave", val=pa, size=size, filename=tmp)
            with open(tmp, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def read_va(self, va, size):
        """Read `size` bytes at a guest VA, walking page by page.

        Returns bytes, with any non-resident page rendered as None in the gap
        map rather than silently zero-filled - a page that simply has not been
        paged in is not the same thing as a page of zeros, and conflating them
        is how you "discover" a global that is actually just cold.
        """
        out = bytearray()
        gaps = []
        off = 0
        while off < size:
            page_va = (va + off) & ~(PAGE - 1)
            in_page = (va + off) - page_va
            n = min(PAGE - in_page, size - off)
            pa = self.va2pa(page_va)
            if pa is None:
                gaps.append((va + off, n))
                out += b"\x00" * n
            else:
                out += self.read_phys(pa + in_page, n)
            off += n
        return bytes(out), gaps

    # --------------------------------------------------------------- context
    def check_context(self):
        want = _mgst_header(32)
        pa = self.va2pa(TEXT_VA)
        if pa is None:
            return False, "VA 0x1000 is unmapped - no user process mapped here"
        hdr = self.read_phys(pa, 32)
        if hdr[:4] != b"\xce\xfa\xed\xfe":
            return False, "no Mach-O magic at VA 0x1000 (got %s)" % hdr[:4].hex()
        if hdr != want:
            import struct
            gn, gs = struct.unpack_from("<II", hdr, 16)
            wn, ws = struct.unpack_from("<II", want, 16)
            return False, ("a Mach-O is mapped but it is NOT MGSTUS "
                           "(ncmds=%#x sizeofcmds=%#x; MGSTUS is %#x/%#x) - "
                           "TTBR0 points at another process right now"
                           % (gn, gs, wn, ws))
        return True, "MGSTUS is the current address space (32-byte header matches the file)"

    def wait_for_context(self, tries=60, delay=0.25):
        """Poll until MGST is the scheduled process. Returns (ok, msg, tries_used).

        MGST only holds TTBR0 while it is actually running, so catching it is a
        sampling problem: poll, and touch the screen to make it run if needed.
        """
        for i in range(tries):
            ok, msg = self.check_context()
            if ok:
                return True, msg, i + 1
            time.sleep(delay)
        return False, msg, tries

    def resident_pages(self, start, size):
        res = []
        for va in range(start, start + size, PAGE):
            if self.va2pa(va) is not None:
                res.append(va)
        return res


def load_symbols():
    """[(va, source_file, name)] sorted by va, from the recovered symbol table.

    MGST_FUNCMAP overrides the default (function_map.csv, v2.3.0) - set it
    alongside MGST_REF_EXE when probing a different version, or these
    addresses silently belong to the wrong binary (see module docstring)."""
    funcmap = os.environ.get("MGST_FUNCMAP") or DEFAULT_FUNCMAP
    syms = []
    with open(funcmap, newline="") as f:
        for row in csv.DictReader(f):
            syms.append((int(row["address"], 16), row["source_file"], row["function"]))
    syms.sort()
    return syms


def demangle(names):
    if not shutil.which("c++filt"):
        return {n: n for n in names}
    p = subprocess.run(["c++filt"], input="\n".join(names), capture_output=True, text=True)
    return dict(zip(names, p.stdout.splitlines())) if p.returncode == 0 else {n: n for n in names}


def hexdump(data, base, gaps):
    gapset = set()
    for gva, n in gaps:
        for a in range(gva, gva + n):
            gapset.add(a)
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        addr = base + i
        hexs, asc = [], []
        for j, b in enumerate(chunk):
            if addr + j in gapset:
                hexs.append("--"); asc.append("?")
            else:
                hexs.append("%02x" % b)
                asc.append(chr(b) if 32 <= b < 127 else ".")
        print("  %08x  %-47s  %s" % (addr, " ".join(hexs), "".join(asc)))


def cmd_context(p, a):
    ok, msg = p.check_context()
    print(("OK   " if ok else "FAIL ") + msg)
    return 0 if ok else 1


def cmd_read(p, a):
    ok, msg = p.check_context()
    if not ok:
        sys.exit("refusing to read: " + msg)
    data, gaps = p.read_va(a.va, a.size)
    hexdump(data, a.va, gaps)
    if gaps:
        print("  note: %d byte(s) lie on non-resident pages, shown as '--'"
              % sum(n for _, n in gaps))


def cmd_sym(p, a):
    syms = load_symbols()
    dem = demangle([s[2] for s in syms])
    pat = a.name.lower()
    hits = [s for s in syms if pat in s[2].lower() or pat in dem.get(s[2], "").lower()]
    if not hits:
        sys.exit("no symbol matching %r" % a.name)
    ok, _ = p.check_context()
    for va, src, name in hits[:a.limit]:
        state = "n/a"
        if ok:
            state = "RESIDENT (executed)" if p.va2pa(va & ~(PAGE - 1)) else "cold (never run)"
        print("  %#08x  %-28s  %s" % (va, src, dem.get(name, name)))
        print("            %s" % state)
    if len(hits) > a.limit:
        print("  ... %d more" % (len(hits) - a.limit))


def cmd_coverage(p, a):
    """Which recovered functions live on pages the guest has actually paged in.

    Demand paging makes this a real, if coarse, execution trace: a page is
    faulted in only when something on it runs. Resolution is one 4 KB page, so
    a hit means "a function on this page ran", not necessarily this one.
    """
    ok, msg = p.check_context()
    if not ok:
        sys.exit("refusing to sample: " + msg)
    res = set(p.resident_pages(TEXT_VA, TEXT_SIZE))
    syms = load_symbols()
    dem = demangle([s[2] for s in syms])
    hot = [(va, src, name) for va, src, name in syms if (va & ~(PAGE - 1)) in res]
    total_pages = TEXT_SIZE // PAGE
    print("__TEXT pages resident: %d/%d (%.1f%%)"
          % (len(res), total_pages, 100.0 * len(res) / total_pages))
    print("functions on resident pages: %d/%d\n" % (len(hot), len(syms)))
    by_src = {}
    for va, src, name in hot:
        by_src.setdefault(src, []).append((va, name))
    for src in sorted(by_src, key=lambda s: -len(by_src[s])):
        print("  %s  (%d)" % (src, len(by_src[src])))
        if a.verbose:
            for va, name in sorted(by_src[src]):
                print("      %#08x  %s" % (va, dem.get(name, name)))


def cmd_watch(p, a):
    ok, msg = p.check_context()
    if not ok:
        sys.exit("refusing to watch: " + msg)
    prev = None
    for i in range(a.count):
        data, gaps = p.read_va(a.va, a.size)
        if prev is None:
            print("[%02d] baseline" % i)
            hexdump(data, a.va, gaps)
        elif data != prev:
            diffs = [j for j in range(len(data)) if data[j] != prev[j]]
            print("[%02d] %d byte(s) changed at +%s"
                  % (i, len(diffs), ",".join(hex(d) for d in diffs[:12])))
            hexdump(data, a.va, gaps)
        else:
            print("[%02d] unchanged" % i)
        prev = data
        time.sleep(a.interval)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--freeze", action="store_true",
                    help="stop the VM during the read for an atomic snapshot")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("context").set_defaults(fn=cmd_context)

    r = sub.add_parser("read"); r.set_defaults(fn=cmd_read)
    r.add_argument("va", type=lambda x: int(x, 0))
    r.add_argument("size", type=lambda x: int(x, 0), nargs="?", default=64)

    s = sub.add_parser("sym"); s.set_defaults(fn=cmd_sym)
    s.add_argument("name"); s.add_argument("--limit", type=int, default=20)

    c = sub.add_parser("coverage"); c.set_defaults(fn=cmd_coverage)
    c.add_argument("-v", "--verbose", action="store_true")

    w = sub.add_parser("watch"); w.set_defaults(fn=cmd_watch)
    w.add_argument("va", type=lambda x: int(x, 0))
    w.add_argument("size", type=lambda x: int(x, 0), nargs="?", default=32)
    w.add_argument("--interval", type=float, default=1.0)
    w.add_argument("--count", type=int, default=10)

    a = ap.parse_args()
    with Probe(freeze=a.freeze) as p:
        sys.exit(a.fn(p, a) or 0)


if __name__ == "__main__":
    main()
