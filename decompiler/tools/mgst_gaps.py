#!/usr/bin/env python3
"""
Decompilation gap ledger: what still stands between the recovered corpus and a
100% decompilation that can be ported 1:1. Phase-1 progress is measured here,
not as coverage %.

    tools/mgst_gaps.py [--corpus recovered/decompiled] [--coverage A.drcov ...]
                       [--out analysis/dynamic/gap_ledger.md]

Gap classes (per source file and total):
  msgsend_lost        objc_msgSend* call (whole statement, _stret aware) whose
                      selector is neither a string literal nor a variable the
                      same function assigns a string literal to
    ..._resolved      ...of those, preceded by a `/* dyn: [...] */` comment from
                      tools/ghidra/ApplyDynamicCalls.java (runtime-observed)
  fun_refs            references to FUN_xxxxxxxx pseudo-functions (unnamed or
                      mis-split code)
  undefined_types     `undefinedN` type uses (untyped locals/fields), split into
    undefined_benign  zero stores through a cast, raw stack byte buffers,
                      extraout_/in_stack_/unaff_ register leftovers, locals
                      only ever set to constants - type-independent meaning
    undefined_copy_only the rest: values only copied/stored/passed or pointer
                      targets - bit-exact with recovered/ghidra_types.h
  undefined_value_arith untyped VALUE locals used in arithmetic / ordered
                      compares - the only kind whose meaning depends on the
                      missing type (target 0)
  jumptable_unrecovered  "Could not recover jumptable" (a real gap)
  jumptable_warn      all jumptable/switch warnings incl. benign "Removing
                      unreachable block" (the inline case table bytes)
  bad_data            halt_baddata / bad instruction
  cpp_raw_this_offsets  `(this + 0x..)` / `this[0x..]` in C++ methods: class layout missing
  never_executed      functions with no block in any given coverage trace:
                      no dynamic evidence; must be verified statically
"""
import argparse
import bisect
import collections
import csv
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

MSG_STMT = re.compile(r"_objc_msgSend(Super2|_stret)?\(((?:[^();]|\((?:[^();]|\([^();]*\))*\))*)\)", re.S)


def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
            continue
        depth += ch in "([{"
        depth -= ch in ")]}"
        cur += ch
    out.append(cur.strip())
    return out
FUN = re.compile(r"\bFUN_[0-9a-f]{8}\b")
UND = re.compile(r"\bundefined\d?\b")
JT = re.compile(r"jumptable|switchD", re.I)
BAD = re.compile(r"halt_baddata|BADDATA|Bad instruction")


