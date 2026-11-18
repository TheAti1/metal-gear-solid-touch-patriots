#!/usr/bin/env python3
"""
Decode drcov_mgst `calls=` output into facts the static decompilation lacks.

    tools/mgst_calls.py oracle/reports/*.calls.tsv --out analysis/dynamic

Inputs are TSV rows written by contrib/plugins/drcov_mgst.c (see its header):
    edge  SRC  DST  N     SRC = last insn of an MGST block, DST = next MGST block
    msg   SITE KIND ISA META CLASS SELECTOR N

Outputs (all merged over every trace given):
  msgsend_sites.tsv    call site, enclosing function, kind, [+/-Class selector]
                       for every executed BL/BLX to objc_msgSend*; this is what
                       Ghidra loses at the ~200 `_objc_msgSend()` calls with no
                       selector/receiver in the corpus
  indirect_targets.tsv every executed register/pc branch (blx rX, bx rX with
                       rX != lr, mov pc, ldr pc, add pc) and its observed
                       targets - jumptables, switch helpers, function pointers
  bl_nonreturn.tsv     BL targets entered from a site that NEVER returned to
                       site+4 although the target ran: `bl` used as a long
                       branch (e.g. FUN_0001339c, the shared epilogue of the
                       scene state machine) - flow-override candidates
  summary.md           counts

Noise: an edge spans whatever ran in between (dylibs, kernel, other threads),
so a thread switch can create a spurious edge. Those have tiny counts and do
not match static structure; the TSVs keep the counts so they can be filtered.
"""
import argparse
import bisect
import collections
import csv
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_EXE = os.environ.get(
    "MGST_REF_EXE",
    os.path.join(ROOT, "work/extracted/Payload/MGSTUS.app/MGSTUS"))
FUNCMAP = os.environ.get("MGST_FUNCMAP", os.path.join(ROOT, "analysis/symbols/function_map.csv"))
TEXT_LO, TEXT_HI = 0x1000, 0x69000
STUBS = (0x5a614, 0x5ae9c)
# Apple switch helpers (tools/ghidra/InstallSwitchCallFixup.java): `bl helper`
# never returns; the helper jumps to the case. function_map.csv has no entry
# for them, so they would otherwise symbolise as "-[RayWeapon render]+0x4xx".
HELPERS = {0x5a5b4: "___switchu8", 0x5a5cc: "___switch8", 0x5a5e4: "___switch16"}
HELPER_RANGE = (0x5a5b4, 0x5a614)


