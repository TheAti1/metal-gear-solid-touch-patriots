#!/usr/bin/env python3
"""Mutation test of the differential harness (LOG 2026-10-09): is it actually
sensitive? A proof is only as good as the harness's ability to see a wrong
function.

For each chosen PROVEN function, one small semantic change is made to its
recompiled C (one at a time):
  int   - an integer literal in the body +1
  cmp   - the first `<` / `<=` / `>` / `>=` / `==` / `!=` flipped
  float - a float literal changed in its last mantissa bit
The mutant is compiled with the project's flags, linked, and tested with the
normal synthetic-call / frame drivers on real snapshots. A mutant must FAIL
(killed). The original .c/.o/.bin/.fp are restored afterwards and the
fingerprint is checked to be the original one.

  tools/mgst_mutation.py [--funcs 0x... ...] [--n 12] [--dirs N]
Output: analysis/verification/mutation_test.md (+ .tsv)
"""
import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
CDIR = os.path.join(ROOT, "recovered/compile")
FN = os.path.join(CDIR, "fn")


def body_span(src):
    m = re.search(r"\bREC_\w+\s*\([^)]*\)\s*\{", src, re.S)
    return (m.end(), len(src)) if m else (0, len(src))


def mutate(src, kind):
    s0, s1 = body_span(src)
    body = src[s0:s1]
    # skip comments and site markers when searching
    def find(pat):
        for m in re.finditer(pat, body):
            pre = body[:m.start()]
            if pre.count("/*") > pre.count("*/"):
                continue
            line = body[body.rfind("\n", 0, m.start()) + 1:m.start()]
            if "#define" in line or "__frame" in line or "(char **)0x" in body[m.start() - 12:m.end() + 2]:
                continue
            return m
        return None
    if kind == "int":
        m = find(r"(?<![\w.x])([1-9]\d{0,4})(?![\w.])")
        if not m:
            return None, None
        new = str(int(m.group(1)) + 1)
    elif kind == "cmp":
        m = find(r"(?<![<>=!])(<=|>=|==|!=|<|>)(?![<>=])")
        if not m or body[m.start() - 1:m.start()] == "-":
            return None, None
        new = {"<": "<=", "<=": "<", ">": ">=", ">=": ">", "==": "!=", "!=": "=="}[m.group(1)]
    elif kind == "float":
        m = find(r"(?<![\w.])(\d+\.\d+)f\b")
        if not m:
            return None, None
        v = float(m.group(1))
        b = struct.unpack("<I", struct.pack("<f", v))[0] ^ 1
        new = "%.9gf" % struct.unpack("<f", struct.pack("<I", b))[0]
        new = new if "." in new or "e" in new else new.replace("f", ".0f")
        return src[:s0] + body[:m.start()] + new + body[m.end():], "%s -> %s" % (m.group(0), new)
    return src[:s0] + body[:m.start()] + new + body[m.end():], "%s -> %s" % (m.group(0), new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--funcs", nargs="*")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--dirs", type=int, default=3)
    a = ap.parse_args()
    import mgst_difftest as D
    import mgst_recompile as R
    FD = D.init_link()
    funcs = {json.loads(l)["addr"]: json.loads(l) for l in open(os.path.join(CDIR, "functions.jsonl"))}
    if a.funcs:
        picks = a.funcs
    else:
        # proven on natural states, mid-sized bodies, spread over the binary
        st = [l.rstrip("\n").split("\t") for l in open(os.path.join(ROOT, "analysis/verification/function_status.tsv"))][1:]
        cand = [r[0] for r in st if r[4] == "pass" and r[3].isdigit() and int(r[3]) >= 50
                and 1500 < os.path.getsize(os.path.join(FN, r[0] + ".c")) < 12000]
        step = max(1, len(cand) // a.n)
        picks = cand[::step][:a.n]
    snaps = sorted(d for d in os.listdir(os.path.join(ROOT, "oracle/reports/snap")) if d.startswith("campaign_") and d.endswith("_dump"))
    dirs = [os.path.join(ROOT, "oracle/reports/snap", snaps[int(i * (len(snaps) - 1) / max(1, a.dirs - 1))]) for i in range(a.dirs)]
    tmp = tempfile.mkdtemp(prefix="mgst_mut_")
    rows = []
    for addr in picks:
        base = os.path.join(FN, addr)
        keep = {ext: open(base + ext, "rb").read() for ext in (".c", ".o", ".bin", ".fp") if os.path.exists(base + ext)}
        orig_fp = keep.get(".fp", b"").decode().strip()
        src = keep[".c"].decode()
        try:
            for kind in ("int", "cmp", "float"):
                mut, what = mutate(src, kind)
                if mut is None:
                    continue
                open(base + ".c", "w").write(mut)
                r = subprocess.run(["clang"] + R.CFLAGS + ["-I", CDIR, "-c", base + ".c", "-o", base + ".o"],
                                   capture_output=True, text=True)
                if r.returncode:
                    rows.append((addr, funcs[addr]["name"], kind, what, "compile-error", ""))
                    continue
                out = os.path.join(tmp, "%s_%s.jsonl" % (addr, kind))
                cmd = [sys.executable, os.path.join(ROOT, "tools/mgst_snap.py"), "calls"] + dirs + \
                      ["--only", addr, "--per-dir", "2", "--jobs", "3", "--out", out + ".calls"]
                subprocess.run(cmd, capture_output=True)
                cmd = [sys.executable, os.path.join(ROOT, "tools/mgst_snap.py"), "frames"] + dirs + \
                      ["--only", addr, "--per-dir", "2", "--frames", "4", "--jobs", "3", "--out", out + ".frames"]
                subprocess.run(cmd, capture_output=True)
                verdicts = []
                for f in (out + ".calls", out + ".frames"):
                    if os.path.exists(f):
                        verdicts += [json.loads(l)["verdict"] for l in open(f)]
                nf = verdicts.count("fail") + verdicts.count("return-unverified")
                np_ = verdicts.count("pass")
                status = "KILLED" if nf else ("SURVIVED" if np_ else "untested")
                rows.append((addr, funcs[addr]["name"], kind, what, status, "fail %d / pass %d / other %d" % (
                    nf, np_, len(verdicts) - nf - np_)))
                print("%s %-40s %-5s %-28s %s" % (addr, funcs[addr]["name"][:40], kind, what[:28], status), flush=True)
        finally:
            for ext, data in keep.items():
                open(base + ext, "wb").write(data)
            D.link(FD[int(addr, 16)])
            fp_now = open(base + ".fp").read().strip() if os.path.exists(base + ".fp") else ""
            if orig_fp and fp_now != orig_fp:
                print("WARNING: fingerprint of %s not restored (%s vs %s)" % (addr, fp_now, orig_fp))
    shutil.rmtree(tmp, ignore_errors=True)
    killed = sum(1 for r in rows if r[4] == "KILLED")
    tested = sum(1 for r in rows if r[4] in ("KILLED", "SURVIVED"))
    with open(os.path.join(ROOT, "analysis/verification/mutation_test.tsv"), "w") as w:
        w.write("addr\tfunction\tmutation\tchange\tresult\tverdicts\n")
        for r in rows:
            w.write("\t".join(r) + "\n")
    print("mutation test: %d mutants tested, %d killed, %d survived" % (tested, killed, tested - killed))


if __name__ == "__main__":
    main()
