#!/usr/bin/env python3
"""
Read and validate snap_mgst entry-state captures (PLAN 4b V3, LOG 2026-10-07).

    tools/mgst_snap.py stats  DIR [DIR ...]
    tools/mgst_snap.py replay DIR [DIR ...] [--only ADDR ...] [--limit N]
    tools/mgst_snap.py diff   DIR [DIR ...] [--only ADDR ...] [--jobs J] [--per-fn K]
    tools/mgst_snap.py frames DIR [DIR ...] [--frames F] [--per-fn K] [--jobs J]

A capture directory (oracle/reports/snap/<tag>/, written by the QEMU plugin
oracle/qemu-ios/contrib/plugins/snap_mgst.c) holds pages.bin (4 KiB pages,
deduplicated) and samples.bin: per sampled call of an MGSTUS function, the
entry registers (core, CPSR, FPSCR, d0-d15), every page the call touched at
its first touch, and which bytes the real call wrote with their final values.

stats   samples per status, functions covered, FPSCR values seen, storage.
replay  capture self-validation: run the ORIGINAL function in Unicorn from the
        sample (pages from the capture only, no live guest) with the same
        boundary model as tools/mgst_difftest.py, and compare the bytes it
        writes with what the real call wrote. A faithful capture + boundary
        model reproduces them exactly; differences are classified.
diff    PLAN 4b V4, the offline differential test: from each sample, the
        ORIGINAL function and its recompiled C (recovered/compile/fn, linked
        at 0x300000 against original addresses) run in Unicorn from the same
        captured state, with the device FPSCR and thread pointer, stack below
        entry SP poisoned with a different byte per run (uninitialised
        reads), boundary services stubbed identically. Verdict rules are
        tools/mgst_difftest.compare; a page the recompiled code touches but
        the original never did is a FAIL. Parallel over all cores.
        -> recovered/compile/difftest_offline.jsonl (+ report via
           tools/mgst_difftest_report.py --results ...)
frames  PLAN 4b route step 4, the offline frame driver: from each full-process
        snapshot (status 4, plugin dump mode) Unicorn runs the game's own
        per-frame method (the snapshot's function, -[CrashLandingAppDelegate
        renderScene]) frame after frame - original code, world memory kept
        across frames, boundary services modelled as in diff. Only the import
        stubs and the entries of the functions under test are hooked, so the
        world runs at Unicorn speed. At each hooked entry the world is paused
        and the original and recompiled function run from that exact state in
        child engines that read the paused world's memory (same verdict rules
        as diff). Functions are tested on their first K reached states per
        snapshot. -> recovered/compile/difftest_frames.jsonl
"""
import argparse
import collections
import json
import mmap
import os
import re
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = 4096
HDR = struct.Struct("<IIIIIQ16IIIII16QII")
PF_CODE, PF_STOREFIRST, PF_UNREADABLE, PF_IO = 1, 2, 4, 8
STATUS = {0: "ok", 1: "limit", 2: "unwound", 3: "exit", 4: "snapshot"}
FRAME = 0x20000          # callee frames below the entry SP (as mgst_difftest)


class Sample:
    __slots__ = ("fn", "hit", "status", "tbs", "regs", "cpsr", "fpscr", "fpexc", "tid", "d",
                 "pages", "dirty", "cap")


