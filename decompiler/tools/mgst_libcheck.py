#!/usr/bin/env python3
"""Call the ORIGINAL iOS 3.1.3 library functions the game imports, inside a
captured snapshot (the process image holds the real, already-bound
libSystem / libm), and compare them with a port's reimplementation
(LOG 2026-10-11).

  tools/mgst_libcheck.py random  [--snap DIR]          Darwin srandom/random vs a
                                                       Python transcription of the
                                                       port's rt/libc.c
  tools/mgst_libcheck.py libm OUT.tsv [--snap DIR]     sinf/cosf/atan2f over the
                                                       inputs the game uses; writes
                                                       the original bits for a
                                                       device-side comparison

Each call enters the game's own import stub (__symbol_stub4, ARM mode), which
jumps through its bound lazy pointer into the real library: exactly the path
the game takes.
"""
import argparse
import math
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

STUB = {"_srandom": 0x5ae48, "_random": 0x5ae24, "_sinf": 0x5ae30, "_cosf": 0x5ab90,
        "_atan2f": 0x5ab78, "_sqrtf": 0x5ae3c}
SENTINEL = 0x0fff0000


class Lib:
    def __init__(self, snapdir):
        from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_MEM_UNMAPPED, UC_PROT_ALL
        from unicorn.arm_const import UC_ARM_REG_C13_C0_3, UC_ARM_REG_FPSCR, UC_ARM_REG_C1_C0_2, UC_ARM_REG_FPEXC
        import mgst_snap as S
        cap = S.Capture(snapdir)
        off = [o for o, s in cap.samples(with_offset=True) if s.status == 4][0]
        self.snap = cap.sample_at(off)
        self.W = S.CallWorld(cap, self.snap)
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        self.mapped = set()
        self.uc.mem_map(SENTINEL, 0x1000, UC_PROT_ALL)
        self.uc.hook_add(UC_HOOK_MEM_UNMAPPED, self._unmapped)
        try:
            self.uc.reg_write(UC_ARM_REG_C1_C0_2, self.uc.reg_read(UC_ARM_REG_C1_C0_2) | (0xf << 20))
            self.uc.reg_write(UC_ARM_REG_FPEXC, 0x40000000)
        except Exception:
            pass
        self.uc.reg_write(UC_ARM_REG_C13_C0_3, self.snap.tid)
        self.uc.reg_write(UC_ARM_REG_FPSCR, self.snap.fpscr)
        self.sp = (self.snap.regs[13] - 0x2000) & ~7

    def _unmapped(self, uc, access, addr, size, value, _):
        from unicorn import UC_PROT_ALL
        for a in (addr, addr + size - 1):
            p = a & ~0xfff
            if p in self.mapped:
                continue
            try:
                data = self.W.page(p)
            except MemoryError:
                return False
            uc.mem_map(p, 0x1000, UC_PROT_ALL)
            uc.mem_write(p, bytes(data))
            self.mapped.add(p)
        return True

    def call(self, name, *words):
        from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, \
            UC_ARM_REG_SP, UC_ARM_REG_LR
        regs = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3]
        for i, w in enumerate(words):
            self.uc.reg_write(regs[i], w & 0xffffffff)
        self.uc.reg_write(UC_ARM_REG_SP, self.sp)
        self.uc.reg_write(UC_ARM_REG_LR, SENTINEL)
        self.uc.emu_start(STUB[name], SENTINEL, count=2_000_000)
        return self.uc.reg_read(UC_ARM_REG_R0)


def f2b(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def b2f(b):
    return struct.unpack("<f", struct.pack("<I", b & 0xffffffff))[0]


class PortRandom:
    """Transcription of mgsport rt/libc.c (BSD TYPE_3 additive feedback)."""
    def __init__(self):
        self.st = [0] * 31
        self.f, self.r = 3, 0

    @staticmethod
    def good_rand(x):
        x = x - (1 << 32) if x & 0x80000000 else x
        if x == 0:
            x = 123459876
        hi, lo = int(x / 127773), x - int(x / 127773) * 127773      # C truncating division
        x = 16807 * lo - 2836 * hi
        if x < 0:
            x += 0x7fffffff
        return x & 0xffffffff

    def srandom(self, seed):
        self.st[0] = seed & 0xffffffff
        for i in range(1, 31):
            self.st[i] = self.good_rand(self.st[i - 1])
        self.f, self.r = 3, 0
        for _ in range(310):
            self.random()

    def random(self):
        self.st[self.f] = (self.st[self.f] + self.st[self.r]) & 0xffffffff
        i = (self.st[self.f] >> 1) & 0x7fffffff
        self.f = 0 if self.f + 1 >= 31 else self.f + 1
        self.r = 0 if self.r + 1 >= 31 else self.r + 1
        return i


def libm_inputs():
    """Angles the game feeds sinf/cosf (radians from degrees, rotation ranges)
    and atan2f pairs (screen deltas), deterministic."""
    xs = []
    for d10 in range(-7200, 7201):                     # -720..720 degrees in 0.1 steps
        xs.append(b2f(f2b(d10 / 10.0 * 3.14 / 180.0)))   # the game's own 3.14/180 conversion
    for i in range(4000):
        xs.append(b2f(f2b(math.sin(i * 0.731) * 40.0)))
    pairs = [(b2f(f2b(y)), b2f(f2b(x))) for y in range(-240, 241, 6) for x in range(-160, 161, 6)]
    return xs, pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("random", "libm"))
    ap.add_argument("out", nargs="?")
    ap.add_argument("--snap", default=os.path.join(ROOT, "oracle/reports/snap/campaign_02-02_dump"))
    a = ap.parse_args()
    L = Lib(a.snap)
    if a.what == "random":
        bad = total = 0
        for seed in (1, 0, 2, 12345, 0x7fffffff, 0x80000000, 0xffffffff, 31337, 1000000007):
            L.call("_srandom", seed)
            p = PortRandom()
            p.srandom(seed)
            for k in range(2000):
                o = L.call("_random") & 0xffffffff
                q = p.random()
                total += 1
                if o != q:
                    bad += 1
                    if bad <= 5:
                        print("seed %#x #%d: iOS %#x port %#x" % (seed, k, o, q))
        print("random(): %d / %d values identical (9 seeds x 2000)" % (total - bad, total))
        return 1 if bad else 0
    xs, pairs = libm_inputs()
    with open(a.out, "w") as w:
        w.write("fn\tin1\tin2\tios_bits\n")
        for x in xs:
            w.write("sinf\t%08x\t-\t%08x\n" % (f2b(x), L.call("_sinf", f2b(x))))
            w.write("cosf\t%08x\t-\t%08x\n" % (f2b(x), L.call("_cosf", f2b(x))))
        for y, x in pairs:
            w.write("atan2f\t%08x\t%08x\t%08x\n" % (f2b(y), f2b(x), L.call("_atan2f", f2b(y), f2b(x))))
    print("libm: %d sinf, %d cosf, %d atan2f original results -> %s" % (len(xs), len(xs), len(pairs), a.out))


if __name__ == "__main__":
    sys.exit(main())