def unused_decl(text, decl):
    """A declared untyped local that is only ever assigned constants/zero."""
    v = re.sub(r"^undefined\d? \**(\w+);$", r"\1", decl.strip())
    uses = re.findall(r"[^\n]*\b%s\b[^\n]*" % re.escape(v), text)
    for u in uses:
        u = u.strip()
        if u == decl.strip():
            continue
        if not re.match(r"^%s = (0x[0-9a-f]+|-?\d+|0\.0|'\\0');$" % re.escape(v), u):
            return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=os.path.join(ROOT, "recovered/decompiled"))
    ap.add_argument("--coverage", nargs="*", default=[])
    ap.add_argument("--out", default=os.path.join(ROOT, "analysis/dynamic/gap_ledger.md"))
    a = ap.parse_args()

    per = collections.defaultdict(collections.Counter)
    for path in sorted(glob.glob(os.path.join(a.corpus, "*.c"))):
        name = os.path.basename(path)
        text = open(path, errors="replace").read()
        for line in text.splitlines():
            per[name]["fun_refs"] += len(FUN.findall(line))
            nu = len(UND.findall(line))
            per[name]["undefined_types"] += nu
            if nu:
                st = line.strip()
                benign = (re.search(r"\*\(undefined\d? \*\)[^;=]*= 0;", st)            # zero store
                          or re.match(r"^undefined\d? \w+ ?\[[^\]]*\];$", st)          # raw stack buffer
                          or "extraout_" in st or "in_stack_" in st or "unaff_" in st
                          or re.match(r"^undefined\d? \**\w+;$", st) and unused_decl(text, st))
                per[name]["undefined_copy_only" if not benign else "undefined_benign"] += nu
            if line.lstrip().startswith("/*") and JT.search(line):
                per[name]["jumptable_warn"] += 1
                if "Could not recover" in line:
                    per[name]["jumptable_unrecovered"] += 1
            per[name]["bad_data"] += len(BAD.findall(line))
            # C++ member access that fell back to raw pointer math: the class
            # layout is missing (a lost ApplyCppTypes result shows up here)
            per[name]["cpp_raw_this_offsets"] += len(re.findall(r"\(\s*this\s*\+\s*0x[0-9a-f]+\)|\bthis\[0x[0-9a-f]+\]", line))
        # functions are separated by the exporter's "/* xxxxxxxx  name */" banners
        for fn in re.split(r"\n(?=/\* [0-9a-f]{8}  )", text):
            # untyped VALUE locals used in arithmetic / ordered compares: the
            # only undefinedN whose meaning could depend on the missing type
            for t, v in re.findall(r"^\s+(undefined\d?) (\w+);$", fn, re.M):
                for l in fn.splitlines():
                    ls = l.strip()
                    if ls.startswith("undefined") or not re.search(r"\b%s\b" % v, ls):
                        continue
                    code = re.sub(r"\*\([^)]*\)", "", ls)
                    if (re.search(r"\b%s\b\s*([-+/%%]|\*(?!\))|<<|>>|<=?|>=?)\s*[\w(]" % v, code)
                            or re.search(r"[\w)]\s*([-+/%%]|<<|>>|<=?|>=?)\s*\b%s\b" % v, code)):
                        per[name]["undefined_value_arith"] += 1
                        break
            assigned = set(re.findall(r"\b(\w+) = (?:\(\w+ \*?\))?\"[^\"]+\"", fn))
            # selector picked from visible selref candidates (compiler-merged
            # call site): ppuVar1 = &PTR_s_updateMove_...; _objc_msgSend(self,*ppuVar1)
            assigned |= set(re.findall(r"\b(\w+) = &PTR_s_\w+", fn))
            assigned |= set(re.findall(r"\b(\w+) = \*\(char \*\*\)PTR_PTR_s_\w+", fn))
            # follow plain copies: op = local_b8; local_74 = *local_80; ...
            copies = re.findall(r"\b(\w+) = \*?(\w+);", fn)
            for _ in range(4):
                assigned |= {dst for dst, src in copies if src in assigned}
            for m in MSG_STMT.finditer(fn):
                stret = m.group(1) == "_stret"
                args = split_args(m.group(2))
                k = 2 if stret else 1
                sel = args[k] if len(args) > k else ""
                if sel.startswith('"'):
                    continue
                v = re.sub(r"^[*(]+|[)]+$", "", sel)
                if v in assigned:
                    per[name]["msgsend_sel_in_var_visible"] += 1
                    continue
                per[name]["msgsend_lost"] += 1
                ls = fn.rfind("\n", 0, m.start())
                prev_lines = [x for x in fn[:max(ls, 0)].splitlines() if x.strip()][-1:] or [""]
                if "dyn:" in prev_lines[0]:
                    per[name]["msgsend_lost_resolved"] += 1

    never = collections.Counter()
    n_never = None
    if a.coverage:
        import mgst_coverage as mc
        with open(mc.FUNCMAP) as f:
            rows = sorted((int(r["address"], 16), r["source_file"]) for r in csv.DictReader(f))
        faddr = [r[0] for r in rows]
        hit = set()
        for t in a.coverage:
            _b, bbs = mc.read_drcov(t)
            for pc, _sz in bbs:
                k = bisect.bisect_right(faddr, pc) - 1
                if k >= 0:
                    hit.add(k)
        for k, (_addr, src) in enumerate(rows):
            if k not in hit:
                never["Classes_" + src.replace("Classes/", "").replace("/", "_") + ".c"
                      if src.startswith("Classes/") else src.replace("/", "_") + ".c"] += 1
        n_never = len(rows) - len(hit)

    cols = ["msgsend_lost", "msgsend_lost_resolved", "msgsend_sel_in_var_visible", "fun_refs",
            "undefined_types", "undefined_value_arith", "undefined_copy_only", "undefined_benign",
            "jumptable_unrecovered", "jumptable_warn", "bad_data", "cpp_raw_this_offsets"]
    tot = collections.Counter()
    for c in per.values():
        tot.update(c)
    lines = ["# Decompilation gap ledger", "",
             "Corpus: `%s`" % os.path.relpath(a.corpus, ROOT),
             "Coverage traces: %s" % (", ".join("`%s`" % os.path.relpath(t, ROOT) for t in a.coverage) or "none"),
             "", "| gap | count |", "|---|---:|"]
    for c in cols:
        lines.append("| %s | %d |" % (c, tot[c]))
    if n_never is not None:
        lines.append("| never_executed functions | %d |" % n_never)
    lines += ["", "## Per file", "",
              "| file | " + " | ".join(cols) + (" | never_exec |" if n_never is not None else " |"),
              "|---|" + "---:|" * (len(cols) + (1 if n_never is not None else 0))]
    for name in sorted(per, key=lambda n: -sum(per[n][c] for c in cols if c != "msgsend_lost_resolved")):
        row = [str(per[name][c]) for c in cols]
        if n_never is not None:
            row.append(str(never.get(name, 0)))
        lines.append("| %s | %s |" % (name, " | ".join(row)))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[5:14 if n_never is not None else 13]))


if __name__ == "__main__":
    main()