class Capture:
    def __init__(self, d):
        self.dir = d
        f = open(os.path.join(d, "pages.bin"), "rb")
        size = os.fstat(f.fileno()).st_size
        self.pages = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) if size else b""
        self.npages = size // PAGE

    def page(self, idx):
        if idx == 0xffffffff or idx >= self.npages:
            return None
        return self.pages[idx * PAGE:(idx + 1) * PAGE]

    def samples(self, with_offset=False):
        data = self._data()
        off = 0
        while off + 8 <= len(data):
            magic, ln = struct.unpack_from("<II", data, off)
            if magic != 0x31504d53 or off + ln > len(data):
                break                                   # truncated tail (QEMU killed)
            s = self.sample_at(off)
            yield (off, s) if with_offset else s
            off += ln

    def _data(self):
        if getattr(self, "_raw", None) is None:
            self._raw = open(os.path.join(self.dir, "samples.bin"), "rb").read()
        return self._raw

    def sample_at(self, off):
        data = self._data()
        if True:
            v = HDR.unpack_from(data, off)
            s = Sample()
            s.cap = self
            s.fn, s.hit, s.status, s.tbs = v[2], v[3], v[4], v[5]
            s.regs = list(v[6:22])
            s.cpsr, s.fpscr, s.fpexc, s.tid = v[22:26]
            s.d = list(v[26:42])
            np_, nd = v[42], v[43]
            p = off + HDR.size
            s.pages = {}
            for _ in range(np_):
                va, idx, fl = struct.unpack_from("<III", data, p)
                s.pages[va] = (idx, fl)
                p += 12
            s.dirty = {}
            for _ in range(nd):
                va, idx = struct.unpack_from("<II", data, p)
                s.dirty[va] = (idx, data[p + 8:p + 8 + PAGE // 8])
                p += 8 + PAGE // 8
            return s

    def real_writes(self, s):
        """{addr: final byte} the real call wrote, outside its callee frames."""
        out = {}
        sp = s.regs[13]
        for va, (idx, bm) in s.dirty.items():
            pg = self.page(idx)
            for i in range(PAGE):
                if bm[i >> 3] >> (i & 7) & 1:
                    a = va + i
                    if sp - FRAME <= a < sp:
                        continue
                    out[a] = pg[i] if pg else None
        return out


def fn_names():
    names = {}
    p = os.path.join(ROOT, "recovered/compile/functions.jsonl")
    if os.path.exists(p):
        for l in open(p):
            f = json.loads(l)
            names[int(f["addr"], 16)] = f["name"]
    return names


def cmd_stats(a):
    names = fn_names()
    entries = [int(l, 16) for l in open(os.path.join(ROOT, "analysis/symbols/function_entries.txt"))]
    st = collections.Counter()
    per_fn = collections.Counter()
    fpscr = collections.Counter()
    npages = []
    total_pages = 0
    for d in a.dirs:
        c = Capture(d)
        total_pages += c.npages
        for s in c.samples():
            st[STATUS.get(s.status, s.status)] += 1
            if s.status == 0:
                per_fn[s.fn] += 1
                npages.append(len(s.pages))
                fpscr["0x%08x" % s.fpscr] += 1
    covered = len(per_fn)
    print("captures      : %s" % " ".join(a.dirs))
    print("samples       : %s" % dict(st))
    print("functions     : %d / %d with >= 1 ok sample (%.1f%%), >= 3: %d" % (
        covered, len(entries), 100.0 * covered / len(entries), sum(1 for v in per_fn.values() if v >= 3)))
    print("pages stored  : %d (%.1f MiB)" % (total_pages, total_pages * PAGE / 2**20))
    if npages:
        npages.sort()
        print("pages/sample  : median %d, p95 %d, max %d" % (
            npages[len(npages) // 2], npages[int(len(npages) * .95)], npages[-1]))
    print("FPSCR at entry: %s" % dict(fpscr.most_common(6)))
    if a.missing:
        miss = [e for e in entries if e not in per_fn]
        for e in miss:
            print("  no sample: 0x%x %s" % (e, names.get(e, "")))


def replay_one(s, funcs):
    import mgst_difftest as D
    from unicorn import UcError
    cap = s.cap
    pristine = {}

    def fetch(page):
        ent = s.pages.get(page)
        if not ent or ent[1] & PF_UNREADABLE:
            raise MemoryError(page)
        data = cap.page(ent[0])
        if data is None:
            raise MemoryError(page)
        return bytes(data)
    thumb = bool(s.cpsr & 0x20)
    regs = s.regs[:15] + [s.fn]
    run = D.Run(pristine, fetch, regs, s.fn | (1 if thumb else 0), thumb, tid=s.tid, fpscr=s.fpscr)
    run.go()
    if run.status != "ok":
        return "untestable", run.status, 0
    real = cap.real_writes(s)
    mine = run.final
    only_real = [k for k in real if k not in mine]
    only_mine = [k for k in mine if k not in real]
    differ = [k for k in real if k in mine and real[k] != mine[k]]
    if not only_real and not only_mine and not differ:
        return "exact", "", len(real)
    det = "real-only %d, replay-only %d, differ %d" % (len(only_real), len(only_mine), len(differ))
    first = sorted(only_real + only_mine + differ)[:1]
    if first:
        det += " (first 0x%x)" % first[0]
    if run.calls and not only_mine and not differ:
        # the real call's boundary services (GL/audio/UI...) wrote memory the
        # stubbed replay cannot: expected, not a capture defect
        return "exact-modulo-boundary", det + "; %d boundary call(s)" % len(run.calls), len(real)
    return "differs", det, len(real)


def cmd_replay(a):
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import mgst_difftest as D
    funcs = D.init_boundary()
    names = fn_names()
    only = {int(x, 16) for x in a.only} if a.only else None
    verdicts = collections.Counter()
    out = open(a.out, "w") if a.out else None
    n = 0
    for d in a.dirs:
        for s in Capture(d).samples():
            if s.status != 0 or (only and s.fn not in only):
                continue
            if a.limit and n >= a.limit:
                break
            n += 1
            try:
                v, det, nw = replay_one(s, funcs)
            except Exception as e:
                v, det, nw = "harness-error", str(e)[:160], 0
            verdicts[v] += 1
            row = {"capture": os.path.basename(d.rstrip("/")), "addr": "0x%x" % s.fn,
                   "name": names.get(s.fn, ""), "hit": s.hit, "verdict": v, "detail": det,
                   "real_bytes": nw, "pages": len(s.pages)}
            if out:
                out.write(json.dumps(row) + "\n")
            if v not in ("exact",) or a.verbose:
                print("%-22s 0x%-6x #%-6d %-50s %s" % (v, s.fn, s.hit, names.get(s.fn, "")[:50], det[:90]),
                      flush=True)
    print("replayed %d samples: %s" % (n, dict(verdicts)))


_CAPS = {}


def _diff_one(task):
    """Worker: original vs recompiled from one sample."""
    import mgst_difftest as D
    d, off = task
    cap = _CAPS.get(d)
    if cap is None:
        cap = _CAPS[d] = Capture(d)
    s = cap.sample_at(off)
    fn = DIFF_FUNCS[s.fn]
    L = DIFF_LINKED[s.fn]
    row = {"capture": os.path.basename(d.rstrip("/")), "addr": fn["addr"], "name": fn["name"], "hit": s.hit,
           "t": 0, "fp": L.get("fp"), "hv": D.HARNESS}

    def fetch(page):
        ent = s.pages.get(page)
        if not ent or ent[1] & (PF_UNREADABLE | PF_IO):
            raise MemoryError(page)
        data = cap.page(ent[0])
        if data is None:
            raise MemoryError(page)
        return bytes(data)
    thumb = bool(s.cpsr & 0x20)
    regs = s.regs[:15] + [s.fn]
    try:
        verdict, detail, ra, rb = D.run_compare(fn, {}, fetch, regs, s.fn | (1 if thumb else 0), thumb, L,
                                                tid=s.tid, fpscr=s.fpscr)
        row.update(verdict=verdict, detail=detail, insns_orig=ra.insns, insns_recomp=rb.insns,
                   boundary_calls=len(ra.calls))
        if verdict == "pass" and ra.covered:
            row["cov"] = D.cov_encode(ra.covered, s.fn & ~1)
    except Exception as e:
        row.update(verdict="untestable", detail="harness exception: %s" % str(e)[:160])
    return row


def cmd_diff(a):
    import multiprocessing
    import mgst_difftest as D
    global DIFF_FUNCS, DIFF_LINKED
    DIFF_FUNCS = D.init_link()
    only = {int(x, 16) for x in a.only} if a.only else None
    tasks, per = [], collections.Counter()
    for d in a.dirs:
        for off, s in Capture(d).samples(with_offset=True):
            if s.status != 0 or s.fn not in DIFF_FUNCS or (only and s.fn not in only):
                continue
            if per[s.fn] >= a.per_fn:
                continue
            per[s.fn] += 1
            tasks.append((d, off))
    # link each function once (serial: subprocesses, writes fn/<addr>.*)
    DIFF_LINKED = {}
    out = open(a.out, "w")
    linkfail = 0
    for fa in sorted(per):
        fn = DIFF_FUNCS[fa]
        try:
            L = D.link(fn)
        except Exception as e:
            L = {"error": "link exception: %s" % str(e)[:120]}
        if not L or "error" in L:
            linkfail += 1
            out.write(json.dumps({"addr": fn["addr"], "name": fn["name"], "verdict": "link-failed",
                                  "detail": (L or {}).get("error", "no object")}) + "\n")
        else:
            DIFF_LINKED[fa] = L
    tasks = [(d, off) for d, off in tasks if _fn_of(d, off) in DIFF_LINKED]
    print("diff: %d samples of %d functions (%d link failures), %d jobs" % (
        len(tasks), len(per), linkfail, a.jobs), flush=True)
    verdicts = collections.Counter()
    with multiprocessing.get_context("fork").Pool(a.jobs) as pool:
        for i, row in enumerate(pool.imap_unordered(_diff_one, tasks, chunksize=4)):
            out.write(json.dumps(row) + "\n")
            verdicts[row["verdict"]] += 1
            if (i + 1) % 500 == 0:
                out.flush()
                print("  %d/%d %s" % (i + 1, len(tasks), dict(verdicts)), flush=True)
    out.close()
    print("diff done: %s -> %s" % (dict(verdicts), a.out))


_TEXT_IMG = None


def text_page(page):
    """A page of the MGSTUS image that the snapshot lacks because the process
    never touched it, so iOS never paged it in: its content is still the
    initial image. __TEXT (read-only) and never-touched __DATA pages come
    from the reference binary (not encrypted: cryptid 0; __TEXT vmaddr 0x1000 =
    file 0, __DATA vmaddr 0x69000 = file 0x68000, filesize 0xd000); the rest
    of __DATA (vmsize 0x20000) is zero-fill (bss)."""
    global _TEXT_IMG
    if _TEXT_IMG is None:
        import mgst_difftest as D
        _TEXT_IMG = open(D.REF_EXE, "rb").read(0x75000)
    if 0x1000 <= page < 0x69000:
        return _TEXT_IMG[page - 0x1000:page]
    if 0x69000 <= page < 0x69000 + 0xd000:
        o = 0x68000 + page - 0x69000
        return _TEXT_IMG[o:o + 0x1000]
    if 0x69000 + 0xd000 <= page < 0x89000:
        return bytes(0x1000)
    raise MemoryError(page)


class FrameWorld:
    """The game's own frames, from a full-process snapshot, in Unicorn."""

    def __init__(self, cap, snap, funcs, linked, per_fn, max_insns):
        import mgst_difftest as D
        from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_MEM_UNMAPPED, UC_HOOK_CODE, UC_HOOK_INTR, UC_PROT_ALL
        from unicorn.arm_const import UC_ARM_REG_C13_C0_3, UC_ARM_REG_FPSCR, UC_ARM_REG_C1_C0_2, UC_ARM_REG_FPEXC
        self.D, self.cap, self.snap, self.funcs, self.linked = D, cap, snap, funcs, linked
        self.per_fn, self.max_insns = per_fn, max_insns
        self.uc = uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.mapped = set()
        uc.mem_map(D.SENTINEL, D.PAGE, UC_PROT_ALL)
        try:
            uc.reg_write(UC_ARM_REG_C1_C0_2, uc.reg_read(UC_ARM_REG_C1_C0_2) | (0xf << 20))
            uc.reg_write(UC_ARM_REG_FPEXC, 0x40000000)
        except Exception:
            pass
        uc.reg_write(UC_ARM_REG_C13_C0_3, snap.tid)
        uc.reg_write(UC_ARM_REG_FPSCR, snap.fpscr)
        uc.hook_add(UC_HOOK_MEM_UNMAPPED, self.on_unmapped)
        uc.hook_add(UC_HOOK_INTR, self.on_intr)
        lo, hi = min(D.STUBS), max(D.STUBS) + 12
        uc.hook_add(UC_HOOK_CODE, self.on_stub, begin=lo, end=hi)
        for a in linked:
            uc.hook_add(UC_HOOK_CODE, self.on_entry, begin=a, end=a)
        self.seen = collections.Counter()
        self.syscalls = collections.Counter()
        self.clock = 1 << 40
        self.rows = []
        self.stop_reason = None
        self.frame = 0

    def snap_page(self, page):
        ent = self.snap.pages.get(page)
        if not ent:
            return text_page(page)
        if ent[1] & (PF_UNREADABLE | PF_IO):
            raise MemoryError(page)
        data = self.cap.page(ent[0])
        if data is None:
            raise MemoryError(page)
        return bytes(data)

    def on_unmapped(self, uc, access, addr, size, value, _):
        from unicorn import UC_PROT_ALL
        for page in {addr & ~0xfff, (addr + size - 1) & ~0xfff}:
            if page in self.mapped:
                continue
            try:
                data = self.snap_page(page)
            except MemoryError:
                self.stop_reason = "unmapped 0x%x" % addr
                return False
            uc.mem_map(page, 0x1000, UC_PROT_ALL)
            uc.mem_write(page, data)
            self.mapped.add(page)
        return True

    def on_intr(self, uc, intno, _):
        """System calls made by the WORLD (frameworks: Mach IPC to system
        services, the clock, ...) are answered so frames can complete:
        mach_absolute_time (trap -3) is a monotonic clock, everything else
        returns success (0). This only drives the world to reach states; each
        TEST runs in a child engine where a system call is 'untestable', so a
        crude world model can never make a test pass."""
        from unicorn.arm_const import UC_ARM_REG_R12, UC_ARM_REG_R0, UC_ARM_REG_R1
        num = uc.reg_read(UC_ARM_REG_R12)
        num = num - (1 << 32) if num & 0x80000000 else num
        self.syscalls[num] += 1
        if sum(self.syscalls.values()) > 200000:
            self.stop_reason = "syscall storm (%s)" % dict(self.syscalls.most_common(3))
            uc.emu_stop()
            return
        if num == -3:
            self.clock += 24000                      # 1 ms of the 24 MHz timebase per call
            uc.reg_write(UC_ARM_REG_R0, self.clock & 0xffffffff)
            uc.reg_write(UC_ARM_REG_R1, self.clock >> 32)
        else:
            uc.reg_write(UC_ARM_REG_R0, 0)

    def on_stub(self, uc, addr, size, _):
        """Boundary services: same model as mgst_difftest.Run (return 0)."""
        D = self.D
        from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_LR, UC_ARM_REG_PC
        name = D.STUBS.get(addr & ~1)
        if name and D.BOUNDARY.match(name):
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_R1, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def child_fetch(self, page):
        if page in self.mapped:
            return bytes(self.uc.mem_read(page, 0x1000))
        return self.snap_page(page)

    def on_entry(self, uc, addr, size, _):
        """A reached call state: original vs recompiled, right here."""
        D = self.D
        if self.seen[addr] >= self.per_fn:
            return
        self.seen[addr] += 1
        fn = self.funcs[addr]
        regs = [uc.reg_read(r) for r in D.REGS]
        regs[15] = addr
        row = {"capture": "%s#%d" % (os.path.basename(self.cap.dir.rstrip("/")), self.snap.hit),
               "frame": self.frame, "addr": fn["addr"], "name": fn["name"], "hit": self.seen[addr],
               "fp": self.linked[addr].get("fp"), "hv": D.HARNESS}
        try:
            L = self.linked[addr]
            v, det, ra, rb = D.run_compare(fn, {}, self.child_fetch, regs, addr | (1 if fn["thumb"] else 0),
                                           fn["thumb"], L, tid=self.snap.tid, fpscr=self.snap.fpscr)
            row.update(verdict=v, detail=det, insns_orig=ra.insns)
            if v == "pass" and ra.covered:
                row["cov"] = D.cov_encode(ra.covered, addr)
        except Exception as e:
            row.update(verdict="untestable", detail="harness exception: %s" % str(e)[:160])
        self.rows.append(row)

    def run_frames(self, n):
        from unicorn import UcError
        from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_SP, UC_ARM_REG_CPSR
        D = self.D
        for k in range(n):
            self.frame = k
            for i, r in enumerate(D.REGS[:15]):
                self.uc.reg_write(r, self.snap.regs[i])
            self.uc.reg_write(UC_ARM_REG_LR, D.SENTINEL | 1)
            try:
                self.uc.emu_start(self.snap.fn | 1, D.SENTINEL, count=self.max_insns)
            except UcError as e:
                self.stop_reason = self.stop_reason or "error %s" % e
            if self.stop_reason:
                return k
            if self.uc.reg_read(D.UC_ARM_REG_PC) & ~1 != D.SENTINEL:
                self.stop_reason = "instruction limit in frame %d" % k
                return k
        return n


def _frames_one(task):
    d, off, nframes, per_fn, max_insns = task
    cap = Capture(d)
    snap = cap.sample_at(off)
    w = FrameWorld(cap, snap, DIFF_FUNCS, DIFF_LINKED, per_fn, max_insns)
    done = w.run_frames(nframes)
    return {"capture": "%s#%d" % (os.path.basename(d.rstrip("/")), snap.hit), "frames_done": done,
            "stop": w.stop_reason, "tests": len(w.rows), "pages": len(w.mapped),
            "syscalls": dict(w.syscalls.most_common(4))}, w.rows


def cmd_frames(a):
    import multiprocessing
    import mgst_difftest as D
    global DIFF_FUNCS, DIFF_LINKED
    DIFF_FUNCS = D.init_link()
    tasks = []
    for d in a.dirs:
        offs = [off for off, s in Capture(d).samples(with_offset=True) if s.status == 4]
        if a.per_dir and len(offs) > a.per_dir:          # an even spread over the run
            offs = sorted({offs[int(i * (len(offs) - 1) / (a.per_dir - 1))] for i in range(a.per_dir)}) \
                if a.per_dir > 1 else offs[:1]
        tasks += [(d, off, a.frames, a.per_fn, a.max_insns) for off in offs]
    print("frames: %d snapshot(s); linking %d functions" % (len(tasks), len(DIFF_FUNCS)), flush=True)
    DIFF_LINKED = {}
    only = {int(x, 16) for x in a.only} if a.only else None
    for fa, fn in sorted(DIFF_FUNCS.items()):
        if only is not None and fa not in only:
            continue
        try:
            L = D.link(fn)
        except Exception:
            L = None
        if L and "error" not in L:
            DIFF_LINKED[fa] = L
    out = open(a.out, "w")
    verdicts = collections.Counter()
    with multiprocessing.get_context("fork").Pool(a.jobs) as pool:
        for info, rows in pool.imap_unordered(_frames_one, tasks):
            for r in rows:
                out.write(json.dumps(r) + "\n")
                verdicts[r["verdict"]] += 1
            out.flush()
            print("  %s: %d frame(s)%s, %d tests, %d pages, syscalls %s" % (
                info["capture"], info["frames_done"], " (stopped: %s)" % info["stop"] if info["stop"] else "",
                info["tests"], info["pages"], info["syscalls"]), flush=True)
    out.close()
    print("frames done: %s -> %s" % (dict(verdicts), a.out))


# --- PLAN 4b V5: synthetic calls on harvested objects -----------------------
#
# A function no snapshot reaches is CALLED directly from a snapshot's state:
# the receiver is a live object of the method's class found in that process
# image (or the class object for a + method), the arguments are a few fixed
# vectors (zeros / ones / small values; pointers -> private zeroed buffers;
# objects -> nil). Original and recompiled run from the identical state and
# are compared exactly as for a natural call (mgst_difftest.compare). Rows are
# tagged source=synthetic so the ledger can tell them apart from natural calls.

CALL_SCRATCH = 0x0e000000          # zeroed private pages for pointer arguments
CALL_FAKE_OBJ = 0x0e100000         # fabricated receiver (zeroed object, isa = class)
CALL_HEAP_LO, CALL_HEAP_HI = 0x100000, 0x30000000
CALL_VECTORS = (("zero", 0, 0.0), ("one", 1, 1.0), ("small", 3, 0.5))
# "live" vector (LOG 2026-10-09): each argument takes the receiver's own
# current ivar of the same name as its selector keyword, else of the same ObjC
# type (re-initialising an enemy with its own pEneDat, its own index, ...) -
# a natural argument where a fixed vector would pass NULL. Arguments with no
# matching ivar use the "one" values. Extra to the per-function budget.


def _ivar_table():
    """{class: [(name, type_without_field_names, offset, size)]}, own ivars."""
    out = collections.defaultdict(list)
    for l in open(os.path.join(ROOT, "analysis/objc/ivars.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0] == "class" or len(p) < 5:
            continue
        out[p[0]].append((p[1], re.sub(r'"[^"]*"', "", p[2]), int(p[3]), int(p[4])))
    return out


def _live_words(W, recv, cls_chain, ivars, selname, args):
    """Argument words of the live vector, or None if no argument is live."""
    keys = [k for k in selname.split(":")[:-1]]
    pool = [iv for c in cls_chain for iv in ivars.get(c, ())]
    words, live = [], 0
    for i, (t, o) in enumerate(args):
        kw = keys[i].lower() if i < len(keys) else ""
        tt = t.lstrip("rnNoORV")
        hit = [iv for iv in pool if iv[0].lower().lstrip("_") == kw and iv[3] <= 8]
        if not hit and tt[:1] == "^":
            hit = [iv for iv in pool if iv[1] == tt]
        ws = None
        if hit:
            name, ity, off, size = hit[0]
            try:
                v = W.rd(recv + off)
                v2 = W.rd(recv + off + 4) if size > 4 else 0
            except (MemoryError, struct.error):
                v = None
            if v is not None:
                if size == 1:
                    v &= 0xff
                    if ity == "c" and v & 0x80:
                        v -= 0x100
                elif size == 2:
                    v &= 0xffff
                    if ity == "s" and v & 0x8000:
                        v -= 0x10000
                ws = [v & 0xffffffff] + ([v2] if size > 4 else [])
                if len(ws) != len(_arg_words(t, 1, 1.0, iter(range(CALL_SCRATCH, CALL_SCRATCH + 0x100000, 0x1000)))):
                    ws = None
                else:
                    live += 1
        if ws is None:
            ws = _arg_words(t, 1, 1.0, iter(range(CALL_SCRATCH + 0x10000 * (i + 1), CALL_SCRATCH + 0x100000, 0x1000)))
        if o is not None:
            while len(words) + 2 < o // 4:          # offsets count self and _cmd
                words.append(0)
        words += ws
    return words if live else None


# C++ receivers (`this`): polymorphic classes by their vtable pointer at +0
# (object word == _ZTV + 8, subclasses included); the others along the
# pointer chains the code itself uses (_gSoundService 0x7576c; SoundService
# f1 at +4 = SoundResourceManager; ALSound field12_0x24 = SoundLabel).
CPP_VTABLES = {"ALSound": [0x6943c + 8], "AQSound": [0x69498 + 8], "Sound": [0x6943c + 8, 0x69498 + 8]}
CPP_CHAINS = {"SoundService": [0x7576c], "SoundResourceManager": [0x7576c, 4],
              "SoundLabel": ("vt", "ALSound", 0x24)}


def _objc_types(enc):
    """'v20@0:4f8{CGSize=ff}12' -> [(type, offset)], return first."""
    out, i = [], 0

    def one(i):
        while i < len(enc) and enc[i] in "rnNoORV":
            i += 1
        c = enc[i]
        if c == "^":
            return one(i + 1)
        if c in "{([":
            close = {"{": "}", "(": ")", "[": "]"}[c]
            depth, j = 0, i
            while True:
                if enc[j] in "{([":
                    depth += 1
                elif enc[j] in "})]":
                    depth -= 1
                    if depth == 0:
                        return j + 1
                elif enc[j] == '"':
                    j = enc.index('"', j + 1)
                j += 1
        if c == "b":
            j = i + 1
            while j < len(enc) and enc[j].isdigit():
                j += 1
            return j
        return i + 1
    while i < len(enc):
        j = one(i)
        t = enc[i:j]
        k = j
        while k < len(enc) and (enc[k].isdigit() or enc[k] == "-"):
            k += 1
        out.append((t, int(enc[j:k]) if k > j else None))
        i = k
    return out


def _arg_words(kind, ival, fval, scratch):
    """Words for one argument of ObjC type `kind`."""
    k = kind.lstrip("rnNoORV")
    if k[:1] in ("^", "*"):
        return [next(scratch)]
    if k[:1] in ("@", "#"):
        return [0]
    if k[:1] == ":":
        return [0]
    if k == "f":
        return [struct.unpack("<I", struct.pack("<f", fval))[0]]
    if k == "d":
        return list(struct.unpack("<II", struct.pack("<d", fval)))
    if k in ("q", "Q"):
        return [ival, 0]
    if k[:1] == "{":
        body = k[k.index("=") + 1:-1] if "=" in k else ""
        fields = re.findall(r'\{[^}]*\}|[a-zA-Z^*@#:]', re.sub(r'"[^"]*"', "", body))
        words = []
        for f in fields:
            words += _arg_words(f, ival, fval, scratch)
        return words or [0]
    return [ival & 0xffffffff]


def _c_arg_words(ctype, ival, fval, scratch):
    t = ctype.strip()
    if "*" in t or "[" in t:
        return [next(scratch)]
    base = t.split()[0] if t.split() else t
    if base == "float":
        return [struct.unpack("<I", struct.pack("<f", fval))[0]]
    if base == "double":
        return list(struct.unpack("<II", struct.pack("<d", fval)))
    if "longlong" in t.replace(" ", "") or base in ("ulonglong", "undefined8", "int64_t"):
        return [ival, 0]
    if re.match(r"(u?int|uint|bool|char|uchar|short|ushort|long|ulong|undefined[1-4]?|byte|word|dword|size_t)$", base):
        return [ival & 0xffffffff]
    raise ValueError("unsupported argument type %r" % t)


class CallWorld:
    """One snapshot: memory access, object harvesting, synthetic calls."""

    def __init__(self, cap, snap):
        self.cap, self.snap = cap, snap
        self.cache = {}

    def page(self, page):
        if page not in self.cache:
            ent = self.snap.pages.get(page)
            if not ent:
                self.cache[page] = text_page(page)
                return self.cache[page]
            if ent[1] & (PF_UNREADABLE | PF_IO):
                raise MemoryError(page)
            data = self.cap.page(ent[0])
            if data is None:
                raise MemoryError(page)
            self.cache[page] = bytes(data)
        return self.cache[page]

    def rd(self, addr):
        p = self.page(addr & ~0xfff)
        return struct.unpack_from("<I", p, addr & 0xfff)[0]

    def harvest(self, class_vas, per_class=4):
        """{class_va: [object addresses]}: 16-byte-aligned heap words whose
        value is the class pointer (an object's isa)."""
        import numpy as np
        want = np.array(sorted(class_vas), dtype=np.uint32)
        found = collections.defaultdict(list)
        for page in sorted(self.snap.pages):
            if not (CALL_HEAP_LO <= page < CALL_HEAP_HI):
                continue
            try:
                w = np.frombuffer(self.page(page), dtype="<u4")[::4]
            except MemoryError:
                continue
            for i in np.nonzero(np.isin(w, want))[0]:
                cv = int(w[i])
                if len(found[cv]) < per_class:
                    found[cv].append(page + int(i) * 16)
        return found

    def cpp_this(self, cls, vt_objs):
        """Candidate `this` pointers for C++ class cls."""
        if cls in CPP_VTABLES:
            return [o for v in CPP_VTABLES[cls] for o in vt_objs.get(v, [])]
        ch = CPP_CHAINS.get(cls)
        try:
            if isinstance(ch, tuple):
                return [p for p in (self.rd(o + ch[2]) for o in self.cpp_this(ch[1], vt_objs)) if p][:4]
            if ch:
                p = self.rd(ch[0])
                for off in ch[1:]:
                    p = self.rd(p + off) if p else 0
                return [p] if p else []
        except (MemoryError, struct.error):
            pass
        return []

    def method_sel(self, ro, sel_name):
        """The selector pointer of sel_name in a class_ro_t's baseMethods."""
        try:
            ml = self.rd(ro + 20)
            if not ml:
                return 0
            n = self.rd(ml + 4)
            for k in range(min(n, 4096)):
                m = ml + 8 + 12 * k
                name = self.rd(m)
                s = bytes(self.page(name & ~0xfff))[name & 0xfff:(name & 0xfff) + len(sel_name) + 1]
                if s == sel_name.encode() + b"\0":
                    return name
        except (MemoryError, struct.error):
            pass
        return 0


SUPERS = {}


def _ancestors(c):
    out = []
    while c and c not in out:
        out.append(c)
        c = SUPERS.get(c)
    return out


def _call_args_table():
    """analysis/symbols/call_args.tsv: per function, the arguments its caller(s)
    in the binary actually pass (cited in the reason column) - for methods
    whose fixed vectors only produce inputs the original itself would crash
    on. Items: ivar:Class.name (that ivar of a live Class object), f:X, i:N."""
    out = {}
    path = os.path.join(ROOT, "analysis/symbols/call_args.tsv")
    if os.path.exists(path):
        for l in open(path):
            p = l.rstrip("\n").split("\t")
            if p[0].startswith("0x") and len(p) > 1:
                out[int(p[0], 16)] = p[1].split(",")
    return out


def _caller_words(W, items, objs, classes, ivars):
    words = []
    for it in items:
        kind, _, v = it.partition(":")
        if kind == "f":
            words.append(struct.unpack("<I", struct.pack("<f", float(v)))[0])
        elif kind == "i":
            words.append(int(v, 0) & 0xffffffff)
        elif kind == "ivar":
            cls, name = v.split(".")
            off = next((iv[2] for c in _ancestors(cls) for iv in ivars.get(c, ()) if iv[0] == name), None)
            obj = next(iter(objs.get(classes[cls][0], [])), None) if cls in classes else None
            if off is None or obj is None:
                return None
            words.append(W.rd(obj + off))
        else:
            return None
    return words


def _call_tasks_load():
    """Targets and their call recipes (static: metadata + prototypes)."""
    classes, subs = {}, collections.defaultdict(set)
    for l in open(os.path.join(ROOT, "analysis/objc/classes.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0] != "class":
            classes[p[0]] = (int(p[2], 16), int(p[3], 16))
            subs[p[1]].add(p[0])
            SUPERS[p[0]] = p[1]

    def family(c):
        out, todo = [], [c]
        while todo:
            x = todo.pop()
            out.append(x)
            todo += sorted(subs.get(x, ()))
        return out
    methods = {}
    for l in open(os.path.join(ROOT, "analysis/objc/methods.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0] != "class" and len(p) > 4:
            methods[int(p[4], 16) & ~1] = (p[0], p[1], p[2], p[3])
    return classes, family, methods


def _calls_one(task):
    import mgst_difftest as D
    d, off, targets, per_fn = task
    cap = Capture(d)
    snap = cap.sample_at(off)
    W = CallWorld(cap, snap)
    classes, family, methods = _call_tasks_load()
    ivars = _ivar_table()
    va2cls = {v[0]: c for c, v in classes.items()}
    tag = "%s#%d" % (os.path.basename(d.rstrip("/")), snap.hit)
    need = set()
    for a in targets:
        m = methods.get(a)
        if m and m[1] == "-":
            need |= {classes[c][0] for c in family(m[0]) if c in classes}
            # live-vector donors for a fabricated receiver: the whole family
            # of the root app class above it (EnemyBase for Canard, ...)
            app = [c for c in _ancestors(m[0]) if c in classes]
            if app:
                need |= {classes[c][0] for c in family(app[-1]) if c in classes}
    cargs = _call_args_table()
    for a in targets:
        for it in cargs.get(a, ()):
            if it.startswith("ivar:") and it[5:].split(".")[0] in classes:
                need.add(classes[it[5:].split(".")[0]][0])
    if any("__thiscall" in DIFF_FUNCS[a]["proto"] for a in targets):
        need |= {v for vs in CPP_VTABLES.values() for v in vs}
    objs = W.harvest(need) if need else {}
    rows, skipped = [], collections.Counter()
    sp = (snap.regs[13] - 0x400) & ~7
    for a in targets:
        fn = DIFF_FUNCS[a]
        L = DIFF_LINKED.get(a)
        if L is None:
            continue
        m = methods.get(a)
        receivers, sel, args = [None], 0, None
        try:
            if m:
                cls, kind, selname, enc = m
                if cls not in classes:
                    skipped["class not in binary"] += 1
                    continue
                cva, ro = classes[cls]
                if kind == "+":
                    receivers = [cva]
                    meta = W.rd(cva)
                    data = W.rd(meta + 16) & ~3
                    mro = data if data < CALL_HEAP_LO else W.rd(data + 8)
                    sel = W.method_sel(mro, selname)
                else:
                    receivers = [o for c in family(cls) if c in classes for o in objs.get(classes[c][0], [])]
                    sel = W.method_sel(ro, selname)
                fabricated = False
                if not receivers:
                    # no live object anywhere: a FABRICATED receiver (zeroed
                    # instance of the class's size, isa = class) - weakest evidence,
                    # tagged in the row (receiver "fabricated:...")
                    receivers, fabricated = [CALL_FAKE_OBJ], True
                    skipped["fabricated receiver"] += 1
                args = [(t, o) for t, o in _objc_types(enc)[3:]]
            else:
                proto = fn["proto"]
                inner = proto[proto.index("(") + 1:proto.rindex(")")]
                ps = [x.strip() for x in inner.split(",")] if inner.strip() not in ("", "void") else []
                if "__thiscall" in proto:
                    cm = re.search(r"\((\w+) \*this", proto)
                    receivers = W.cpp_this(cm.group(1), objs) if cm else []
                    if not receivers:
                        skipped["C++ method: no live this"] += 1
                        continue
                    ps = ps[1:]
                args = [(re.sub(r"\s*\w+$", "", x) if re.search(r"[\w*]\s+\**\w+$", x) else x, None) for x in ps]
        except (MemoryError, struct.error, ValueError, IndexError) as e:
            skipped["setup: %s" % str(e)[:40]] += 1
            continue
        n = nlive = nbad = 0
        for recv in receivers:
            vecs = CALL_VECTORS + ((("live", 1, 1.0),) if (m and m[1] == "-" and args) else ()) + \
                ((("caller", 1, 1.0),) if (m and a in cargs) else ())
            for vname, ival, fval in vecs:
                if (n >= per_fn and vname not in ("live", "caller")) or (vname in ("live", "caller") and nlive >= 4):
                    continue
                scr = iter(range(CALL_SCRATCH, CALL_SCRATCH + 0x100000, 0x1000))
                try:
                    words = []
                    if vname == "caller":
                        try:
                            cw = _caller_words(W, cargs[a], objs, classes, ivars)
                        except (MemoryError, struct.error):
                            cw = None
                        if cw is None:
                            break
                        words = [recv, sel] + cw
                    elif vname == "live":
                        try:
                            rcls = va2cls.get(W.rd(recv))
                        except (MemoryError, struct.error):
                            rcls = None
                        lw = None
                        if recv != CALL_FAKE_OBJ:
                            lw = _live_words(W, recv, _ancestors(rcls or m[0]), ivars, m[2], args)
                        else:
                            # donor: a live object of the nearest ancestor family
                            for anc in _ancestors(m[0]):
                                if anc not in classes:
                                    break
                                for c in family(anc):
                                    for o in objs.get(classes[c][0], []) if c in classes else []:
                                        lw = _live_words(W, o, _ancestors(c), ivars, m[2], args)
                                        if lw is not None:
                                            break
                                    if lw is not None:
                                        break
                                if lw is not None:
                                    break
                        if lw is None:
                            break
                        words = [recv, sel] + lw
                    elif m:
                        words = [recv, sel]
                        for t, o in args:
                            ws = _arg_words(t, ival, fval, scr)
                            if o is not None:
                                while len(words) < o // 4:
                                    words.append(0)
                            words += ws
                    else:
                        if recv is not None:
                            words = [recv]
                        for t, _ in args:
                            words += _c_arg_words(t, ival, fval, scr)
                except ValueError as e:
                    skipped["args: %s" % str(e)[:40]] += 1
                    break
                regs = list(snap.regs)
                for i in range(4):
                    regs[i] = words[i] if i < len(words) else 0
                regs[13] = sp
                pristine = {}
                for p in range(CALL_SCRATCH, CALL_SCRATCH + 0x8000, 0x1000):
                    pristine[p] = bytes(0x1000)
                if m and recv == CALL_FAKE_OBJ:
                    pristine[CALL_FAKE_OBJ] = struct.pack("<I", classes[m[0]][0]) + bytes(0x1000 - 4)
                stack = words[4:]
                if stack:
                    page = sp & ~0xfff
                    buf = bytearray(W.page(page))
                    nxt = bytearray(W.page(page + 0x1000)) if (sp & 0xfff) + 4 * len(stack) > 0x1000 else None
                    for i, wv in enumerate(stack):
                        a2 = sp + 4 * i
                        tgt = buf if a2 < page + 0x1000 else nxt
                        struct.pack_into("<I", tgt, a2 & 0xfff, wv & 0xffffffff)
                    pristine[page] = bytes(buf)
                    if nxt is not None:
                        pristine[page + 0x1000] = bytes(nxt)
                row = {"capture": tag, "source": "synthetic", "addr": fn["addr"], "name": fn["name"],
                       "receiver": ("fabricated:%s" % m[0]) if (m and recv == CALL_FAKE_OBJ) else ("0x%x" % recv if recv else None),
                       "args": vname, "fp": L.get("fp"),
                       "hv": D.HARNESS}
                try:
                    v, det, ra, rb = D.run_compare(fn, pristine, W.page, regs, a | (1 if fn["thumb"] else 0),
                                                   fn["thumb"], L, tid=snap.tid, fpscr=snap.fpscr)
                    row.update(verdict=v, detail=det, insns_orig=ra.insns)
                    if v == "pass" and ra.covered:
                        row["cov"] = D.cov_encode(ra.covered, a)
                except Exception as e:
                    row.update(verdict="untestable", detail="harness exception: %s" % str(e)[:160])
                rows.append(row)
                # an untestable call (e.g. a stray isa match that is no real
                # object, NULL fields) does not use up the budget: the next
                # receiver is tried (LOG 2026-10-09)
                if row["verdict"] == "untestable":
                    nbad += 1
                    if nbad > 12:
                        break
                    continue
                if vname in ("live", "caller"):
                    nlive += 1
                else:
                    n += 1
    return {"capture": tag, "objects": sum(len(v) for v in objs.values()), "skipped": dict(skipped)}, rows


def cmd_calls(a):
    """Synthetic calls (V5) for the functions the ledger has not proven."""
    import multiprocessing
    import mgst_difftest as D
    global DIFF_FUNCS, DIFF_LINKED
    DIFF_FUNCS = D.init_link()
    # targets: every function no NATURAL call reached (independent of earlier
    # synthetic results, so a rerun never drops a function it proved before),
    # plus --also verdict classes from the natural results (e.g. untestable)
    natural = {}
    import glob
    cdir = os.path.join(ROOT, "recovered/compile")
    for path in [os.path.join(cdir, "difftest_offline.jsonl")] + glob.glob(os.path.join(cdir, "difftest_frames*.jsonl")):
        if os.path.exists(path):
            for l in open(path):
                r = json.loads(l)
                v = natural.setdefault(int(r["addr"], 16), set())
                v.add(r["verdict"])
    also = set(x for x in a.also.split(",") if x)
    targets = sorted(fa for fa in DIFF_FUNCS
                     if fa not in natural or (also and natural[fa] <= also))
    if a.only:
        targets = sorted({int(x, 16) for x in a.only} & set(DIFF_FUNCS))
    DIFF_LINKED = {}
    for fa in targets:
        try:
            L = D.link(DIFF_FUNCS[fa])
        except Exception:
            L = None
        if L and "error" not in L:
            DIFF_LINKED[fa] = L
    tasks = []
    for d in a.dirs:
        snaps = [off for off, s in Capture(d).samples(with_offset=True) if s.status == 4]
        if not snaps:
            continue
        pick = sorted({snaps[int(i * (len(snaps) - 1) / max(1, a.per_dir - 1))] for i in range(a.per_dir)})
        tasks += [(d, off, targets, a.per_fn) for off in pick]
    print("calls: %d target function(s) (unreached%s), %d linked, %d snapshot(s)" % (
        len(targets), " + only " + a.also if also else "", len(DIFF_LINKED), len(tasks)), flush=True)
    out = open(a.out, "w")
    verdicts = collections.Counter()
    with multiprocessing.get_context("fork").Pool(a.jobs) as pool:
        for info, rows in pool.imap_unordered(_calls_one, tasks):
            for r in rows:
                out.write(json.dumps(r) + "\n")
                verdicts[r["verdict"]] += 1
            out.flush()
            print("  %s: %d objects, %d tests, skipped %s" % (
                info["capture"], info["objects"], len(rows), info["skipped"]), flush=True)
    out.close()
    print("calls done: %s -> %s" % (dict(verdicts), a.out))


def cmd_link(a):
    """Link every function (writes fn/<addr>.{bin,fp}); prints the count."""
    import mgst_difftest as D
    funcs = D.init_link()
    ok = 0
    for fa, fn in sorted(funcs.items()):
        try:
            L = D.link(fn)
        except Exception:
            L = None
        ok += bool(L and "error" not in L)
    print("linked %d / %d" % (ok, len(funcs)))


def stale_functions():
    """Functions whose every result row tested an older build (fingerprint
    differs from fn/<addr>.fp)."""
    import glob
    cdir = os.path.join(ROOT, "recovered/compile")
    import mgst_difftest as D
    cur, rows = {}, collections.defaultdict(set)
    oldfail, newhv = set(), set()
    for f in glob.glob(os.path.join(cdir, "fn", "*.fp")):
        cur[os.path.basename(f)[:-3]] = open(f).read().strip()
    for pat in ("difftest_offline*.jsonl", "difftest_frames*.jsonl", "difftest_calls*.jsonl"):
        for path in glob.glob(os.path.join(cdir, pat)):
            for l in open(path):
                r = json.loads(l)
                k = r["addr"]
                rows[k].add(r.get("fp"))
                if r.get("fp") == cur.get(k):
                    if r.get("hv", 1) >= D.HARNESS:
                        newhv.add(k)
                    elif r["verdict"] in ("fail", "untestable"):
                        oldfail.add(k)          # a newer harness may decide it
    # a newer harness is retried only where the ledger has no decision yet
    # (not proven, not V0): an already-proven function's old untestable rows
    # do not need it - that rule made the 2026-10-09 refresh run 3h45m
    decided = set()
    st = os.path.join(ROOT, "analysis/verification/function_status.tsv")
    if os.path.exists(st):
        for l in open(st):
            p = l.rstrip("\n").split("\t")
            if p[0].startswith("0x") and len(p) > 5 and (p[4] == "pass" or p[5]):
                decided.add(p[0])
    # stale: no row for the current build; or a failure seen only by an older harness
    return sorted(k for k, fps in rows.items() if k in cur and (
        cur[k] not in fps or (k in oldfail and k not in newhv and k not in decided)))


def cmd_refresh(a):
    """Re-test only the functions whose results are stale (their recompiled
    binary changed since they were tested): per-call diff, frame driver and
    synthetic calls, each into its own difftest_*_refresh_<stamp>.jsonl."""
    import subprocess
    import time
    if not a.no_link:
        cmd_link(a)
    st = stale_functions()
    print("refresh: %d stale function(s)" % len(st), flush=True)
    if not st:
        return
    stamp = time.strftime("%Y%m%d_%H%M%S")
    cdir = os.path.join(ROOT, "recovered/compile")
    snap = os.path.abspath(__file__)
    dirs = sorted(d for d in (os.path.join(ROOT, "oracle/reports/snap", x)
                              for x in os.listdir(os.path.join(ROOT, "oracle/reports/snap"))) if os.path.isdir(d))
    caps = [d for d in dirs if not (d.endswith("_dump") or "_dump_" in os.path.basename(d) or "menutour" in d)]
    dumps = [d for d in dirs if d not in caps]
    j = str(a.jobs)
    # changed code is re-validated on a spread of states, not every snapshot
    steps = [("offline", ["diff"] + caps), ("frames", ["frames"] + dumps + ["--per-dir", str(a.per_dir)]),
             ("calls", ["calls"] + dumps)]
    for name, args in steps:
        out = os.path.join(cdir, "difftest_%s_refresh_%s.jsonl" % (name, stamp))
        cmd = [sys.executable, snap] + args + ["--only"] + st + ["--jobs", j, "--out", out]
        print("refresh: %s -> %s" % (name, os.path.basename(out)), flush=True)
        subprocess.run(cmd, stdout=subprocess.DEVNULL)
    print("refresh done; still stale: %d" % len(stale_functions()))


_FN_CACHE = {}


def _fn_of(d, off):
    cap = _FN_CACHE.get(d)
    if cap is None:
        cap = _FN_CACHE[d] = Capture(d)
    return struct.unpack_from("<I", cap._data(), off + 8)[0]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stats")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--missing", action="store_true", help="list functions without an ok sample")
    p = sub.add_parser("replay")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--only", nargs="*")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--out", help="jsonl results")
    p.add_argument("-v", "--verbose", action="store_true")
    p = sub.add_parser("diff")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--only", nargs="*")
    p.add_argument("--jobs", type=int, default=os.cpu_count())
    p.add_argument("--per-fn", type=int, default=6, help="samples per function (diverse hits first)")
    p.add_argument("--out", default=os.path.join(ROOT, "recovered/compile/difftest_offline.jsonl"))
    p = sub.add_parser("frames")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--frames", type=int, default=30)
    p.add_argument("--per-fn", type=int, default=3, help="tests per function per snapshot")
    p.add_argument("--max-insns", type=int, default=60_000_000, help="per frame")
    p.add_argument("--only", nargs="*", help="test only these function addresses (hex)")
    p.add_argument("--per-dir", type=int, default=0, help="at most N snapshots per directory (even spread; 0 = all)")
    p.add_argument("--jobs", type=int, default=os.cpu_count())
    p.add_argument("--out", default=os.path.join(ROOT, "recovered/compile/difftest_frames.jsonl"))
    p = sub.add_parser("calls", help="synthetic calls on harvested objects (V5)")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--also", default="untestable", help="also target functions whose natural results are only these verdicts (comma list, e.g. untestable)")
    p.add_argument("--per-dir", type=int, default=2, help="snapshots per directory (spread)")
    p.add_argument("--only", nargs="*", help="call only these function addresses (hex), reached or not")
    p.add_argument("--per-fn", type=int, default=3, help="calls per function per snapshot")
    p.add_argument("--jobs", type=int, default=os.cpu_count())
    p.add_argument("--out", default=os.path.join(ROOT, "recovered/compile/difftest_calls.jsonl"))
    p = sub.add_parser("link", help="link every function (fn/<addr>.bin/.fp)")
    p = sub.add_parser("refresh", help="re-test only functions whose results are for an older build")
    p.add_argument("--jobs", type=int, default=os.cpu_count())
    p.add_argument("--no-link", action="store_true")
    p.add_argument("--per-dir", type=int, default=3, help="frame-driver snapshots per directory")
    a = ap.parse_args()
    {"stats": cmd_stats, "replay": cmd_replay, "diff": cmd_diff, "frames": cmd_frames,
     "calls": cmd_calls, "link": cmd_link, "refresh": cmd_refresh}[a.cmd](a)


if __name__ == "__main__":
    main()
