#!/usr/bin/env python3
"""
Step 7' differential test: does each recompiled function behave exactly like
the original, on REAL game state?

    tools/mgst_difftest.py [--seconds N] [--samples K] [--batch B] [--only ADDR ...]

Needs: the oracle running with --gdb (MGST in the foreground, ideally being
driven by tools/oracle_drive.py), and tools/mgst_recompile.py output
(recovered/compile/fn/<addr>.o).

For each function entry hit INSIDE MGSTUS (identity: Mach-O header at 0x1000)
the guest stays paused while two Unicorn runs start from the identical state:
  A  the original code at its original address
  B  the recompiled code (linked at 0x300000, every reference -> original addr)
Memory is faulted in page by page from the paused guest, so both runs see the
real heap/objects/ObjC runtime. Pure code executes for real (ObjC runtime,
Foundation, libc, soft-float helpers). Calls through import stubs to
rendering/audio/OS services (gl*, al*, Audio*, CG*, UI*, NSLog, clocks) are the
boundary: recorded with their arguments and returned 0 in both runs.

PASS    same r0 (and r1 for 64-bit returns), same bytes written everywhere
        except the callee's own stack frames, same boundary-call sequence
FAIL    any difference (details kept)
UNTESTABLE  syscall / instruction limit / unmapped memory in the original run

Results: recovered/compile/difftest_results.jsonl, difftest_report.md
"""
import argparse
import collections
import binascii
import json
import hashlib
import os
import re
import socket
import struct
import subprocess
import sys
import time

from unicorn import (Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_ARM, UC_HOOK_MEM_UNMAPPED,
                     UC_HOOK_MEM_WRITE, UC_HOOK_CODE, UC_HOOK_INTR, UC_PROT_ALL)
from unicorn.arm_const import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDIR = os.environ.get("MGST_CDIR") or os.path.join(ROOT, "recovered/compile")   # MGST_CDIR: test another export (rebuild check)
FDIR = os.path.join(CDIR, "fn")
REF_EXE = os.path.join(ROOT, "work/extracted/Payload/MGSTUS.app/MGSTUS")
BASE = 0x00300000
SENTINEL = 0x7ff00000
DYLD_LO, DYLD_HI = 0x69000, 0x693e0      # __DATA,__dyld + __nl_symbol_ptr + __la_symbol_ptr
DYLD_IMG_LO, DYLD_IMG_HI = 0x2fe00000, 0x2fe40000   # dyld's own image (binding state)
PAGE = 0x1000
MAX_INSNS = 3_000_000
BOUNDARY = re.compile(r"^_(gl|al|alc|Audio|CG|UI|NSLog|NSSearchPath|mach_absolute_time|CFAbsoluteTime|CFRunLoop|"
                      r"CFURLCreate|CFRelease|_Unwind|objc_begin_catch|objc_end_catch)")
APP_CALLEES = {}                   # addr -> (name, argument words); init_boundary()
_COVER = None                      # fn entry -> frozenset(instruction addresses); test coverage
# ___switchu8/8/16: computed BRANCHES into case code (they never return to
# LR), so never tracked as callees nor stubbed by the callee boundary
SWITCH_HELPERS = {0x5a5b4, 0x5a5cc, 0x5a5e4}


def cover_set(entry):
    """The tested function's own instructions (recovered/compile/function_insns.tsv,
    tools/ghidra/CoverageAudit.java), for test-coverage recording."""
    global _COVER
    if _COVER is None:
        _COVER = {}
        path = os.path.join(CDIR, "function_insns.tsv")
        if os.path.exists(path):
            tmp = collections.defaultdict(list)
            for l in open(path):
                p = l.rstrip("\n").split("\t")
                if p[0] != "function":
                    tmp[int(p[0], 16)].append(int(p[1], 16))
            _COVER = {k: frozenset(v) for k, v in tmp.items()}
    return _COVER.get(entry & ~1)


def cov_encode(addrs, base):
    """Covered instruction addresses -> compact 'off-off,off' (hex offsets from base)."""
    out, run = [], None
    for a in sorted(addrs):
        o = a - base
        if run and o - run[1] <= 4:
            run[1] = o
        else:
            if run:
                out.append(run)
            run = [o, o]
    if run:
        out.append(run)
    return ",".join("%x" % a if a == b else "%x-%x" % (a, b) for a, b in out)
PLACEHOLDER_LO, PLACEHOLDER_HI = 0x100000, 0x40000000   # heap + shared-library data (harness 7)
MSG_STUBS = ("_objc_msgSend", "_objc_msgSendSuper2", "_objc_msgSend_stret")
IMAGE_DATA_LO, IMAGE_DATA_HI = 0x69000, 0x89000      # MGSTUS __DATA (its class structs)
REGS = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5,
        UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11,
        UC_ARM_REG_R12, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC]


# ---------------------------------------------------------------- gdb RSP
class RSP:
    def __init__(self, host="127.0.0.1", port=1234):
        self.s = socket.create_connection((host, port), timeout=30)
        self.buf = b""

    def _recv_packet(self, timeout=None):
        self.s.settimeout(timeout)
        while True:
            i = self.buf.find(b"$")
            if i >= 0:
                j = self.buf.find(b"#", i)
                if j >= 0 and len(self.buf) >= j + 3:
                    pkt = self.buf[i + 1:j]
                    self.buf = self.buf[j + 3:]
                    self.s.sendall(b"+")
                    return pkt.decode("latin-1")
            chunk = self.s.recv(65536)
            if not chunk:
                raise ConnectionError("gdbstub closed")
            self.buf += chunk

    def cmd(self, data, timeout=30):
        pkt = data.encode("latin-1")
        cs = sum(pkt) & 0xff
        self.s.sendall(b"$" + pkt + b"#%02x" % cs)
        return self._recv_packet(timeout)

    def read(self, addr, n):
        out = b""
        while n:
            k = min(n, 0x800)
            r = self.cmd("m%x,%x" % (addr, k))
            if r.startswith("E") or not r:
                raise MemoryError("m %x" % addr)
            out += binascii.unhexlify(r)
            addr += k
            n -= k
        return out

    def regs(self):
        r = self.cmd("g")
        vals = [struct.unpack("<I", binascii.unhexlify(r[i * 8:i * 8 + 8]))[0] for i in range(16)]
        return vals

    def cont_until_stop(self, timeout):
        self.s.sendall(b"$c#63")
        try:
            return self._recv_packet(timeout)
        except socket.timeout:
            self.s.sendall(b"\x03")
            return self._recv_packet(30)


# ---------------------------------------------------------------- linking
def stub_map():
    out = {}
    for l in open(os.path.join(ROOT, "analysis/symbols/stubs_v230.tsv")):
        if l.startswith("addr"):
            continue
        a, n = l.split()
        out[int(a, 16)] = n
    return out


