"""
Process-identity-gated breakpoints and watchpoints for MGST on the oracle.

Load inside gdb (it is a gdb Python script, not a standalone program):

    gdb -q -batch -x tools/mgst_gdb.py -ex 'mgst-connect' \
        -ex 'mgst-watch 0x75ae8 rw field3' -ex 'mgst-run'

WHY THIS EXISTS
---------------
QEMU's gdbstub breakpoints and watchpoints are keyed on VIRTUAL address, and
on iOS 3.1.3 every process shares the same un-ASLR'd layout: SpringBoard has
its own code at 0x2xxxx and its own __DATA at 0x75adc, exactly like MGSTUS.
A bare `rwatch *0x75ae8` therefore fires for whichever process touches
that VA, and one stray hit from another process is enough to "find" a reader
that does not exist in MGST. This is the same TTBR0 identity trap
mgst_probe.py and contrib/plugins/drcov_mgst.c guard against (LOG AUDIT
2026-09-27, STEP 5 2026-09-28).

Every hit here runs the SAME identity check as those two: gdb reads the
32-byte Mach-O header at VA 0x1000 through the stopped vCPU's MMU (= the
process that made the access) and compares it with the reference MGSTUS
file. A hit only counts if it matches. Either way it is logged, then gdb
auto-continues (stop() returns False), so the game keeps running and this
acts as a tracer rather than a debugger.

COMMANDS
--------
    mgst-connect [host:port]           target remote (default :1234)
    mgst-break ADDR [label [EXPR;EXPR..]]
                                       gated breakpoint. Optional gdb
                                       expressions (';'-separated, evaluated
                                       at the hit, e.g. '$r3;*(int*)($r2+8)')
                                       are logged as hex in the `extra` column
    mgst-watch ADDR r|w|rw [label] [len]
                                       gated watchpoint(s): r=read, w=write,
                                       rw=separate read AND write watchpoints,
                                       so the log says which kind each hit was
    mgst-run [seconds]                 continue, log hits; SIGINT or the
                                       timeout stops, then DETACHES (never
                                       kills: a 'k' packet terminates QEMU)
    mgst-summary                       per-label counts, match vs rejected

Env: MGST_REF_EXE (default v2.3.0), MGST_FUNCMAP (default
analysis/symbols/function_map.csv), MGST_GDB_LOG (default
oracle/reports/gdb_hits_<ts>.tsv).

READ vs WRITE, and the reported PC
----------------------------------
QEMU reports gdb watchpoint hits AFTER the accessing instruction completes,
so $pc is the next instruction. The log records $pc and $lr as-is and
symbolises $pc to the enclosing function. Function-level attribution is
reliable; instruction-level needs `x/3i $pc-6` by hand.
"""
import bisect
import random
import csv
import os
import signal
import subprocess
import sys
import threading
import time

import gdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_EXE = os.environ.get(
    "MGST_REF_EXE",
    os.path.join(ROOT, "work/extracted/Payload/MGSTUS.app/MGSTUS"))
FUNCMAP = os.environ.get(
    "MGST_FUNCMAP", os.path.join(ROOT, "analysis/symbols/function_map.csv"))
LOG_PATH = os.environ.get(
    "MGST_GDB_LOG",
    os.path.join(ROOT, "oracle/reports/gdb_hits_%s.tsv"
                 % time.strftime("%Y%m%d_%H%M%S")))

with open(REF_EXE, "rb") as f:
    REF_HEADER = f.read(32)

_addrs, _names = [], []
if os.path.exists(FUNCMAP):
    with open(FUNCMAP) as f:
        rows = sorted((int(r["address"], 16), r["function"])
                      for r in csv.DictReader(f))
    _addrs = [a for a, _ in rows]
    _names = [n for _, n in rows]


def symbolize(pc):
    pc &= ~1
    i = bisect.bisect_right(_addrs, pc) - 1
    if i < 0:
        return "?"
    return "%s+0x%x" % (_names[i], pc - _addrs[i])


def is_mgst():
    try:
        got = bytes(gdb.selected_inferior().read_memory(0x1000, 32))
    except gdb.MemoryError:
        return False
    return got == REF_HEADER


