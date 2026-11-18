#!/usr/bin/env python3
"""Package the complete, verified decompilation into ONE self-contained folder
for a porting session (LOG 2026-10-10).

  tools/make_port_handoff.py [--out PORT_HANDOFF]

LOCAL ONLY: the decompiled C is a derivative of Konami's binary. The folder is
git-ignored and must never be published (the GitHub folder ships the tools that
regenerate it instead).

Layout:
  README.md            how the code is organised and how to build on it
  src/<original source file>/<addr>_<name>.c
                       the VERIFIED C of every function, exactly as compiled
                       and differentially tested (recovered/compile/fn/*.c),
                       grouped by the game's original source file (STABS)
  include/             mgst_types.fixed.h + ghidra_ops.h (every type/macro the
                       C uses)
  index.tsv            per function: address, name, source file, verdict,
                       evidence, test coverage, path
  tables/              symbols.tsv (every global/function -> original address),
                       extslots.tsv (imported symbols -> binding slots),
                       functions.jsonl (prototypes + C as exported)
  readable/            the human-readable corpus, one file per original
                       source file (recovered/decompiled; NOT the tested form)
  runtime/vfpshim/     float/integer helper shims with the device's semantics
  binary/MGSTUS        the original executable (data image + reference)
  assets/MGSTUS.app/   the complete original app bundle (art, audio, data
                       tables, .al/.rl animation lists, plists, strings)
  assets/audio_flac/   the audio converted losslessly (tools/port_audio.py;
                       bit-exact for PCM, IMA4 music via ffmpeg's decoder)
  docs/                platform API inventory, gate sign-off, V0 audit,
                       coverage audit, test coverage, ledger
"""
import argparse
import csv
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "recovered/compile")


def safe(s):
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", s).strip("_")[:90]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "PORT_HANDOFF"))
    a = ap.parse_args()
    out = a.out
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    srcmap = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "analysis/symbols/function_map.csv"))):
        srcmap[int(r["address"], 16)] = r["source_file"]
    status = {}
    for l in open(os.path.join(ROOT, "analysis/verification/function_status.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0].startswith("0x"):
            status[int(p[0], 16)] = p
    cov = {}
    tc = os.path.join(ROOT, "analysis/verification/test_coverage.tsv")
    if os.path.exists(tc):
        for l in open(tc):
            p = l.rstrip("\n").split("\t")
            if p[0].startswith("0x"):
                cov[int(p[0], 16)] = (p[6], p[7])
    funcs = [json.loads(l) for l in open(os.path.join(C, "functions.jsonl"))]
    rows = []
    for f in funcs:
        if f.get("c") is None:
            continue
        addr = int(f["addr"], 16)
        sf = srcmap.get(addr, "_compiler_and_linker_glue")
        d = os.path.join(out, "src", safe(sf.replace("/", "__")))
        os.makedirs(d, exist_ok=True)
        fname = "%s_%s.c" % (f["addr"], safe(f["name"]))
        shutil.copy2(os.path.join(C, "fn", f["addr"] + ".c"), os.path.join(d, fname))
        st = status.get(addr, [f["addr"], f["name"], "", "", "?", "", ""])
        pct, ncov = cov.get(addr, ("", "0"))
        rows.append((f["addr"], f["name"], sf, st[4], st[5] if len(st) > 5 else "", pct if ncov != "0" else "",
                     os.path.relpath(os.path.join(d, fname), out)))
    with open(os.path.join(out, "index.tsv"), "w") as w:
        w.write("addr\tfunction\toriginal_source_file\tverdict\tv0_audit\ttest_coverage_pct\tpath\n")
        for r in sorted(rows, key=lambda r: int(r[0], 16)):
            w.write("\t".join(r) + "\n")
    os.makedirs(os.path.join(out, "include"))
    for h in ("mgst_types.fixed.h", "ghidra_ops.h"):
        shutil.copy2(os.path.join(C, h), os.path.join(out, "include", h))
    os.makedirs(os.path.join(out, "tables"))
    for t in ("symbols.tsv", "extslots.tsv", "functions.jsonl"):
        shutil.copy2(os.path.join(C, t), os.path.join(out, "tables", t))
    shutil.copytree(os.path.join(ROOT, "recovered/decompiled"), os.path.join(out, "readable"))
    os.makedirs(os.path.join(out, "runtime"))
    shutil.copytree(os.path.join(C, "vfpshim"), os.path.join(out, "runtime", "vfpshim"),
                    ignore=shutil.ignore_patterns("*.o"))
    os.makedirs(os.path.join(out, "binary"))
    shutil.copy2(os.path.join(ROOT, "work/extracted/Payload/MGSTUS.app/MGSTUS"), os.path.join(out, "binary", "MGSTUS"))
    os.makedirs(os.path.join(out, "assets"))
    shutil.copytree(os.path.join(ROOT, "work/extracted/Payload/MGSTUS.app"), os.path.join(out, "assets", "MGSTUS.app"),
                    ignore=shutil.ignore_patterns("MGSTUS", "_CodeSignature", "CodeResources"))
    flac = os.path.join(ROOT, "build/port_assets/audio")
    if os.path.isdir(flac):
        shutil.copytree(flac, os.path.join(out, "assets", "audio_flac"))
    os.makedirs(os.path.join(out, "docs"))
    for src, dst in (("analysis/port/platform_api.md", "PLATFORM_API.md"),
                     ("analysis/verification/gate_signoff.md", "GATE_SIGNOFF.md"),
                     ("analysis/verification/v0_audit.md", "V0_AUDIT.md"),
                     ("analysis/verification/coverage_audit.md", "COVERAGE_AUDIT.md"),
                     ("analysis/verification/test_coverage.md", "TEST_COVERAGE.md"),
                     ("analysis/verification/test_coverage.tsv", "test_coverage.tsv"),
                     ("analysis/verification/function_status.tsv", "function_status.tsv"),
                     ("analysis/verification/status.md", "STATUS.md"),
                     ("recovered/compile/compile_report.md", "COMPILE_REPORT.md"),
                     ("GIT_UPLOAD/docs/FORMATS.md", "FORMATS.md")):
        if os.path.exists(os.path.join(ROOT, src)):
            shutil.copy2(os.path.join(ROOT, src), os.path.join(out, "docs", dst))
    shutil.copy2(os.path.join(ROOT, "tools/port_handoff_README.md"), os.path.join(out, "README.md"))
    n_src = len({r[2] for r in rows})
    print("port handoff %s: %d functions in %d source files" % (out, len(rows), n_src))


if __name__ == "__main__":
    main()