def link(fn):
    """Link recovered/compile/fn/<addr>.o at BASE; every undefined symbol ->
    original address (.thumb_set for Thumb functions, .set otherwise)."""
    base = os.path.join(FDIR, fn["addr"])
    if not os.path.exists(base + ".o"):
        return None
    syms = SYMS
    nm = subprocess.run(["arm-none-eabi-nm", "-u", base + ".o"], capture_output=True, text=True).stdout.split()
    und = [x for x in nm if x != "U"]
    lines = [".syntax unified"]
    missing = []
    for u in und:
        v = syms.get(u)
        if v is None and u in LIBMAP:
            v = LIBMAP[u]
        if v is None:
            ma = re.match(r"^_?(?:[a-z]{0,3}Ram|DAT|LAB|UNK)_?([0-9a-f]{8})$", u)
            if ma:
                v = (int(ma.group(1), 16), "data")
        if v is None:
            missing.append(u)
            continue
        addr, kind = v
        lines.append(".globl %s" % u)
        if kind == "func_thumb":
            lines.append(".type %s, %%function" % u)
            lines.append(".thumb_set %s, 0x%x" % (u, addr))
        elif kind == "func_arm":
            # ARM-mode target (dyld stubs, switch helpers): typed as a function so
            # the linker turns Thumb `bl` into `blx` (interworking)
            lines.append(".type %s, %%function" % u)
            lines.append(".set %s, 0x%x" % (u, addr))
        else:
            lines.append(".set %s, 0x%x" % (u, addr))
    if missing and not all(m.startswith("__aeabi") or m.startswith("__") for m in missing):
        return {"error": "unresolved: " + ",".join(missing[:5])}
    open(base + ".syms.s", "w").write("\n".join(lines) + "\n")
    subprocess.run(["clang", "--target=armv6-none-eabi", "-c", base + ".syms.s", "-o", base + ".syms.o"], check=True)
    # vfpshim.a before libgcc: clang's soft-float calls become ARM-mode VFP
    # instructions (device FPSCR semantics; tools/mgst_recompile.py VFP_SHIMS)
    shim = os.path.join(CDIR, "vfpshim.a")
    # -z muldefs: a libgcc member pulled in for a 64-bit conversion (no VFP
    # equivalent, e.g. __fixdfdi) also defines __floatunsidf etc.; the shim
    # (earlier on the command line) must win
    r = subprocess.run(["arm-none-eabi-ld", "-z", "muldefs", "-Ttext=0x%x" % BASE, "-e", "REC_" + fn["cname"],
                        "-o", base + ".elf", base + ".o", base + ".syms.o"] +
                       ([shim] if os.path.exists(shim) else []) + [LIBGCC],
                       capture_output=True, text=True)
    if r.returncode:
        return {"error": "ld: " + r.stderr.strip().splitlines()[-1][:160]}
    # ALL allocated sections: the ARM/Thumb interworking veneers the linker
    # adds for calls into the ARM-mode dyld stubs live in .glue_7/.glue_7t
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", base + ".elf", base + ".bin"], check=True)
    ent = subprocess.run(["arm-none-eabi-nm", base + ".elf"], capture_output=True, text=True).stdout
    m = re.search(r"^([0-9a-f]+) [Tt] REC_%s$" % re.escape(fn["cname"]), ent, re.M)
    if not m:
        return {"error": "entry symbol REC_%s not found" % fn["cname"]}
    code = open(base + ".bin", "rb").read()
    entry = int(m.group(1), 16) | 1
    # fingerprint of exactly what a test runs: result rows carry it, and the
    # ledger counts a row only while it matches the current build (stale
    # rows -> `mgst_snap.py refresh` re-tests just those functions)
    fp = hashlib.sha1(code + entry.to_bytes(4, "little")).hexdigest()[:16]
    open(base + ".fp", "w").write(fp + "\n")
    return {"entry": entry, "bin": code, "fp": fp}


# ---------------------------------------------------------------- emulation
_REF_IMG = None


def _ref_image():
    global _REF_IMG
    if _REF_IMG is None:
        _REF_IMG = open(REF_EXE, "rb").read(0x75000)
    return _REF_IMG


_FMT = re.compile(r"%(?:%|[-+ #0']*(\*|\d+)?(?:\.(\*|\d+))?(hh|h|ll|l|q|L|z|t|j)?([diouxXcCsSpP@eEfFgGaA]))")


def nslog_words(uc, cf, map_page):
    """Argument words NSLog consumes after its format (a CFString constant:
    isa, flags, cstr, length). doubles and ll/q take 2 words (APCS: 4-byte
    alignment), a `*` width/precision 1. Unknown format -> 3 (all of r1-r3)."""
    def rd(addr, n):
        try:
            for p in range((addr & ~(PAGE - 1)), addr + n, PAGE):
                if not map_page(p):
                    raise MemoryError(p)
            return bytes(uc.mem_read(addr, n))
        except (UcError, MemoryError):
            # constant CFStrings and their C strings are static image data:
            # a capture lacks the page when the real run never logged it
            if not 0x1000 <= addr < 0x76000:
                raise
            img = _ref_image()
            o = addr - 0x1000 if addr < 0x69000 else addr - 0x69000 + 0x68000
            return img[o:o + n]
    try:
        cstr, n = struct.unpack("<II", rd(cf + 8, 8))
        fmt = rd(cstr, min(n, 512)).decode("latin-1")
    except (UcError, struct.error, MemoryError):
        return 3
    w = 0
    for m in _FMT.finditer(fmt):
        if m.group(0) == "%%":
            continue
        w += (m.group(1) == "*") + (m.group(2) == "*")
        conv, mod = m.group(4), m.group(3)
        w += 2 if conv in "eEfFgGaA" or mod in ("ll", "q") else 1
    return w


# --- deterministic OS model for the test world (PLAN 4b step 5, LOG 2026-10-08)
# A function that loads a resource (NSData/fopen/AudioFile...) reaches BSD
# system calls; without answers the test was "untestable". Both runs of a
# pair get IDENTICAL answers from this model, and every modelled call is
# appended to the boundary-call trace, so a recompiled function that makes
# different system calls (or the same ones with different arguments) still
# FAILS. Files are served read-only from the IPA payload (the app bundle);
# anything else (Documents/, unknown paths) is ENOENT. Anonymous mmap gets
# zero pages from a fixed, per-run bump allocator.
APP_DIR = os.path.join(ROOT, "work/extracted/Payload/MGSTUS.app")
OS_MMAP_BASE = 0x50000000
ENOENT, EBADF, EINVAL = 2, 9, 22
SYS_NAMES = {3: "read", 5: "open", 6: "close", 20: "getpid", 25: "geteuid", 73: "munmap", 75: "madvise",
             197: "mmap", 199: "lseek", 338: "stat64", 339: "fstat64", 340: "lstat64",
             396: "read_nocancel", 398: "open_nocancel", 399: "close_nocancel"}