def reg(name):
    return int(gdb.parse_and_eval("$" + name)) & 0xffffffff


_log = None
counts = {}   # label -> [matched, rejected]


def eval_extra(exprs):
    out = []
    for e in exprs:
        try:
            out.append("0x%x" % (int(gdb.parse_and_eval(e)) & 0xffffffff))
        except (gdb.error, gdb.MemoryError):
            out.append("?")
    return ",".join(out)


def log_hit(kind, label, addr, matched, exprs=()):
    global _log
    if _log is None:
        _log = open(LOG_PATH, "w", buffering=1)
        _log.write("time\tkind\tlabel\taddr\tmgst\tpc\tfunc\tlr\tlr_func\tvalue\textra\n")
    c = counts.setdefault(label, [0, 0])
    c[0 if matched else 1] += 1
    pc, lr = reg("pc"), reg("lr")
    val = ""
    if addr is not None:
        try:
            val = "0x%08x" % int.from_bytes(
                bytes(gdb.selected_inferior().read_memory(addr, 4)), "little")
        except gdb.MemoryError:
            val = "?"
    extra = eval_extra(exprs) if matched else ""
    _log.write("%.3f\t%s\t%s\t0x%x\t%d\t0x%08x\t%s\t0x%08x\t%s\t%s\t%s\n" % (
        time.time(), kind, label, addr if addr is not None else pc,
        1 if matched else 0, pc,
        symbolize(pc) if matched else "-", lr,
        symbolize(lr) if matched else "-", val, extra))


class GatedBreakpoint(gdb.Breakpoint):
    def __init__(self, spec, kind, label, addr, exprs=(), **kw):
        super().__init__(spec, internal=False, **kw)
        self.kind, self.label, self.addr = kind, label, addr
        self.exprs = [e for e in exprs if e.strip()]

    def stop(self):
        log_hit(self.kind, self.label, self.addr, is_mgst(), self.exprs)
        return False   # tracer: always auto-continue