def load_funcs():
    with open(FUNCMAP) as f:
        rows = sorted((int(r["address"], 16), r["function"]) for r in csv.DictReader(f))
    return [a for a, _ in rows], [n for _, n in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("traces", nargs="+")
    ap.add_argument("--out", default=os.path.join(ROOT, "analysis/dynamic"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    code = open(REF_EXE, "rb").read()
    faddr, fname = load_funcs()

    def func(va):
        if HELPER_RANGE[0] <= va < HELPER_RANGE[1]:
            h = max(k for k in HELPERS if k <= va) if va >= min(HELPERS) else None
            return "%s+0x%x" % (HELPERS[h], va - h) if h else "?"
        i = bisect.bisect_right(faddr, va) - 1
        return "%s+0x%x" % (fname[i], va - faddr[i]) if i >= 0 else "?"

    def fstart(va):
        i = bisect.bisect_right(faddr, va) - 1
        return faddr[i] if i >= 0 else None

    def hw(va):
        return struct.unpack_from("<H", code, va - 0x1000)[0]

    def classify(src):
        """Kind of control transfer ending at SRC (Thumb unless in the ARM stubs)."""
        if STUBS[0] <= src < STUBS[1] or not (TEXT_LO <= src < TEXT_HI - 2):
            return "arm/other"
        h = hw(src)
        if (h & 0xff87) == 0x4780:
            return "blx_reg"
        if (h & 0xff87) == 0x4700:
            return "bx_lr" if ((h >> 3) & 0xf) == 14 else "bx_reg"
        if (h & 0xff87) == 0x4687:
            return "mov_pc"
        if (h & 0xff87) == 0x4487:
            return "add_pc"
        if (h & 0xff00) == 0xbd00:
            return "pop_pc"
        h0 = hw(src - 2) if src >= TEXT_LO + 2 else 0
        if (h0 & 0xf800) == 0xf000 and (h & 0xe800) == 0xe800:
            return "bl_pair"          # SRC is the second half of a BL/BLX pair
        if (h & 0xf800) == 0xf000 and (hw(src + 2) & 0xe800) == 0xe800:
            return "bl"
        if (h & 0xf000) == 0xd000 or (h & 0xf800) == 0xe000:
            return "branch"
        return "fallthrough/other"

    def bl_target(site):
        h0, h1 = hw(site), hw(site + 2)
        off = ((h0 & 0x7ff) << 12) | ((h1 & 0x7ff) << 1)
        if off & 0x400000:
            off -= 0x800000
        t = site + 4 + off
        return t & ~3 if (h1 & 0xf800) == 0xe800 else t

    def is_return_site(t):
        """T directly follows a call (BL pair or BLX rX): T is a return address."""
        if not (TEXT_LO + 4 <= t < TEXT_HI):
            return False
        h0, h1 = hw(t - 4), hw(t - 2)
        if (h0 & 0xf800) == 0xf000 and (h1 & 0xe800) == 0xe800:
            return True
        return (h1 & 0xff87) == 0x4780

    edges = collections.Counter()
    msgs = {}
    for t in a.traces:
        for line in open(t):
            p = line.rstrip("\n").split("\t")
            if p[0] == "edge":
                edges[(int(p[1], 16), int(p[2], 16))] += int(p[3])
            elif p[0] == "msg":
                site = int(p[1], 16)
                key = (site, p[2], p[5], p[4], p[6])
                msgs[key] = msgs.get(key, 0) + int(p[7])

    # ---- msgSend sites
    by_site = collections.defaultdict(list)
    for (site, kind, cls, meta, sel), n in msgs.items():
        by_site[site].append((("+" if meta == "1" else "-") + "[%s %s]" % (cls, sel), kind, n))
    with open(os.path.join(a.out, "msgsend_sites.tsv"), "w") as f:
        f.write("site\tfunction\tkind\tobserved\tn_receiver_classes\n")
        for site in sorted(by_site):
            obs = sorted(by_site[site], key=lambda x: -x[2])
            f.write("0x%x\t%s\t%s\t%s\t%d\n" % (site, func(site), obs[0][1],
                    " | ".join("%s x%d" % (o[0], o[2]) for o in obs), len(obs)))

    # ---- indirect targets (BL/BLX pair: the block ends at the 2nd halfword)
    indirect = collections.defaultdict(collections.Counter)
    kinds = {}
    bl_seen = collections.defaultdict(set)    # bl site -> observed next blocks
    for (src, dst), n in edges.items():
        k = classify(src)
        if k in ("blx_reg", "bx_reg", "mov_pc", "add_pc"):
            if k != "blx_reg" and is_return_site(dst):
                continue              # `pop {rN}; bx rN` is an armv6 Thumb return
            indirect[src][dst] += n
            kinds[src] = k
        elif k == "bl":               # QEMU reports a BL pair as one insn at its 1st half
            bl_seen[src].add(dst)
        elif k == "bl_pair":
            bl_seen[src - 2].add(dst)
        elif k == "arm/other" and STUBS[0] <= src < STUBS[1]:
            pass
    with open(os.path.join(a.out, "indirect_targets.tsv"), "w") as f:
        f.write("site\tfunction\tinsn\tn_targets\ttargets\n")
        for src in sorted(indirect):
            tg = indirect[src]
            f.write("0x%x\t%s\t%s\t%d\t%s\n" % (src, func(src), kinds[src], len(tg),
                    " | ".join("0x%x %s x%d" % (d, func(d), n) for d, n in tg.most_common())))

    # ---- switch helpers: helper exits -> case targets, attributed to the
    # calling site in the same function
    helper_exits = collections.Counter()
    for (src, dst), n in edges.items():
        if HELPER_RANGE[0] <= src < HELPER_RANGE[1] and not (HELPER_RANGE[0] <= dst < HELPER_RANGE[1]):
            helper_exits[dst] += n
    def switch_table(site, helper):
        """Static case targets of the inline table after `bl helper` (LOG STEPS 3+4)."""
        ret = site + 4
        if helper == "___switch16":
            cnt = struct.unpack_from("<H", code, ret - 0x1000)[0]
            ent = [struct.unpack_from("<h", code, ret + 2 + 2 * i - 0x1000)[0] for i in range(cnt + 1)]
        else:
            cnt = code[ret - 0x1000]
            fmt = "B" if helper == "___switchu8" else "b"
            ent = [struct.unpack_from(fmt, code, ret + 1 + i - 0x1000)[0] for i in range(cnt + 1)]
        return [ret + e * 2 for e in ent]

    switch_sites = {}
    claimed = set()
    for site in sorted(bl_seen):
        tgt = bl_target(site)
        if tgt in HELPERS:
            table = switch_table(site, HELPERS[tgt])
            seen = sorted(set(table) & set(helper_exits))
            claimed |= set(table)
            switch_sites[site] = (HELPERS[tgt], len(set(table)), seen)
    unclaimed = sorted(d for d in helper_exits if d not in claimed)
    with open(os.path.join(a.out, "switch_targets.tsv"), "w") as f:
        f.write("site\tfunction\thelper\tn_static_targets\tn_seen\tseen_targets\n")
        for site, (h, nstat, seen) in switch_sites.items():
            f.write("0x%x\t%s\t%s\t%d\t%d\t%s\n" % (site, func(site), h, nstat, len(seen),
                    " ".join("0x%x" % c for c in seen)))
        for d in unclaimed:
            f.write("UNCLAIMED\t%s\t-\t-\t-\t0x%x (helper exit matching no static table)\n" % (func(d), d))

    # ---- BL that never returns to site+4
    returned = set()
    for (src, dst), n in edges.items():
        returned.add(dst)
    nonret = collections.defaultdict(list)
    for site, dsts in bl_seen.items():
        tgt = bl_target(site)
        if not (TEXT_LO <= tgt < HELPER_RANGE[0]):
            continue
        entered = tgt in dsts or any(fstart(d) == fstart(tgt) for d in dsts)
        if entered and (site + 4) not in returned:
            nonret[tgt].append(site)
    with open(os.path.join(a.out, "bl_nonreturn.tsv"), "w") as f:
        f.write("target\ttarget_function\tn_sites\tsites\n")
        for tgt in sorted(nonret, key=lambda t: -len(nonret[t])):
            s = sorted(nonret[tgt])
            f.write("0x%x\t%s\t%d\t%s\n" % (tgt, func(tgt), len(s), " ".join("0x%x" % x for x in s)))

    multi = sum(1 for s in by_site.values() if len({o[0] for o in s}) > 1)
    summary = [
        "# Dynamic call map (drcov_mgst calls=)",
        "",
        "Traces: " + ", ".join("`%s`" % os.path.relpath(t, ROOT) for t in a.traces),
        "",
        "| | |", "|---|---:|",
        "| distinct edges | %d |" % len(edges),
        "| objc_msgSend* call sites executed | %d |" % len(by_site),
        "| ... with more than one receiver class/selector (polymorphic) | %d |" % multi,
        "| indirect branch sites executed | %d |" % len(indirect),
        "| ... with more than one target | %d |" % sum(1 for v in indirect.values() if len(v) > 1),
        "| switch-helper call sites executed | %d (%d case targets seen) |" % (
            len(switch_sites), sum(len(c) for _, _, c in switch_sites.values())),
        "| helper exits matching NO static table (decode errors) | %d |" % len(unclaimed),
        "| BL-as-branch targets (never return to site+4) | %d (%d sites) |" % (
            len(nonret), sum(len(v) for v in nonret.values())),
    ]
    open(os.path.join(a.out, "summary.md"), "w").write("\n".join(summary) + "\n")
    print("\n".join(summary[4:]))


if __name__ == "__main__":
    main()