class OSModel:
    def __init__(self, run):
        self.run = run
        self.fds = {}            # fd -> [host path, position, size]
        self.next_fd = 3
        self.brk = OS_MMAP_BASE

    def cstr(self, addr):
        out = b""
        while len(out) < 1024:
            page = addr & ~(PAGE - 1)
            if not self.run.map_page(page):
                raise MemoryError(page)
            chunk = bytes(self.run.uc.mem_read(addr, PAGE - (addr - page)))
            z = chunk.find(b"\0")
            if z >= 0:
                return out + chunk[:z]
            out += chunk
            addr = page + PAGE
        return out

    def host_path(self, guest):
        g = guest.decode("utf-8", "replace")
        k = g.find("MGSTUS.app/")
        if k < 0:
            return None
        rel = os.path.normpath(g[k + len("MGSTUS.app/"):])
        if rel.startswith(".."):
            return None
        h = os.path.join(APP_DIR, rel)
        return h if os.path.isfile(h) else None

    def write_guest(self, addr, data):
        for page in range(addr & ~(PAGE - 1), addr + len(data), PAGE):
            if not self.run.map_page(page):
                raise MemoryError(page)
        self.run.uc.mem_write(addr, data)
        lo, hi = self.run.entry_sp - 0x20000, self.run.entry_sp
        for i in range(len(data)):
            if not lo <= addr + i < hi:          # callee frames are private (as on_write)
                self.run.writes[addr + i] = None

    def zero_map(self, length):
        n = (length + PAGE - 1) & ~(PAGE - 1)
        base = self.brk
        self.brk += n + PAGE                   # guard page between regions
        for page in range(base, base + n, PAGE):
            self.run.pristine[page] = bytes(PAGE)
        return base

    def stat_buf(self, size):
        b = bytearray(108)
        struct.pack_into("<IHH", b, 0, 1, 0o100444, 1)           # dev, mode (regular, r--r--r--), nlink
        struct.pack_into("<Q", b, 60, size)                         # st_size
        struct.pack_into("<Q", b, 68, (size + 511) // 512)          # st_blocks
        struct.pack_into("<I", b, 76, 4096)                         # st_blksize
        return bytes(b)

    def call(self, num, a):
        """-> (ok, value) or None if not modelled."""
        if num in (5, 398):                                         # open
            h = self.host_path(self.cstr(a[0]))
            if h is None or (a[1] & 3) != 0:                       # not found, or not O_RDONLY
                return False, ENOENT
            fd = self.next_fd
            self.next_fd += 1
            self.fds[fd] = [h, 0, os.path.getsize(h)]
            return True, fd
        if num in (6, 399):
            return (True, 0) if self.fds.pop(a[0], None) else (False, EBADF)
        if num in (3, 396):                                         # read
            f = self.fds.get(a[0])
            if f is None:
                return False, EBADF
            with open(f[0], "rb") as fh:
                fh.seek(f[1])
                data = fh.read(a[2])
            if data:
                self.write_guest(a[1], data)
            f[1] += len(data)
            return True, len(data)
        if num == 199:                                              # lseek(fd, off64 lo/hi, whence)
            f = self.fds.get(a[0])
            if f is None:
                return False, EBADF
            off = a[1] | (a[2] << 32)
            off = off - (1 << 64) if off >> 63 else off
            base = {0: 0, 1: f[1], 2: f[2]}.get(a[3])
            if base is None or base + off < 0:
                return False, EINVAL
            f[1] = base + off
            return True, f[1] & 0xffffffff                         # (r1 = high word: 0 for our sizes)
        if num in (338, 340):                                       # stat64 / lstat64
            h = self.host_path(self.cstr(a[0]))
            if h is None:
                return False, ENOENT
            self.write_guest(a[1], self.stat_buf(os.path.getsize(h)))
            return True, 0
        if num == 339:                                              # fstat64
            f = self.fds.get(a[0])
            if f is None:
                return False, EBADF
            self.write_guest(a[1], self.stat_buf(f[2]))
            return True, 0
        if num == 197:                                              # mmap(addr, len, prot, flags, fd, off)
            length, flags, fd = a[1], a[3], a[4]
            if length == 0 or length > 64 << 20:
                return False, EINVAL
            if flags & 0x1000 or fd == 0xffffffff:                  # MAP_ANON
                return True, self.zero_map(length)
            f = self.fds.get(fd)
            if f is None:
                return False, EBADF
            base = self.zero_map(length)
            with open(f[0], "rb") as fh:
                fh.seek(a[5] | (a[6] << 32))
                data = fh.read(length)
            for i in range(0, len(data), PAGE):
                page = base + i
                self.run.pristine[page] = data[i:i + PAGE].ljust(PAGE, b"\0")
            return True, base
        if num in (73, 75):                                         # munmap / madvise
            return True, 0
        if num in (20, 25):                                         # getpid / geteuid
            return True, 501 if num == 25 else 100
        return None

_FW_WORDS = None


def fw_arg_words(sel):
    """Argument words (after self, _cmd) of a framework selector."""
    global _FW_WORDS
    if _FW_WORDS is None:
        _FW_WORDS = {}
        for l in open(os.path.join(ROOT, "analysis/objc/external_methods.tsv")):
            if l.startswith("#"):
                continue
            p = l.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            w = 0
            for t in [x for x in re.split(r",(?![^(]*\))", p[2]) if x]:
                if t in ("f8", "i8", "u8"):
                    w += 2
                elif t.startswith("struct(CGRect"):
                    w += 4
                elif t.startswith("struct(CGPoint") or t.startswith("struct(CGSize"):
                    w += 2
                elif t.startswith("struct("):
                    w += 2
                else:
                    w += 1
            _FW_WORDS[p[0]] = w
    if sel in _FW_WORDS:
        return _FW_WORDS[sel]
    return sel.count(":")



class Run:
    """One emulated call. tid/fpscr: the thread pointer (TPIDRURO - libSystem,
    objc and Foundation reach thread-local data through it; left 0 they fault
    at 0x44c/0x468/0x47c/0x70, which the 2026-09-30 report misread as stubbed
    services returning NULL) and the device FPSCR (measured: FZ+DN).
    poison: byte pattern written over the free stack below the entry SP of
    every mapped page, different per run, so a read of uninitialised stack
    shows up as a difference (PLAN 4b V4)."""
    def __init__(self, pristine, fetch, regs, entry, thumb, code=None, tid=None, fpscr=None, poison=None,
                 fw_boundary=False, callee_boundary=False, placeholder=False):
        self.pristine, self.fetch = pristine, fetch
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB if thumb else UC_MODE_ARM)
        self.mapped = set()
        self.writes = {}
        self.calls = []
        self.status = None
        self.insns = 0
        self.trail = []
        self.glarrays = {}
        self.entry_sp = regs[13]
        self.code = code
        uc = self.uc
        uc.mem_map(SENTINEL, PAGE, UC_PROT_ALL)
        if code:
            size = (len(code) + PAGE - 1) & ~(PAGE - 1)
            uc.mem_map(BASE, size, UC_PROT_ALL)
            uc.mem_write(BASE, code)
            for p in range(BASE, BASE + size, PAGE):
                self.mapped.add(p)
        for i, r in enumerate(REGS[:15]):
            uc.reg_write(r, regs[i])
        uc.reg_write(UC_ARM_REG_LR, SENTINEL | 1)
        # enable VFP (recompiled code uses VFPv2 directly; FPEXC.EN)
        try:
            uc.reg_write(UC_ARM_REG_C1_C0_2, uc.reg_read(UC_ARM_REG_C1_C0_2) | (0xf << 20))
            uc.reg_write(UC_ARM_REG_FPEXC, 0x40000000)
        except Exception:
            pass
        if tid is not None:
            uc.reg_write(UC_ARM_REG_C13_C0_3, tid)
        if fpscr is not None:
            uc.reg_write(UC_ARM_REG_FPSCR, fpscr)
        self.poison = poison
        uc.hook_add(UC_HOOK_MEM_UNMAPPED, self.on_unmapped)
        uc.hook_add(UC_HOOK_MEM_WRITE, self.on_write)
        uc.hook_add(UC_HOOK_CODE, self.on_code)
        uc.hook_add(UC_HOOK_INTR, self.on_intr)
        self.start = entry
        self.os = OSModel(self)
        self.fw_boundary = fw_boundary
        # callee boundary (harness 8): a SET of MGSTUS entries to stub (or True
        # = every proven/V0 callee, the harness-6 behaviour); the stack of
        # active MGSTUS callees is tracked so a stuck run names its culprit
        self.callee_boundary = callee_boundary
        self.track = callee_boundary is not False
        self.appstack = []
        self.culprit = None
        self.placeholder = placeholder
        self.placeholders = 0
        # test coverage: which of the tested function's own instructions the
        # ORIGINAL code executed (code is None = the original binary)
        self.cover = cover_set(entry) if code is None else None
        self.covered = set()

    def map_page(self, page):
        if page in self.mapped:
            return True
        data = self.pristine.get(page)
        if data is None:
            try:
                data = self.fetch(page)
            except MemoryError:
                # free stack below the entry SP: the recompiled frame may be
                # deeper than the original's (a page the capture never saw);
                # it is private to the run - poisoned, never a FAIL
                if self.poison is not None and self.entry_sp - 0x20000 <= page < self.entry_sp:
                    data = bytes(PAGE)
                elif self.placeholder and PLACEHOLDER_LO <= page < PLACEHOLDER_HI:
                    # harness 7: a heap/framework page the capture does not
                    # hold gets a deterministic pattern (each word = 0xDA000000
                    # | its address bits), identical in both runs; the
                    # comparison then decides on identical inputs
                    data = b"".join(struct.pack("<I", 0xDA000000 | ((page + 4 * i) & 0x00ffffff))
                                    for i in range(PAGE // 4))
                    self.placeholders += 1
                    self.pristine[page] = data
                else:
                    return False
            else:
                self.pristine[page] = data
        if self.poison is not None and page + PAGE > self.entry_sp - 0x20000 and page < self.entry_sp:
            lo = max(page, self.entry_sp - 0x20000) - page
            hi = min(page + PAGE, self.entry_sp) - page
            data = data[:lo] + bytes([self.poison]) * (hi - lo) + data[hi:]
        self.uc.mem_map(page, PAGE, UC_PROT_ALL)
        self.uc.mem_write(page, data)
        self.mapped.add(page)
        return True

    def on_unmapped(self, uc, access, addr, size, value, _):
        ok = self.map_page(addr & ~(PAGE - 1))
        if ok and (addr + size - 1) & ~(PAGE - 1) != addr & ~(PAGE - 1):
            ok = self.map_page((addr + size - 1) & ~(PAGE - 1))
        if not ok:
            self.status = "untestable: unmapped 0x%x (pc trail %s)" % (addr, " ".join("%x" % t for t in self.trail[-12:]))
        return ok

    def on_write(self, uc, access, addr, size, value, _):
        # callee stack frames (below the entry SP) are private to each run
        if self.entry_sp - 0x20000 <= addr < self.entry_sp:
            return
        for i in range(size):
            self.writes[addr + i] = None

    # --- framework boundary mode (harness 5, LOG 2026-10-09) ---------------
    def word(self, addr):
        if not self.map_page(addr & ~(PAGE - 1)):
            raise MemoryError(addr)
        return struct.unpack("<I", bytes(self.uc.mem_read(addr, 4)))[0]

    def framework_send(self, uc, name):
        """objc_msgSend* to a receiver whose class is NOT MGSTUS's (UIKit,
        Foundation, ...): record (selector, receiver class, argument words)
        and return 0, like the C boundary services. MGSTUS's own classes
        (class structs inside its image) and nil receivers run for real."""
        stret = name.endswith("_stret")
        r = [uc.reg_read(x) for x in REGS[:4]]
        recv, sel = (r[1], r[2]) if stret else (r[0], r[1])
        try:
            if name == "_objc_msgSendSuper2":
                cls = self.word(self.word(recv + 4) + 4)        # objc_super.class -> its superclass
            else:
                if recv == 0:
                    return False
                cls = self.word(recv)                           # isa (metaclass for class receivers)
            if IMAGE_DATA_LO <= cls < IMAGE_DATA_HI:
                return False                                    # MGST class: real dispatch
        except MemoryError:
            pass                                                # unreadable receiver: treat as framework
        try:
            selname = self.os.cstr(sel).decode("latin-1")
        except MemoryError:
            selname = "?"
        sp = uc.reg_read(UC_ARM_REG_SP)
        norm = lambda v: "stackptr" if sp - 0x40 <= v < self.entry_sp else v
        # exactly the argument words the selector takes (SDK signature, else
        # one per ':'); leftover r2/r3 values are not arguments
        nw = fw_arg_words(selname)
        words = (r[3:] if stret else r[2:]) + [None] * 8
        if nw > len(r) - (3 if stret else 2):
            try:
                words = (r[3:] if stret else r[2:]) + [self.word(sp + 4 * i) for i in range(nw)]
            except MemoryError:
                pass
        args = tuple(norm(v) if v is not None else "?" for v in words[:nw])
        self.calls.append(("msg[fw] " + selname, args, ()))
        uc.reg_write(UC_ARM_REG_R0, 0)
        uc.reg_write(UC_ARM_REG_R1, 0)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        return True

    # --- callee boundary mode (harness 6, LOG 2026-10-09) ------------------
    def app_call(self, uc, addr):
        """Entry of an MGSTUS function that is itself proven bit-identical or
        V0-audited (APP_CALLEES): record (function, its argument words) and
        return 0 instead of running it. Compositional: the caller's own body is
        compared given identical callee results; the callee has its own proof.
        Used only when a run is otherwise untestable (instruction limit, a
        callee stuck in framework/OS code)."""
        cname, nw = APP_CALLEES[addr]
        r = [uc.reg_read(x) for x in REGS[:4]]
        sp = uc.reg_read(UC_ARM_REG_SP)
        words = r[:min(nw, 4)]
        if nw > 4:
            try:
                words += list(struct.unpack("<%dI" % (nw - 4), uc.mem_read(sp, 4 * (nw - 4))))
            except UcError:
                words += ["?"]
        norm = lambda v: "stackptr" if isinstance(v, int) and sp - 0x40 <= v < self.entry_sp else v
        self.calls.append(("app " + cname, tuple(norm(v) for v in words), ()))
        uc.reg_write(UC_ARM_REG_R0, 0)
        uc.reg_write(UC_ARM_REG_R1, 0)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def import_call(self, uc, name):
        """An import the run got stuck in (harness 9): record its argument
        words (prototype) and return 0, like the boundary services."""
        nw = ARGWORDS.get(name, 4)
        r = [uc.reg_read(x) for x in REGS[:min(nw, 4)]]
        sp = uc.reg_read(UC_ARM_REG_SP)
        st = ()
        if nw > 4:
            try:
                st = struct.unpack("<%dI" % (nw - 4), uc.mem_read(sp, 4 * (nw - 4)))
            except UcError:
                st = ("?",)
        norm = lambda v: "stackptr" if isinstance(v, int) and sp - 0x40 <= v < self.entry_sp else v
        self.calls.append(("imp " + name, tuple(norm(x) for x in r), tuple(norm(x) for x in st)))
        uc.reg_write(UC_ARM_REG_R0, 0)
        uc.reg_write(UC_ARM_REG_R1, 0)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def on_code(self, uc, addr, size, _):
        self.insns += 1
        if self.cover is not None and addr in self.cover:
            self.covered.add(addr)
        self.trail.append(addr)
        if len(self.trail) > 40:
            del self.trail[0]
        if self.insns > MAX_INSNS:
            self.status = "untestable: instruction limit"
            uc.emu_stop()
            return
        if addr & ~1 == SENTINEL:
            uc.emu_stop()
            return
        if self.track:
            a1 = addr & ~1
            while self.appstack and a1 == self.appstack[-1][1]:
                self.appstack.pop()
            if a1 in APP_CALLEES and a1 != (self.start & ~1) and a1 not in SWITCH_HELPERS:
                cb = self.callee_boundary
                if cb is True or a1 in cb:
                    self.app_call(uc, a1)
                    return
                self.appstack.append((a1, uc.reg_read(UC_ARM_REG_LR) & ~1))
            # harness 9: imports executed for real (libc ...) are tracked too,
            # so a run stuck INSIDE an import names it ("imp:_fseek"); the
            # retry then stubs that import like the boundary services below
            nm = STUBS.get(a1)
            if nm and not BOUNDARY.match(nm) and nm not in MSG_STUBS:
                cb = self.callee_boundary
                if cb is not True and ("imp:" + nm) in cb:
                    self.import_call(uc, nm)
                    return
                self.appstack.append(("imp:" + nm, uc.reg_read(UC_ARM_REG_LR) & ~1))
        name = STUBS.get(addr & ~1)
        if name and self.fw_boundary and name in MSG_STUBS and self.framework_send(uc, name):
            return
        if name and BOUNDARY.match(name):
            # only the arguments the import actually takes (argument words from
            # its prototype; leftover r2/r3 values are not arguments)
            nw = ARGWORDS.get(name, 4)
            if name == "_NSLog":
                # variadic: the format string says how many words follow
                nw = 1 + nslog_words(uc, uc.reg_read(REGS[0]), self.map_page)
            r = [uc.reg_read(x) for x in REGS[:min(nw, 4)]]
            sp = uc.reg_read(UC_ARM_REG_SP)
            st = ()
            if nw > 4:
                try:
                    st = struct.unpack("<%dI" % (nw - 4), uc.mem_read(sp, 4 * (nw - 4)))
                except UcError:
                    st = ("?",)
            # pointers into the live stack: their address differs between the
            # two builds and the bytes behind them are layout-dependent, so
            # they compare as "a stack pointer"; GL client arrays are compared
            # by exactly the vertices glDrawArrays consumes (below)
            def norm(v):
                if isinstance(v, int) and sp - 0x40 <= v < self.entry_sp:
                    return "stackptr"
                return v
            if name in ("_glVertexPointer", "_glTexCoordPointer", "_glColorPointer"):
                self.glarrays[name] = (r[0], r[2], r[3])          # size, stride, ptr
            if name == "_glDrawArrays" and len(r) >= 3:
                first, count = r[1], r[2]
                data = []
                for k in sorted(self.glarrays):
                    size, stride, ptr = self.glarrays[k]
                    step = stride or size * 4
                    try:
                        data.append((k, bytes(uc.mem_read(ptr + first * step, count * step))))
                    except UcError:
                        data.append((k, None))
                self.calls.append((name, tuple(r), tuple(data)))
            else:
                self.calls.append((name, tuple(norm(x) for x in r), tuple(norm(x) for x in st)))
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_R1, 0)
            lr = uc.reg_read(UC_ARM_REG_LR)
            uc.reg_write(UC_ARM_REG_PC, lr)

    def on_intr(self, uc, intno, _):
        num = uc.reg_read(UC_ARM_REG_R12)
        num = num - (1 << 32) if num & 0x80000000 else num
        res = None
        if intno == 2 and num > 0:
            a = [uc.reg_read(r) for r in REGS[:7]]
            try:
                res = self.os.call(num, a)
            except MemoryError:
                res = None
        if res is None:
            self.status = "untestable: syscall (intr %d, r12=%d)" % (intno, num)
            uc.emu_stop()
            return
        ok, val = res
        self.calls.append(("sys_" + SYS_NAMES.get(num, str(num)), (ok, val if not ok else
                           ("mapped" if num == 197 else val)), ()))
        uc.reg_write(UC_ARM_REG_R0, val & 0xffffffff)
        if num == 199:
            uc.reg_write(UC_ARM_REG_R1, 0)
        cpsr = uc.reg_read(UC_ARM_REG_CPSR)
        uc.reg_write(UC_ARM_REG_CPSR, (cpsr | (1 << 29)) if not ok else (cpsr & ~(1 << 29)))

    def initial(self, addr):
        """Byte at addr before the run (None if the address was never mapped)."""
        page = addr & ~(PAGE - 1)
        data = self.pristine.get(page)
        if data is None:
            try:
                data = self.fetch(page)
            except MemoryError:
                return None
        return data[addr - page]

    def go(self):
        try:
            self.uc.emu_start(self.start, SENTINEL, count=MAX_INSNS + 10)
        except UcError as e:
            if not self.status:
                self.status = "error: %s at 0x%x" % (e, self.uc.reg_read(UC_ARM_REG_PC))
        if not self.status:
            self.status = "ok"
        if self.status != "ok" and self.appstack:
            self.culprit = self.appstack[-1][0]
        self.ret = (self.uc.reg_read(UC_ARM_REG_R0), self.uc.reg_read(UC_ARM_REG_R1))
        self.final = {}
        for a in self.writes:
            try:
                self.final[a] = bytes(self.uc.mem_read(a, 1))[0]
            except UcError:
                pass
        return self


# Harness version, recorded in every result row ("hv"). Bump it when a
# harness change can turn a verdict (NSLog arity, uninit-read re-check, ...):
# the ledger then uses, per function, only rows from its newest harness.
# 1 = rows before 2026-10-08 19:30 (no field), 2 = uninit-read re-check,
# 3 = OS model (files from the app bundle, mmap) instead of untestable syscalls,
# 4 = OS-model writes into callee frames private (as CPU writes),
# 5 = framework-boundary retry for untestable pairs (messages to non-MGST objects stubbed),
# 6 = callee-boundary retry (proven / V0 MGSTUS callees stubbed and recorded),
# 7 = placeholder-page retry (uncaptured heap/framework pages = deterministic pattern),
# 8 = selective callee boundary: only the callees that get stuck are stubbed,
# 9 = imports (libc ...) a run gets stuck in join the selective boundary.
HARNESS = 9


def _recomp_fpscr(fpscr):
    """MGST_RECOMP_FPSCR=ieee: run the RECOMPILED side with flush-to-zero and
    default-NaN cleared (FPSCR bits 24/25), i.e. the IEEE float mode of a port
    that does not emulate the device's FZ+DN (wasm, arm64 default). Measures
    which functions the missing FZ emulation changes on real states; never
    used for proofs (LOG 2026-10-11)."""
    if fpscr is not None and os.environ.get("MGST_RECOMP_FPSCR") == "ieee":
        return fpscr & ~((1 << 24) | (1 << 25))
    return fpscr


def run_compare(fn, pristine, fetch, regs, entry, thumb, L, tid=None, fpscr=None):
    """Original vs recompiled from one state -> (verdict, detail, run_a, run_b).
    The two runs poison the free stack differently (0xa5 / 0x5a) so that a
    read of uninitialised stack shows up. A difference caused ONLY by such a
    read, which the original binary makes too (e.g. objc_msgSend_stret to a
    nil receiver leaves the struct unwritten), is not a decompilation error:
    when a failing pair agrees under two common poison patterns, the verdict
    is pass with detail "uninit-read" (LOG 2026-10-08)."""
    def pair(pa, pb):
        ra = Run(dict(pristine), fetch, regs, entry, thumb, tid=tid, fpscr=fpscr, poison=pa).go()
        rb = Run(dict(pristine), fetch, regs, L["entry"], True, code=L["bin"], tid=tid,
                 fpscr=_recomp_fpscr(fpscr), poison=pb).go()
        return compare(fn, ra, rb), ra, rb
    (v, det), ra, rb = pair(0xa5, 0x5a)
    if v == "untestable":
        # stuck inside framework code (Mach IPC, framework allocator pages):
        # retry with messages to framework objects as the boundary
        def fpair(pa, pb):
            xa = Run(dict(pristine), fetch, regs, entry, thumb, tid=tid, fpscr=fpscr, poison=pa, fw_boundary=True).go()
            xb = Run(dict(pristine), fetch, regs, L["entry"], True, code=L["bin"], tid=tid, fpscr=fpscr, poison=pb,
                     fw_boundary=True).go()
            return compare(fn, xa, xb), xa, xb
        (v2, det2), xa, xb = fpair(0xa5, 0x5a)
        if v2 != "untestable":
            if v2 == "fail" and all(fpair(p, p)[0][0] == "pass" for p in (0xa5, 0x3c)):
                v2, det2 = "pass", "uninit-read: " + det2[:120]
            return v2, "fw-boundary: " + det2, xa, xb
        # still stuck (instruction limit, OS call inside a callee): proven /
        # V0-audited MGSTUS callees become the boundary too (harness 6)
        stubs = True
        if APP_CALLEES:
            def cpair(pa, pb, cb):
                ya = Run(dict(pristine), fetch, regs, entry, thumb, tid=tid, fpscr=fpscr, poison=pa,
                         fw_boundary=True, callee_boundary=cb).go()
                yb = Run(dict(pristine), fetch, regs, L["entry"], True, code=L["bin"], tid=tid, fpscr=fpscr,
                         poison=pb, fw_boundary=True, callee_boundary=cb).go()
                return compare(fn, ya, yb), ya, yb
            # harness 8: stub ONLY the callees that get stuck (innermost active
            # MGSTUS function at the fault), one at a time; every other callee
            # runs for real, so branches on its results are exercised (with
            # all callees stubbed to return 0 they were not - mutation test)
            sel = set()
            for _ in range(8):
                (v3, det3), ya, yb = cpair(0xa5, 0x5a, sel)
                cul = ya.culprit if ya.status != "ok" else yb.culprit
                if v3 != "untestable" or cul is None or cul in sel:
                    break
                sel.add(cul)
            stubs = sel
            if v3 == "untestable":
                (v3, det3), ya, yb = cpair(0xa5, 0x5a, True)       # harness-6 fallback: every callee
                stubs = True
            if v3 != "untestable":
                if v3 == "fail" and all(cpair(p, p, stubs)[0][0] == "pass" for p in (0xa5, 0x3c)):
                    v3, det3 = "pass", "uninit-read: " + det3[:120]
                tag = "callee-boundary(all)" if stubs is True else "callee-boundary(%s)" % ",".join(
                    c if isinstance(c, str) else "%x" % c for c in sorted(stubs, key=str))
                return v3, tag + ": " + det3, ya, yb
        # still stuck on memory the capture does not hold (framework data such
        # as an NSString constant of MediaPlayer, an uncaptured heap page):
        # placeholder pages, identical in both runs (harness 7)
        def ppair(pa, pb):
            za = Run(dict(pristine), fetch, regs, entry, thumb, tid=tid, fpscr=fpscr, poison=pa,
                     fw_boundary=True, callee_boundary=stubs if APP_CALLEES else False, placeholder=True).go()
            zb = Run(dict(pristine), fetch, regs, L["entry"], True, code=L["bin"], tid=tid, fpscr=fpscr,
                     poison=pb, fw_boundary=True, callee_boundary=stubs if APP_CALLEES else False, placeholder=True).go()
            return compare(fn, za, zb), za, zb
        (v4, det4), za, zb = ppair(0xa5, 0x5a)
        if v4 != "untestable":
            if v4 == "fail" and all(ppair(p, p)[0][0] == "pass" for p in (0xa5, 0x3c)):
                v4, det4 = "pass", "uninit-read: " + det4[:120]
            return v4, "placeholder-pages(%d): %s" % (za.placeholders, det4), za, zb
    if v == "fail":
        same = [pair(p, p)[0] for p in (0xa5, 0x3c)]
        if all(x[0] == "pass" for x in same):
            return "pass", "uninit-read: differs only through uninitialised stack the original reads too (%s)" % det[:120], ra, rb
    return v, det, ra, rb


def compare(fn, a, b):
    if not a.status == "ok":
        return "untestable", a.status
    if b.status != "ok":
        return "fail", "recompiled run: " + b.status
    diffs = []
    # compare only as many return bits as the declared return type has
    ret = re.match(r"^\s*(?:static\s+)?([\w\s\*]+?)\s*\b\w+\s*\(", fn["proto"].replace("__thiscall", ""))
    rt = ret.group(1).strip() if ret else "int"
    declared = OBJC_RET.get(int(fn["addr"], 16))
    if declared is not None:
        rt = {"v": "void", "f": "float", "d": "double", "c": "char", "C": "char", "B": "char", "s": "short",
              "S": "short", "q": "long long", "Q": "long long"}.get(declared, "int")
    if "__stret" in fn["proto"] or declared == "{":
        # struct returned through the hidden r0 pointer: the result is the
        # memory written there (compared below); r0 itself carries nothing
        rt, declared = "void", "v"
    ret_verified = declared is not None or not re.search(r"\b(int|undefined4)\b", rt) or "*" in rt
    if rt == "void":
        mask0, mask1 = 0, 0
    elif "*" in rt:
        mask0, mask1 = 0xffffffff, 0
    elif re.search(r"\b(double|longlong|ulonglong|long long|undefined8|uint64_t|int64_t|qword)\b", rt):
        mask0, mask1 = 0xffffffff, 0xffffffff
    elif re.search(r"\b(char|uchar|bool|byte|undefined1|_gbool)\b", rt):
        mask0, mask1 = 0xff, 0
    elif re.search(r"\b(short|ushort|word|undefined2)\b", rt):
        mask0, mask1 = 0xffff, 0
    else:
        mask0, mask1 = 0xffffffff, 0
    if (a.ret[0] ^ b.ret[0]) & mask0 or (a.ret[1] ^ b.ret[1]) & mask1:
        diffs.append("return (%s) r0/r1 %08x/%08x vs %08x/%08x" % ((rt,) + a.ret + b.ret))
    # dyld's own state is not program behaviour: lazy-binding writes to
    # __la_symbol_ptr / __dyld happen on the first call through a stub, and the
    # recompiled code reaches libgcc helpers directly
    keys = {k for k in set(a.final) | set(b.final)
            if not (DYLD_LO <= k < DYLD_HI) and not (DYLD_IMG_LO <= k < DYLD_IMG_HI)}
    # compare the RESULTING memory: a byte one run never wrote still holds
    # its initial value (a library routine may store and then restore a
    # global - a net no-op the other build never performs)
    def final(r, k):
        if k in r.final:
            return r.final[k]
        return r.initial(k)
    bad = [k for k in sorted(keys) if final(a, k) != final(b, k)]
    # a word holding an address inside the callee stack area on BOTH sides is
    # layout-dependent (the recompiled frame differs), like stack-pointer
    # arguments of boundary calls: equal for the comparison
    if bad:
        lo, hi = a.entry_sp - 0x20000, a.entry_sp
        def word(r, w):
            bs = [final(r, w + i) for i in range(4)]
            return None if None in bs else int.from_bytes(bytes(bs), "little")
        skip = set()
        for w in {k & ~3 for k in bad}:
            va, vb = word(a, w), word(b, w)
            if va is not None and vb is not None and lo <= va < hi and lo <= vb < hi:
                skip.update(range(w, w + 4))
        bad = [k for k in bad if k not in skip]
    if bad:
        diffs.append("%d memory bytes differ (first 0x%x: %s vs %s)" % (
            len(bad), bad[0], final(a, bad[0]), final(b, bad[0])))
    if a.calls != b.calls:
        i = next((k for k in range(min(len(a.calls), len(b.calls))) if a.calls[k] != b.calls[k]),
                 min(len(a.calls), len(b.calls)))
        show = lambda c: c if not isinstance(c, tuple) else tuple(
            ("stack", x[1].hex()[:32] if x[1] else None) if isinstance(x, tuple) and x and x[0] == "stack" else x for x in c)
        diffs.append("boundary calls differ at #%d of %d/%d: %s  vs  %s" % (
            i, len(a.calls), len(b.calls),
            (a.calls[i][0], show(a.calls[i][1]), show(a.calls[i][2])) if i < len(a.calls) else None,
            (b.calls[i][0], show(b.calls[i][1]), show(b.calls[i][2])) if i < len(b.calls) else None))
    if diffs and all(d.startswith("return") for d in diffs) and not ret_verified:
        return "return-unverified", "; ".join(diffs) + " (return type only inferred)"
    return ("pass", "") if not diffs else ("fail", "; ".join(diffs))


def init_boundary():
    """Load the boundary tables Run needs (STUBS, ARGWORDS); returns the
    decompiled functions by address. Shared with tools/mgst_snap.py."""
    global STUBS, ARGWORDS, APP_CALLEES
    STUBS = stub_map()
    ARGWORDS = {}
    APP_CALLEES = {}
    funcs = {}
    for l in open(os.path.join(CDIR, "functions.jsonl")):
        f = json.loads(l)
        if f.get("c") is not None:
            funcs[int(f["addr"], 16)] = f
        else:
            # import prototype -> number of 32-bit argument words
            m = re.search(r"\((.*)\)", f["proto"])
            words = 0
            if m and m.group(1).strip() not in ("", "void"):
                for prm in m.group(1).split(","):
                    prm = prm.strip()
                    if prm == "...":
                        words = max(words, 4)
                        continue
                    words += 2 if re.search(r"\b(double|longlong|long long|ulonglong|undefined8)\b", prm) and "*" not in prm else \
                        4 if "CGRect" in prm and "*" not in prm else 6 if "CGAffineTransform" in prm and "*" not in prm else 1
            ARGWORDS[f["name"]] = words
    # callee boundary (harness 6): functions the ledger has proven or V0-audited
    ok = set()
    st = os.path.join(ROOT, "analysis/verification/function_status.tsv")
    if os.path.exists(st):
        for l in open(st):
            p = l.rstrip("\n").split("\t")
            if p[0].startswith("0x") and len(p) > 5 and (p[4] == "pass" or p[5]):
                ok.add(int(p[0], 16))
    for a, f in funcs.items():
        if a in ok:
            APP_CALLEES[a] = (f["name"], proto_words(f["proto"]))
    return funcs


def proto_words(proto):
    """32-bit argument words of a C prototype (APCS: 64-bit values = 2 words,
    by-value CGRect = 4)."""
    m = re.search(r"\((.*)\)", proto)
    words = 0
    if m and m.group(1).strip() not in ("", "void"):
        for prm in m.group(1).split(","):
            prm = prm.strip()
            if prm == "...":
                words = max(words, 4)
                continue
            words += 2 if re.search(r"\b(double|longlong|long long|ulonglong|undefined8)\b", prm) and "*" not in prm else \
                4 if "CGRect" in prm and "*" not in prm else 6 if "CGAffineTransform" in prm and "*" not in prm else 1
    return words


def init_link():
    """Tables link() and compare() need (SYMS, LIBMAP, LIBGCC, OBJC_RET) plus
    init_boundary(); returns the decompiled functions by address. Shared with
    tools/mgst_snap.py."""
    global SYMS, LIBMAP, LIBGCC, OBJC_RET
    funcs = init_boundary()
    LIBGCC = subprocess.run(["arm-none-eabi-gcc", "-march=armv6", "-mthumb", "-mfloat-abi=softfp",
                             "-print-libgcc-file-name"], capture_output=True, text=True).stdout.strip()
    SYMS = {}
    # a `data` label sitting on a function entry (Ghidra names a method's
    # entry after the ObjC/C++ member it touches, e.g. `itemFlag` at
    # +[EnemyManager itemFlag] 0x2ab34) is never what a DATA reference means:
    # the variable is the other row (static __ZL8itemFlag 0x84364). 55 names.
    entries = {int(f["addr"], 16) for f in funcs.values()}
    for l in open(os.path.join(CDIR, "symbols.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0] != "name":
            v = (int(p[2], 16), p[3])
            old = SYMS.get(p[1])
            if old is None or (old[1] == "data" and old[0] in entries and v[1] == "data" and v[0] not in entries):
                SYMS[p[1]] = v
    # Ghidra names a class AND its metaclass `objc::class_t::X`: the receiver
    # of +[X ...] is the CLASS object (classes.tsv class_va), never the metaclass
    for l in open(os.path.join(ROOT, "analysis/objc/classes.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0] != "class":
            SYMS["objc__class_t__" + p[0]] = (int(p[2], 16), "data")
    OBJC_RET = {}
    for l in open(os.path.join(ROOT, "analysis/objc/methods.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0] != "class" and len(p) > 4:
            OBJC_RET[int(p[4], 16) & ~1] = p[3][:1]
    # libc names clang/libgcc may emit -> the original binary's own import stubs
    LIBMAP = {}
    for addr, n in STUBS.items():
        LIBMAP[n.lstrip("_")] = (addr, "func_arm")
    return funcs


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=1800)
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--stage", type=int, help="redirect the next +[Stage setNum:] to this stage (ACT mode start)")
    ap.add_argument("--godmode", action="store_true", help="Snake never dies (HP := max at setDamage)")
    ap.add_argument("--warmup", type=float, default=0,
                    help="seconds with only injection breakpoints armed (a stage loads at full speed)")
    ap.add_argument("--drain", type=int, default=0, help="enemy HP %% lost per AI state change (0 = off)")
    a = ap.parse_args()

    funcs = init_link()
    todo = {}
    for addr, f in funcs.items():
        if a.only and f["addr"] not in a.only and f["name"] not in a.only:
            continue
        if os.path.exists(os.path.join(FDIR, f["addr"] + ".o")):
            todo[addr] = f
    # functions the coverage traces saw executing first (the game will hit them)
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import glob as _glob
        import mgst_coverage as _mc
        seen = set()
        for t in _glob.glob(os.path.join(ROOT, "oracle/reports/campaign_*.drcov")):
            try:
                for pc, _sz in _mc.read_drcov(t)[1]:
                    seen.add(pc)
            except Exception:
                pass
        starts = sorted(todo)
        import bisect as _bi
        hitfn = set()
        for pc in seen:
            k = _bi.bisect_right(starts, pc) - 1
            if k >= 0:
                hitfn.add(starts[k])
        order = [k for k in starts if k in hitfn] + [k for k in starts if k not in hitfn]
        todo = {k: todo[k] for k in order}
        print("functions to test: %d (%d seen executing in coverage)" % (len(todo), len(hitfn)))
    except Exception as e:
        print("no coverage ordering:", e)
    linked = {}
    results = {}
    out = open(os.path.join(CDIR, "difftest_results.jsonl"), "a")
    ref_hdr = open(REF_EXE, "rb").read(32)

    g = RSP(port=a.port)
    g.cmd("?")

    import signal as _sig

    def _bye(*_a):
        # never leave the guest halted with our breakpoints in it
        try:
            g.s.sendall(b"\x03")
            time.sleep(0.5)
            for k in list(active):
                g.cmd("z1,%x,2" % k, timeout=5)
            g.s.sendall(b"$D#44")
        finally:
            os._exit(1)
    _sig.signal(_sig.SIGTERM, _bye)
    _sig.signal(_sig.SIGINT, _bye)
    # ---- state injection (same rules as tools/mgst_gdb.py), gated on identity
    SETNUM, SETDAMAGE, SETAI = 0x3f0ec, 0x3d448, 0x2c92c
    cls_of = {}
    sup = {}
    for l in open(os.path.join(ROOT, "analysis/objc/classes.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0] != "class":
            cls_of[int(p[2], 16)] = p[0]
            sup[p[0]] = p[1]

    def is_enemy(c):
        while c and c != "?":
            if c == "NPC":
                return False
            if c == "EnemyBase":
                return True
            c = sup.get(c)
        return False

    inj = {}
    if a.stage:
        inj[SETNUM] = "stage"
    if a.godmode:
        inj[SETDAMAGE] = "god"
    if a.drain:
        inj[SETAI] = "drain"
    stage_left = [a.stage]
    injlog = collections.Counter()

    def w32(addr, v):
        g.cmd("M%x,4:%s" % (addr, struct.pack("<I", v & 0xffffffff).hex()))

    def setreg(n, v):
        g.cmd("P%x=%s" % (n, struct.pack("<I", v & 0xffffffff).hex()))

    def r32(addr):
        return struct.unpack("<I", g.read(addr, 4))[0]

    def inject(pc, regs):
        kind = inj[pc]
        if kind == "stage" and stage_left[0]:
            setreg(2, stage_left[0])
            injlog["stage->%d (was %d)" % (stage_left[0], regs[2])] += 1
            stage_left[0] = 0
        elif kind == "god":
            mx = r32(0x84b48)
            w32(0x84b44, mx)
            if regs[2] >= mx:
                setreg(2, max(mx - 1, 0))
            injlog["godmode"] += 1
        elif kind == "drain" and (regs[2] & 0xffff) not in (10, 0xff):
            self_ = regs[0]
            c = cls_of.get(r32(self_), "?")
            if is_enemy(c):
                ene = r32(self_ + 12)
                hp, mx = struct.unpack("<ii", g.read(ene, 8))
                if hp > 0:
                    new = hp - max(1, mx * a.drain // 100)
                    if new <= 0:
                        w32(ene, 0)
                        setreg(2, 10)
                        injlog["kill:" + c] += 1
                    else:
                        w32(ene, new)
                        injlog["drain:" + c] += 1

    for k in inj:
        todo.pop(k, None)
        g.cmd("Z1,%x,2" % k)
    t_start = time.time()
    t_end = t_start + a.seconds
    samples = {k: 0 for k in todo}
    pristine_ro = {}                 # read-only pages (MGST __TEXT, dylib text) survive across stops
    active = []
    last_hit = time.time()
    while time.time() < t_end and any(samples[k] < a.samples for k in todo):
        # (re)arm a batch of breakpoints
        pending = [k for k in todo if samples[k] < a.samples]
        # rotate: a batch that saw no hit for ROTATE s goes to the back of the line
        if active and time.time() - last_hit > 20:
            for k in active:
                if k in todo and samples[k] < a.samples:
                    todo[k] = todo.pop(k)
            last_hit = time.time()
            pending = [k for k in todo if samples[k] < a.samples]
        want = pending[:a.batch] if time.time() >= t_start + a.warmup else []
        for k in active:
            if k not in want:
                g.cmd("z1,%x,2" % k)
        for k in want:
            if k not in active:
                g.cmd("Z1,%x,2" % k)
        active = want
        stop = g.cont_until_stop(timeout=20)
        regs = g.regs()
        pc = regs[15] & ~1
        if pc in inj:
            try:
                if g.read(0x1000, 32) == ref_hdr:
                    inject(pc, regs)
            except MemoryError:
                pass
            continue
        if pc not in todo:
            continue
        last_hit = time.time()
        try:
            if g.read(0x1000, 32) != ref_hdr:
                continue                                  # same VA in another process
        except MemoryError:
            continue
        fn = todo[pc]
        if pc not in linked:
            try:
                linked[pc] = link(fn)
            except Exception as e:
                linked[pc] = {"error": "link exception: %s" % str(e)[:120]}
        L = linked[pc]
        if not L or "error" in L:
            results[pc] = ("link-failed", (L or {}).get("error", "no object"))
            samples[pc] = a.samples
            out.write(json.dumps({"addr": fn["addr"], "name": fn["name"], "verdict": "link-failed",
                                  "detail": results[pc][1]}) + "\n")
            continue
        page_cache = dict(pristine_ro)

        def fetch(page):
            return g.read(page, PAGE)
        try:
            ra = Run(page_cache, fetch, regs, pc | (1 if fn["thumb"] else 0), fn["thumb"]).go()
            rb = Run(page_cache, fetch, regs, L["entry"], True, code=L["bin"]).go()
        except Exception as e:
            samples[pc] += 1
            out.write(json.dumps({"addr": fn["addr"], "name": fn["name"], "verdict": "untestable",
                                  "detail": "harness exception: %s" % str(e)[:160]}) + "\n")
            continue
        for p, d in page_cache.items():
            if 0x1000 <= p < 0x69000 or 0x30000000 <= p < 0x38000000:
                pristine_ro[p] = d
        verdict, detail = compare(fn, ra, rb)
        samples[pc] += 1
        prev = results.get(pc)
        if prev is None or verdict == "fail" or (prev[0] == "untestable" and verdict == "pass"):
            results[pc] = (verdict, detail)
        out.write(json.dumps({"addr": fn["addr"], "name": fn["name"], "verdict": verdict, "detail": detail,
                              "insns_orig": ra.insns, "insns_recomp": rb.insns,
                              "boundary_calls": len(ra.calls), "t": time.time()}) + "\n")
        out.flush()
        print("%-6s %s %s %s" % (verdict, fn["addr"], fn["name"][:60], detail[:80]), flush=True)
    for k in list(active) + list(inj):
        g.cmd("z1,%x,2" % k)
    g.s.sendall(b"$D#44")   # detach, guest keeps running
    print("injections: %s" % dict(injlog))
    print("tested %d functions" % len(results))


if __name__ == "__main__":
    main()
