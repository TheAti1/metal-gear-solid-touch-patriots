#!/usr/bin/env python3
"""Summarise recovered/compile/difftest_results.jsonl (tools/mgst_difftest.py)
into recovered/compile/difftest_report.md.

Per function the verdict is: fail if ANY sample failed, else pass if any sample
passed, else return-unverified / untestable / link-failed.
"""
import collections
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDIR = os.path.join(ROOT, "recovered/compile")
RANK = {"fail": 5, "pass": 4, "return-unverified": 3, "untestable": 2, "link-failed": 1}


def cause(d):
    t = d["detail"]
    if d["verdict"] == "pass":
        return ""
    if d["verdict"] == "untestable":
        m = re.match(r"untestable: (\w+)", t)
        return "untestable: " + (m.group(1) if m else "?")
    if "unmapped" in t and "recompiled run" in t:
        return "recompiled code touches memory the original never does"
    if "memory bytes differ" in t:
        return "different bytes written to memory"
    if "boundary calls differ" in t:
        return "different calls to graphics/audio/OS services"
    if t.startswith("return"):
        return "different return value"
    return t[:60]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(CDIR, "difftest_results.jsonl"))
    ap.add_argument("--out", default=os.path.join(CDIR, "difftest_report.md"))
    a = ap.parse_args()
    best = {}
    samples = collections.Counter()
    for l in open(a.results):
        d = json.loads(l)
        samples[d["addr"]] += 1
        cur = best.get(d["addr"])
        if cur is None or RANK[d["verdict"]] > RANK[cur["verdict"]]:
            best[d["addr"]] = d
    n = len(best)
    c = collections.Counter(d["verdict"] for d in best.values())
    comp = open(os.path.join(CDIR, "compile_report.md")).read()
    ncomp = int(re.search(r"compiled \| \*\*(\d+)", comp).group(1))
    ntot = int(re.search(r"functions \| (\d+)", comp).group(1))
    tested_ok = c["pass"] + c["fail"]
    lines = [
        "# Step 7' differential test report", "",
        "Original vs recompiled function, run from the same real game state (oracle paused, pages "
        "faulted in on demand) in Unicorn; see tools/mgst_difftest.py.", "",
        "| | |", "|---|---:|",
        "| functions decompiled | %d |" % ntot,
        "| recompile standalone (clang ARMv6 Thumb) | %d (%.1f%%) |" % (ncomp, 100.0 * ncomp / ntot),
        "| hit on the oracle and tested (samples: %d) | %d |" % (sum(samples.values()), n),
        "| **pass** (identical returns, memory writes, boundary calls) | **%d** |" % c["pass"],
        "| fail | %d |" % c["fail"],
        "| return-only mismatch, return type only inferred | %d |" % c["return-unverified"],
        "| untestable sample (syscall / NULL from a stubbed service / limit) | %d |" % c["untestable"],
        "| link failed | %d |" % c["link-failed"],
        "| pass rate of decided tests (pass / (pass+fail)) | **%.1f%%** |" % (100.0 * c["pass"] / tested_ok if tested_ok else 0),
        "", "## Failures by cause", ""]
    causes = collections.Counter(cause(d) for d in best.values() if d["verdict"] == "fail")
    for k, v in causes.most_common():
        lines.append("- %d x %s" % (v, k))
    lines += ["", "## Failing functions", ""]
    for d in sorted((d for d in best.values() if d["verdict"] == "fail"), key=lambda d: d["addr"]):
        lines.append("- `%s` %s: %s" % (d["addr"], d["name"], d["detail"][:220].replace("|", "/")))
    lines += ["", "## Untestable / unverified", ""]
    for d in sorted((d for d in best.values() if d["verdict"] in ("untestable", "return-unverified", "link-failed")),
                    key=lambda d: d["addr"]):
        lines.append("- `%s` %s: %s" % (d["addr"], d["name"], d["detail"][:160].replace("|", "/")))
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[6:17]))


if __name__ == "__main__":
    main()
