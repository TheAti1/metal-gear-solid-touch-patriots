#!/usr/bin/env python3
"""
Per-function verification ledger for the "decompilation complete" gate
(PLAN 4b, V7). Every percentage in reports comes from this file.

    tools/mgst_status.py [--results recovered/compile/difftest_offline.jsonl]

Writes analysis/verification/function_status.tsv (one row per function) and
analysis/verification/status.md (the % breakdown). Inputs: the export
(recovered/compile/functions.jsonl), compile results (fn/<addr>.o), the
compile report's V0 list (entry-stack approximations), the offline
differential results, the V1 audit report.

verdict per function (worst sample wins, as tools/mgst_difftest_report.py):
  pass              bit-identical on every tested state
  fail              at least one state differs (reason = first difference)
  return-unverified only the return value differs and its type is inferred
  untestable        every state hit an OS call / unmodelled boundary / limit
  no-state          compiles, but no captured state reached it yet
  no-compile        does not compile
"""
import argparse
import glob
import collections
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDIR = os.path.join(ROOT, "recovered/compile")
OUT = os.path.join(ROOT, "analysis/verification")
RANK = {"fail": 5, "pass": 4, "return-unverified": 3, "untestable": 2, "link-failed": 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", nargs="*", default=sorted(glob.glob(os.path.join(CDIR, "difftest_offline*.jsonl"))) +
                    sorted(glob.glob(os.path.join(CDIR, "difftest_frames*.jsonl"))) +
                    sorted(glob.glob(os.path.join(CDIR, "difftest_calls*.jsonl"))))
    a = ap.parse_args()
    funcs = [json.loads(l) for l in open(os.path.join(CDIR, "functions.jsonl"))]
    funcs = [f for f in funcs if f.get("c") is not None]
    rep = open(os.path.join(CDIR, "compile_report.md")).read()
    v0 = set(re.findall(r"^- (0x[0-9a-f]+) `", rep.split("## Entry-stack approximations")[-1], re.M)) \
        if "## Entry-stack approximations" in rep else set()
    extra = os.path.join(OUT, "v0_extra.tsv")       # V0 entries not from the compile report
    if os.path.exists(extra):
        v0 |= {l.split("\t")[0] for l in open(extra) if l.startswith("0x")}
    best, states = {}, collections.Counter()
    natural_pass = set()            # passed on a call the game itself made
    # current build fingerprints (fn/<addr>.fp, written by mgst_difftest.link):
    # a row tested a binary; it only counts while that binary is still the build
    cur_fp = {}
    for f in funcs:
        try:
            cur_fp[f["addr"]] = open(os.path.join(CDIR, "fn", f["addr"] + ".fp")).read().strip()
        except OSError:
            pass
    stale = collections.Counter()
    void_now = {f["addr"] for f in funcs
                if re.match(r"^\s*(?:static\s+)?void\s", f["proto"].replace("__thiscall", ""))}
    # ... or proven void from the binary: no call site reads r0/r1
    # (tools/ghidra/AnalyzeReturnUse.java -> analysis/symbols/return_use.tsv)
    ru = os.path.join(ROOT, "analysis/symbols/return_use.tsv")
    if os.path.exists(ru):
        for l in open(ru):
            p = l.rstrip("\n").split("\t")
            if len(p) > 5 and p[5] == "void" and p[0] != "addr":
                void_now.add("0x%x" % int(p[0], 16))
    rows_in = []
    for path in a.results:
        if os.path.exists(path):
            rows_in += [json.loads(l) for l in open(path)]
    newest = {}                     # per function: newest harness version among current-build rows
    for r in rows_in:
        if r.get("fp") == cur_fp.get(r["addr"]):
            newest[r["addr"]] = max(newest.get(r["addr"], 1), r.get("hv", 1))
    if True:
        for r in rows_in:
            # a newer harness supersedes an older one's FAIL/UNTESTABLE rows (it
            # was built to decide exactly those); an older PASS of the same binary
            # stays evidence (every harness change so far made the comparison
            # fairer or added a capability, none made a pass invalid)
            if r.get("hv", 1) < newest.get(r["addr"], 1) and r["verdict"] != "pass":
                continue
            k = r["addr"]
            if r.get("fp") != cur_fp.get(k) and r["verdict"] != "link-failed":
                stale[k] += 1
                continue
            states[k] += 1
            # a return-unverified row differed ONLY in r0/r1; if the function is
            # now declared void (unused return, analysis/symbols/unused_returns.tsv),
            # nothing it returns is observable: the row is a pass
            if r["verdict"] == "return-unverified" and k in void_now:
                r = dict(r, verdict="pass", detail="return differs only; declared void (unused return)")
            elif r["verdict"] == "return-unverified":
                # the function returns a value its callers use, and r0 differs:
                # a real difference (2026-10-11: SoundManager::categoryVolume
                # returned 1.065e9 for 1.0 and still counted as proven because a
                # pass row outranked this one)
                r = dict(r, verdict="fail", detail="return value differs (non-void): " + r.get("detail", "")[:160])
            if r["verdict"] == "pass" and r.get("source") != "synthetic":
                natural_pass.add(k)
            if k not in best or RANK[r["verdict"]] > RANK[best[k]["verdict"]]:
                best[k] = r
    rows, count = [], collections.Counter()
    for f in sorted(funcs, key=lambda f: int(f["addr"], 16)):
        k = f["addr"]
        compiles = os.path.exists(os.path.join(CDIR, "fn", k + ".o"))
        if not compiles:
            v, why = "no-compile", ""
        elif k in best:
            v = best[k]["verdict"]
            v = "fail" if v == "link-failed" else v
            why = best[k].get("detail", "")[:160].replace("\t", " ").replace("\n", " ") if v != "pass" else ""
        elif stale[k]:
            v, why = "stale", "%d result(s) for an older build: run tools/mgst_snap.py refresh" % stale[k]
        else:
            v, why = "no-state", ""
        count[v] += 1
        rows.append((k, f["name"], "yes" if compiles else "no", str(states.get(k, 0)), v,
                     "V0:entry-stack" if k in v0 else "", why))
    with open(os.path.join(OUT, "function_status.tsv"), "w") as w:
        w.write("addr\tfunction\tcompiles\tstates\tverdict\tv0\treason\n")
        for r in rows:
            w.write("\t".join(r) + "\n")
    n = len(rows)
    audit = open(os.path.join(OUT, "v1_audit.md")).read()
    audit_ok = "All audits pass" in audit
    pct = lambda x: 100.0 * x / n
    synth_only = sum(1 for r in rows if r[4] == "pass" and r[0] not in natural_pass)
    covered = sum(1 for r in rows if r[4] == "pass" or r[0] in v0)
    tested = count["pass"] + count["fail"] + count["return-unverified"] + count["untestable"]
    decided = count["pass"] + count["fail"]
    lines = ["# Decompilation verification status", "",
             "Generated by `tools/mgst_status.py` from `function_status.tsv`. Gate (PLAN 4b): every function",
             "passes on diverse real states, or is on the V0 list (manual asm-to-C audit, <= 2 %).", "",
             "| | functions | %% of %d |" % n, "|---|---:|---:|",
             "| decompiled | %d | 100.0 |" % n,
             "| compile standalone | %d | %.1f |" % (n - count["no-compile"], pct(n - count["no-compile"])),
             "| V1 static audits | %s | |" % ("all pass" if audit_ok else "FAILING"),
             "| reached by a captured state or a synthetic call | %d | %.1f |" % (tested, pct(tested)),
             "| **proven bit-identical (pass)** | **%d** | **%.1f** |" % (count["pass"], pct(count["pass"])),
             "| - of which only by synthetic calls (V5: harvested receiver, fixed argument vectors) | %d | %.1f |" % (
                 synth_only, pct(synth_only)),
             "| fail | %d | %.1f |" % (count["fail"], pct(count["fail"])),
             "| return-unverified (only an inferred return type differs) | %d | %.1f |" % (
                 count["return-unverified"], pct(count["return-unverified"])),
             "| untestable on the states so far | %d | %.1f |" % (count["untestable"], pct(count["untestable"])),
             "| stale (results only for an older build; `mgst_snap.py refresh`) | %d | %.1f |" % (
                 count["stale"], pct(count["stale"])),
             "| no state yet | %d | %.1f |" % (count["no-state"], pct(count["no-state"])),
             "| V0 list (manual audit, analysis/verification/v0_audit.md) | %d | %.2f |" % (len(v0), pct(len(v0))),
             "| **covered: proven or V0-audited (gate)** | **%d** | **%.1f** |" % (covered, pct(covered)), "",
             "Pass rate of decided tests: %.1f %% (%d / %d)." % (100.0 * count["pass"] / max(1, decided),
                                                                count["pass"], decided)]
    # the gate (PLAN 4b): every function proven, or audited on the V0 list
    open_rows = [r for r in rows if r[4] != "pass" and r[0] not in v0]
    with open(os.path.join(OUT, "gate_open.tsv"), "w") as w:
        w.write("addr\tfunction\tverdict\treason\n")
        for r in open_rows:
            w.write("\t".join((r[0], r[1], r[4], r[6])) + "\n")
    by = collections.Counter(r[4] for r in open_rows)
    lines += ["", "**Gate:** %s - %d function(s) neither proven nor V0-audited (%s); list in "
              "`analysis/verification/gate_open.tsv`." % (
                  "PASSED" if not open_rows else "OPEN", len(open_rows),
                  ", ".join("%d %s" % (v, k) for k, v in by.most_common()) or "none")]
    open(os.path.join(OUT, "status.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[5:]))


if __name__ == "__main__":
    main()