class MgstConnect(gdb.Command):
    """mgst-connect [host:port] - attach to the oracle's gdbstub."""
    def __init__(self):
        super().__init__("mgst-connect", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        gdb.execute("set confirm off")
        # Async target: `continue` returns at once under -batch, and the next
        # command dies with "target is running", skipping detach and leaving
        # QEMU halted in 'debug' state (measured 2026-09-28).
        gdb.execute("maint set target-async off")
        gdb.execute("set pagination off")
        gdb.execute("set architecture arm")
        gdb.execute("set remote hardware-watchpoint-limit unlimited",
                    to_string=True)
        gdb.execute("target remote %s" % (arg.strip() or ":1234"))
        print("mgst: connected; stopped context is MGSTUS: %s" % is_mgst())
        print("mgst: logging hits to %s" % LOG_PATH)


class MgstBreak(gdb.Command):
    """mgst-break ADDR [label [EXPR;EXPR..]]"""
    def __init__(self):
        super().__init__("mgst-break", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        a = arg.split()
        addr = int(a[0], 0)
        label = a[1] if len(a) > 1 else hex(addr)
        exprs = " ".join(a[2:]).split(";")
        GatedBreakpoint("*0x%x" % addr, "exec", label, None, exprs,
                        type=gdb.BP_HARDWARE_BREAKPOINT
                        if hasattr(gdb, "BP_HARDWARE_BREAKPOINT")
                        else gdb.BP_BREAKPOINT)
        print("mgst: gated breakpoint %s at 0x%x" % (label, addr))


class MgstWatch(gdb.Command):
    """mgst-watch ADDR r|w|rw [label] [len]"""
    def __init__(self):
        super().__init__("mgst-watch", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        a = arg.split()
        addr = int(a[0], 0)
        mode = a[1] if len(a) > 1 else "rw"
        label = a[2] if len(a) > 2 else hex(addr)
        ln = int(a[3], 0) if len(a) > 3 else 4
        ctype = {1: "char", 2: "short", 4: "int"}.get(ln, "int")
        spec = "*(%s *)0x%x" % (ctype, addr)
        if "r" in mode:
            GatedBreakpoint(spec, "read", label, addr,
                            type=gdb.BP_WATCHPOINT, wp_class=gdb.WP_READ)
        if "w" in mode:
            GatedBreakpoint(spec, "write", label, addr,
                            type=gdb.BP_WATCHPOINT, wp_class=gdb.WP_WRITE)
        print("mgst: gated %s watchpoint %s at 0x%x" % (mode, label, addr))


ENEMY_DATA_PTR = 0x75ad8     # _enemy_data: EneDat * (0x2fc each; hostages live in npcData, not here)
ENEMY_MAX = 0x84d6c          # +[Stage getEnemyMax]
BLEED = {"period": 0.0, "pct": 0}


def bleed_tick():
    """Periodic, breakpoint-free HP drain over the whole enemy_data array, for
    enemies that sit in one AI state (e.g. Mantis waiting in her aiStep 2):
    their own code reacts (hp < 1 checks, Mantis successionHP-hp > 4 stage
    change). Only applied when the interrupted context IS MGSTUS."""
    if not is_mgst():
        counts.setdefault("bleed-skip(not MGST)", [0, 0])[1] += 1
        return
    base = int(gdb.parse_and_eval("*(unsigned int *)0x%x" % ENEMY_DATA_PTR)) & 0xffffffff
    n = int(gdb.parse_and_eval("*(int *)0x%x" % ENEMY_MAX))
    if not base or not (0 < n <= 128):
        return
    for i in range(n):
        e = base + i * 0x2fc
        hp = int(gdb.parse_and_eval("*(int *)0x%x" % e))
        mx = int(gdb.parse_and_eval("*(int *)0x%x" % (e + 4)))
        if hp > 0 and mx > 0:
            gdb.execute("set *(int *)0x%x = %d" % (e, max(0, hp - max(1, mx * BLEED["pct"] // 100))))
    counts.setdefault("bleed-tick", [0, 0])[0] += 1


class MgstBleed(gdb.Command):
    """mgst-bleed PERIOD PCT - every PERIOD s mgst-run interrupts the VM and every
    live enemy in enemy_data loses PCT% of max HP (no breakpoint involved)."""
    def __init__(self):
        super().__init__("mgst-bleed", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        a = arg.split()
        BLEED["period"], BLEED["pct"] = float(a[0]), int(a[1])
        print("mgst: bleed %d%% every %.0fs" % (BLEED["pct"], BLEED["period"]))


class MgstRun(gdb.Command):
    """mgst-run [seconds] - continue; stop on SIGINT/timeout; then detach.
    With mgst-bleed configured, a private timer interrupts every PERIOD s to
    run bleed_tick(); any OTHER SIGINT (Ctrl-C, the campaign script ending a
    chunk) still ends the run."""
    def __init__(self):
        super().__init__("mgst-run", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        secs = float(arg) if arg.strip() else 0
        end = time.time() + secs if secs else None
        tick = {"ours": False}

        def fire():
            tick["ours"] = True
            os.kill(os.getpid(), signal.SIGINT)

        try:
            while True:
                left = (end - time.time()) if end else None
                if left is not None and left <= 0:
                    break
                wait = BLEED["period"] if BLEED["period"] else left
                if left is not None and wait is not None:
                    wait = min(wait, left)
                t = None
                if wait:
                    tick["ours"] = False
                    t = threading.Timer(wait, fire)
                    t.daemon = True
                    t.start()
                try:
                    gdb.execute("continue")
                except (gdb.error, KeyboardInterrupt) as e:
                    print("mgst: continue ended: %s" % e)
                if t:
                    t.cancel()
                if not tick["ours"]:
                    break                     # external interrupt: end the run
                if BLEED["period"] and (end is None or time.time() < end):
                    bleed_tick()
        finally:
            try:
                gdb.execute("mgst-summary")
                gdb.execute("delete")
            finally:
                gdb.execute("detach")
            print("mgst: detached - QEMU keeps running")


class MgstSummary(gdb.Command):
    """mgst-summary"""
    def __init__(self):
        super().__init__("mgst-summary", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        print("mgst: %-14s %9s %9s" % ("label", "MGSTUS", "rejected"))
        for k in sorted(counts):
            print("mgst: %-14s %9d %9d" % (k, counts[k][0], counts[k][1]))
        print("mgst: log %s" % LOG_PATH)


class ActionBreakpoint(GatedBreakpoint):
    """Gated breakpoint that runs gdb `set` commands on MGSTUS hits only.

    shots = how many matching hits apply the actions (0 = every hit)."""
    def __init__(self, addr, label, actions, shots=0):
        super().__init__("*0x%x" % addr, "exec", label, None,
                         type=gdb.BP_HARDWARE_BREAKPOINT
                         if hasattr(gdb, "BP_HARDWARE_BREAKPOINT")
                         else gdb.BP_BREAKPOINT)
        self.actions, self.shots, self.done = actions, shots, 0

    def stop(self):
        matched = is_mgst()
        log_hit(self.kind, self.label, None, matched, ["$r2"])
        if matched and (self.shots == 0 or self.done < self.shots):
            for a in self.actions:
                gdb.execute(a)
            self.done += 1
            print("mgst: %s applied (%d): %s" % (self.label, self.done, "; ".join(self.actions)))
        return False


STAGE_SETNUM = 0x3f0ec     # +[Stage setNum:]  (r2 = stage, 1..29 accepted)
STAGE_SETSUB = 0x3f134     # +[Stage setSubNum:]


class MgstStage(gdb.Command):
    """mgst-stage N - the next MGSTUS call to +[Stage setNum:] gets N instead."""
    def __init__(self):
        super().__init__("mgst-stage", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        n = int(arg, 0)
        ActionBreakpoint(STAGE_SETNUM, "stage->%d" % n, ["set $r2 = %d" % n], shots=1)


class MgstSubstage(gdb.Command):
    """mgst-substage N - the next MGSTUS call to +[Stage setSubNum:] gets N
    instead (stage start calls setSubNum:0): start a boss stage in a later
    phase (LOG 2026-10-08: 900 s runs never left sub-stage 0)."""
    def __init__(self):
        super().__init__("mgst-substage", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        n = int(arg, 0)
        ActionBreakpoint(STAGE_SETSUB, "substage->%d" % n, ["set $r2 = %d" % n], shots=1)


PLAYER_INITHP = 0x387e0     # +[Player initHP:] (r2 = max HP)
SURVIVAL_FLG_OFF = 53080    # CrashLandingAppDelegate.survival_flg (ivars.tsv)


class _OneShotGameScene(gdb.Breakpoint):
    """First MGSTUS -[CrashLandingAppDelegate GameScene] entry: run actions
    with $r0 = self, then disable itself (a live per-frame breakpoint would
    slow QEMU 10-30x)."""
    def __init__(self, actions):
        super().__init__("*0x%x" % GAMESCENE_ADDR, internal=False)
        self.actions = actions

    def stop(self):
        if not is_mgst():
            return False
        for a in self.actions:
            gdb.execute(a)
        print("mgst: survival applied: %s" % "; ".join(self.actions), flush=True)
        self.enabled = False
        return False


class MgstSurvival(gdb.Command):
    """mgst-survival [MAXHP] - play the stage in Survival mode (LOG 2026-10-10,
    test-coverage targets): survival_flg := 1 at the first GameScene; with
    MAXHP, every +[Player initHP:] gets MAXHP (the Survival save/continue code
    branches on getMaxHP == 8)."""
    def __init__(self):
        super().__init__("mgst-survival", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        _OneShotGameScene(["set *(unsigned char *)($r0 + %d) = 1" % SURVIVAL_FLG_OFF])
        if arg.strip():
            hp = int(arg, 0)
            ActionBreakpoint(PLAYER_INITHP, "initHP->%d" % hp, ["set $r2 = %d" % hp])


PLAYER_SETDAMAGE = 0x3d448  # +[Player setDamage:::] (r2 = damage; HP 0x84b44, max 0x84b48)


class MgstGodmode(gdb.Command):
    """mgst-godmode - Snake never dies, but HP stays in its real range.

    On every +[Player setDamage:::] entry: HP := max HP, damage := min(damage,
    max-1). Hit reactions still run. (v1 raised initHP to 30000; the result
    screen then indexed its number textures out of range and MGST crashed in
    sh_drawResult_Clear -> +[TextureManager StringdrawImage], LOG STEP 5.)"""
    def __init__(self):
        super().__init__("mgst-godmode", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        ActionBreakpoint(PLAYER_SETDAMAGE, "godmode", [
            "set *(int *)0x84b44 = *(int *)0x84b48",
            "set $r2 = ((int)$r2 >= *(int *)0x84b48) ? *(int *)0x84b48 - 1 : $r2"])


HIT_TEST_EXIT = 0x2cf24    # -[EnemyBase checkCollisionWithBullet:hit:distance:] epilogue
                           # (r0 = result, 2 = hit; r6 = self; [sp+0x10] = char hit[3])
DMG_RANGE_GATE = 0x2dc6e   # checkCollisionWithBullet_Dmg: `cmp r3,#2` on pEneDat->distance
                           # (distance > 2 with the M4 = out of range, SVD needed)

_classes = {}
_ctsv = os.path.join(ROOT, "analysis/objc/classes.tsv")
if os.path.exists(_ctsv):
    with open(_ctsv) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            _classes[int(r["class_va"], 16)] = (r["class"], r["super"])


def is_enemy_class(name):
    """EnemyBase descendants, excluding NPC (hostages - hitting them is a penalty)."""
    by_name = {v[0]: v[1] for v in _classes.values()}
    while name and name != "?":
        if name == "NPC":
            return False
        if name == "EnemyBase":
            return True
        name = by_name.get(name)
    return False


def class_of(reg_name):
    try:
        isa = int(gdb.parse_and_eval("*(unsigned int *)$%s" % reg_name)) & 0xffffffff
    except (gdb.error, gdb.MemoryError):
        return "?"
    return _classes.get(isa, ("0x%x" % isa, ""))[0]


G_DEVICE_SHAKE = 0x80f30
SHAKE_EVERY = int(os.environ.get("MGST_SHAKE_EVERY", "40"))


class AutoHit(gdb.Breakpoint):
    """Every EnemyBase bullet test on an enemy (not a hostage) reports a hit."""
    def __init__(self):
        super().__init__("*0x%x" % HIT_TEST_EXIT, internal=False,
                         type=gdb.BP_HARDWARE_BREAKPOINT
                         if hasattr(gdb, "BP_HARDWARE_BREAKPOINT") else gdb.BP_BREAKPOINT)
        self.n = 0
        self.per_class = {}

    def stop(self):
        if not is_mgst():
            return False
        cls = class_of("r6")
        if is_enemy_class(cls):
            hitp = int(gdb.parse_and_eval("*(unsigned int *)($sp + 0x10)")) & 0xffffffff
            # random part per hit: hit[0] body, hit[1] head, hit[2] legs/armor.
            # A per-call rotation (n % 3) aliased with the number of enemies
            # tested per shot - with 3 Gekkos each always got the same part and
            # none ever died (M17 stalled; Gekko needs legs, then head once
            # collapsed: -[Gekko calculateDamage:::::] 0x31138).
            k = random.randrange(3)
            if cls == "Gekko":
                # legs until it collapses (anime_no 2/7), then the head
                ene = int(gdb.parse_and_eval("*(unsigned int *)($r6 + 12)")) & 0xffffffff
                anim = int(gdb.parse_and_eval("*(int *)0x%x" % (ene + 212)))
                k = 1 if anim in (2, 7) else 2
            gdb.execute("set *(unsigned char *)0x%x = 1" % (hitp + k))
            gdb.execute("set $r0 = 2")
            self.n += 1
            self.per_class[cls] = self.per_class.get(cls, 0) + 1
            counts.setdefault("autohit:" + cls, [0, 0])[0] += 1
            if SHAKE_EVERY and self.n % SHAKE_EVERY == 0:
                # g_DeviceShake: what -[.. accelerometer:didAccelerate:] sets
                # above 2.1 g; clears frozen screens (M13/M14) and steals the
                # doll back from Mantis. Piggybacked here because a per-frame
                # breakpoint slowed the game ~10x.
                gdb.execute("set *(unsigned char *)0x%x = 1" % G_DEVICE_SHAKE)
                counts.setdefault("shake", [0, 0])[0] += 1
        return False


class RangeGate(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x%x" % DMG_RANGE_GATE, internal=False,
                         type=gdb.BP_HARDWARE_BREAKPOINT
                         if hasattr(gdb, "BP_HARDWARE_BREAKPOINT") else gdb.BP_BREAKPOINT)

    def stop(self):
        if is_mgst():
            gdb.execute("set $r3 = 0")
            counts.setdefault("rangegate", [0, 0])[0] += 1
        return False


DMG_ENTRY = 0x2dc3c        # -[EnemyBase checkCollisionWithBullet_Dmg:weaponType:damage:]
                           # r0 = self, r3 = weaponType (2 = missile -> hitMissile:)
MISSILE_CLASSES = set(os.environ.get("MGST_MISSILE_CLASSES", "Canard").split(","))


class MissileGate(gdb.Breakpoint):
    """Enemies only missiles can kill (M10: Canard choppers need a KERO-TAN
    missile) get every shot as weaponType 2, so the real missile path runs."""
    def __init__(self):
        super().__init__("*0x%x" % DMG_ENTRY, internal=False,
                         type=gdb.BP_HARDWARE_BREAKPOINT
                         if hasattr(gdb, "BP_HARDWARE_BREAKPOINT") else gdb.BP_BREAKPOINT)

    def stop(self):
        if is_mgst():
            cls = class_of("r0")
            if cls in MISSILE_CLASSES:
                gdb.execute("set $r3 = 2")
                counts.setdefault("missile:" + cls, [0, 0])[0] += 1
        return False


DOLL_HIT_TEST = 0x57eb8    # -[Doll checkCollisionWithBullet_Dmg:..]: `cmp r0,#0` right after
                           # [self checkCollision:withRect:] (0x57eb4, runtime: always Doll)


class DollGate(gdb.Breakpoint):
    """Mantis's dolls (M18) are hit through their own per-part geometry test,
    not EnemyBase's; force it so the real fall / pick-up / steal code runs."""
    def __init__(self):
        super().__init__("*0x%x" % DOLL_HIT_TEST, internal=False,
                         type=gdb.BP_HARDWARE_BREAKPOINT
                         if hasattr(gdb, "BP_HARDWARE_BREAKPOINT") else gdb.BP_BREAKPOINT)

    def stop(self):
        if is_mgst():
            gdb.execute("set $r0 = 1")
            counts.setdefault("doll", [0, 0])[0] += 1
        return False


class MgstAutohit(gdb.Command):
    """mgst-autohit - every shot hits every active enemy (range gate bypassed)."""
    def __init__(self):
        super().__init__("mgst-autohit", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        AutoHit()
        RangeGate()
        MissileGate()
        DollGate()
        print("mgst: autohit armed (%d classes known)" % len(_classes))


class EveryBreakpoint(gdb.Breakpoint):
    def __init__(self, addr, period, actions):
        super().__init__("*0x%x" % addr, internal=False,
                         type=gdb.BP_HARDWARE_BREAKPOINT
                         if hasattr(gdb, "BP_HARDWARE_BREAKPOINT") else gdb.BP_BREAKPOINT)
        self.period, self.actions, self.n, self.label = period, actions, 0, "every@0x%x" % addr

    def stop(self):
        if is_mgst():
            self.n += 1
            if self.n % self.period == 0:
                for a in self.actions:
                    gdb.execute(a)
                counts.setdefault(self.label, [0, 0])[0] += 1
        return False


class MgstEvery(gdb.Command):
    """mgst-every ADDR N CMD[;CMD..] - on every Nth MGSTUS hit of ADDR run the gdb commands.
    Shake (FullScreenEffect proc reads g_DeviceShake 0x80f30):
        mgst-every 0x35b84 150 set *(char *)0x80f30 = 1"""
    def __init__(self):
        super().__init__("mgst-every", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        a = arg.split(None, 2)
        EveryBreakpoint(int(a[0], 0), int(a[1], 0), [c.strip() for c in a[2].split(";")])


SET_AICONTROL = 0x2c92c    # -[EnemyBase setAiControl:] r0 = self, r2 = new state (10 = die)
OFF_PENEDAT = 12           # EnemyBase.pEneDat (analysis/objc/ivars.tsv)


class DrainBreakpoint(gdb.Breakpoint):
    """State injection, no gameplay: whenever an enemy's AI changes state it
    loses PCT% of its max HP (EneDat.param.hp). When that reaches 0 the
    argument is rewritten to 10, so the GAME executes setAiControl:10 - the
    same die state its hit handler sets. HP-threshold boss phases (Ray 60/20%,
    Liquid 25%, Raven, Mantis successionHP ...) are passed on the way down.
    Hostages (NPC) are never touched.

    v1 (a timer loop that toggled a breakpoint on -[EnemyBase update:] every
    few seconds) slowed the game ~30x - measured 4 s of game time per 123 s;
    this one is a single permanent breakpoint on a state-change method."""
    def __init__(self, pct):
        super().__init__("*0x%x" % SET_AICONTROL, internal=False,
                         type=gdb.BP_HARDWARE_BREAKPOINT
                         if hasattr(gdb, "BP_HARDWARE_BREAKPOINT") else gdb.BP_BREAKPOINT)
        self.pct = pct

    def stop(self):
        if not is_mgst():
            return False
        new_state = int(gdb.parse_and_eval("$r2")) & 0xffff
        if new_state in (10, 0xff):
            return False
        cls = class_of("r0")
        if not is_enemy_class(cls):
            return False
        obj = int(gdb.parse_and_eval("$r0")) & 0xffffffff
        ene = int(gdb.parse_and_eval("*(unsigned int *)0x%x" % (obj + OFF_PENEDAT))) & 0xffffffff
        hp = int(gdb.parse_and_eval("*(int *)0x%x" % ene))
        mx = int(gdb.parse_and_eval("*(int *)0x%x" % (ene + 4)))
        if hp <= 0:
            return False
        new = hp - max(1, mx * self.pct // 100)
        if new <= 0:
            gdb.execute("set *(int *)0x%x = 0" % ene)
            gdb.execute("set $r2 = 10")
            counts.setdefault("drain-kill:" + cls, [0, 0])[0] += 1
        else:
            gdb.execute("set *(int *)0x%x = %d" % (ene, new))
            counts.setdefault("drain-hit:" + cls, [0, 0])[0] += 1
        return False


class MgstDrain(gdb.Command):
    """mgst-drain PCT - every enemy AI state change costs PCT% of max HP; at 0
    the enemy dies through setAiControl:10."""
    def __init__(self):
        super().__init__("mgst-drain", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        pct = int(arg.split()[-1])
        DrainBreakpoint(pct)
        print("mgst: drain %d%% of max HP per AI state change" % pct)


for _c in (MgstConnect, MgstBreak, MgstWatch, MgstRun, MgstSummary,
           MgstStage, MgstSubstage, MgstSurvival, MgstGodmode, MgstAutohit, MgstEvery, MgstDrain, MgstBleed):
    _c()


# --- menu tour (PLAN 4b route: snapshots of screens the missions never show) ---
GAMESCENE = 0x10f2c          # -[CrashLandingAppDelegate GameScene] (per frame, self in r0)
GAMESCENE_ADDR = GAMESCENE
OFF_SCENE, OFF_CASE = 52, 60                 # _Scene, _case
OFF_NEXT, OFF_BAR, OFF_BACK = 45152, 45164, 45176   # next_scene, bar_anim_cnt, back_anim_cnt


class _AtGameScene(gdb.Breakpoint):
    """One-shot action at -[CrashLandingAppDelegate GameScene] entry, in the
    MGSTUS context only (a timer interrupt may stop the CPU in another
    process, whose page tables do not map MGSTUS memory: LOG 2026-10-08).
    action(self_ptr) runs once; the breakpoint then disables itself."""
    def __init__(self, action):
        super().__init__("*0x%x" % GAMESCENE, internal=True)
        self.action, self.done = action, False

    def stop(self):
        if self.done or not is_mgst():
            return False
        self.done = True
        self.action(reg("r0"))
        gdb.post_event(lambda: setattr(self, "enabled", False))
        return False


class MgstTour(gdb.Command):
    """mgst-tour DUMPDIR SETTLE SCENE [SCENE ...] - visit title-menu scenes.

    For each scene: back to the title (_Scene=1, _case=0: its case 0 reloads
    the title if it was released), wait, then do what the title does when a
    menu bar is chosen (next_scene=N, _case=2, bar/back animation counters 0)
    so the game itself runs Change_scene:/title_release; after SETTLE seconds
    touch DUMPDIR/dump.request (snap_mgst dump mode snapshots the next frame).
    Fields are written at a one-shot GameScene entry breakpoint (MGSTUS
    context, between frames); timers only pace the tour."""
    def __init__(self):
        super().__init__("mgst-tour", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        a = arg.split()
        dumpdir, settle, scenes = a[0], float(a[1]), [int(x, 0) for x in a[2:]]
        inf = gdb.selected_inferior()

        def rd(me, off):
            return int.from_bytes(bytes(inf.read_memory(me + off, 4)), "little", signed=True)

        def wr(me, off, v):
            inf.write_memory(me + off, (v & 0xffffffff).to_bytes(4, "little"))

        def run_for(secs):
            t = threading.Timer(secs, lambda: os.kill(os.getpid(), signal.SIGINT))
            t.daemon = True
            t.start()
            try:
                gdb.execute("continue")
            except (gdb.error, KeyboardInterrupt) as e:
                print("mgst-tour: continue ended: %s" % e)
            t.cancel()

        def at_scene(fn, wait):
            bp = _AtGameScene(fn)
            run_for(wait)
            bp.delete()
            return bp.done

        try:
            for n in scenes:
                seen = {}

                def to_title(me):
                    seen["before"] = (rd(me, OFF_SCENE), rd(me, OFF_CASE))
                    wr(me, OFF_SCENE, 1); wr(me, OFF_CASE, 0)
                at_scene(to_title, 8)

                def choose(me, n=n):
                    seen["title"] = (rd(me, OFF_SCENE), rd(me, OFF_CASE))
                    wr(me, OFF_NEXT, n); wr(me, OFF_CASE, 2); wr(me, OFF_BAR, 0); wr(me, OFF_BACK, 0)
                at_scene(choose, settle)

                def probe(me):
                    seen["now"] = (rd(me, OFF_SCENE), rd(me, OFF_CASE))
                at_scene(probe, 1)
                open(os.path.join(dumpdir, "dump.request"), "a").close()
                run_for(6)
                got = seen.get("now", (None, None))
                print("mgst-tour: scene %d: before %s, title %s, now %s%s" % (
                    n, seen.get("before"), seen.get("title"), got,
                    "" if got[0] == n else "  (NOT REACHED)"), flush=True)
                # in-screen taps (MGST_TOUR_TAPS="x,y;x,y;..."): each tap is sent
                # while the CPU runs, then the next frame is snapshotted - the
                # screen's own touch handling, sub-menus, toggles (LOG 2026-10-09)
                if got[0] == n:
                    for xy in [t for t in os.environ.get("MGST_TOUR_TAPS", "").split(";") if t]:
                        x, y = xy.split(",")
                        tt = threading.Timer(0.5, lambda x=x, y=y: subprocess.Popen(
                            [sys.executable, "tools/oracle_input.py", "tap", x, y],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
                        td = threading.Timer(3.0, lambda: open(os.path.join(dumpdir, "dump.request"), "a").close())
                        tt.daemon = td.daemon = True
                        tt.start(); td.start()
                        run_for(5)
                        print("mgst-tour: scene %d: tap %s,%s" % (n, x, y), flush=True)
        finally:
            gdb.execute("delete")
            gdb.execute("detach")
            print("mgst-tour: detached", flush=True)


MgstTour()
