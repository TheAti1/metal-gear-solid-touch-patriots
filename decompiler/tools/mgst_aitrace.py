#!/usr/bin/env python3
"""Summarise a gdb_step2 AI trace (mgst-break 0x2de10 with the EnemyBase ivar
expressions) into per-enemy state segments.

    tools/mgst_aitrace.py oracle/reports/gdb_step2_ai_*.tsv

Columns in `extra`: self,index,aiControl,aiStep,timer,sign,attack,move,
attackTime,type,scriptStep,scriptRow,t0,t1,t2,t3. One row = one
-[EnemyBase update:] call = one game frame for that enemy.
"""
import collections, sys

def s16(v): v &= 0xffff; return v - 0x10000 if v & 0x8000 else v
def s32(v): return v - (1 << 32) if v & 0x80000000 else v

STATE = {0xff: "idle", 0: "Appearance", 1: "Attack", 2: "Move", 3: "MoveAttack",
         4: "MoveAttack2", 5: "MoveEnd", 6: "LifeAct", 7: "SelfDestruction",
         8: "SpecialAttack", 9: "DataMove", 10: "Die"}

def main():
    per = collections.OrderedDict()
    for path in sys.argv[1:]:
        for l in list(open(path))[1:]:
            r = l.rstrip("\n").split("\t")
            if r[4] != "1": continue
            e = [int(x, 16) for x in r[10].split(",")]
            per.setdefault(e[0], []).append(e)
    for me, rows in per.items():
        e0 = rows[0]
        print("enemy @0x%x idx=%d type=%d frames=%d  sign=%d attack=%d move=%d attackTime=%d  "
              "spawn-table t=(%d,%d,%d,%d)" % (
                  me, s16(e0[1]), s32(e0[9]), len(rows), s16(e0[5]), s16(e0[6]),
                  s16(e0[7]), s16(e0[8]), *[s32(x) for x in e0[12:16]]))
        seg = None
        for e in rows:
            key = (s16(e[2]) & 0xffff, s32(e[10]))
            if seg is None or seg[0] != key:
                if seg: print("   %-16s step=%d  %4d frames  timer %d..%d" % (
                    STATE.get(seg[0][0] & 0xff if seg[0][0] == 0xffff else seg[0][0], seg[0][0]),
                    seg[0][1], seg[1], seg[2], seg[3]))
                seg = [key, 0, s32(e[4]), s32(e[4])]
            seg[1] += 1; seg[3] = s32(e[4])
        if seg: print("   %-16s step=%d  %4d frames  timer %d..%d" % (
            STATE.get(seg[0][0], seg[0][0]), seg[0][1], seg[1], seg[2], seg[3]))
if __name__ == "__main__":
    main()
