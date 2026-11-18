#!/usr/bin/env python3
"""Generate the figures of claude_notes/ (the GitHub write-up) from the
project's own data, so every graphic is reproducible (LOG 2026-10-11).

  tools/make_claude_notes.py      -> analysis/claude_notes/images/*.svg

Inputs: analysis/notes/macho_loadcommands.txt, analysis/symbols/function_map.csv,
analysis/verification/{function_status,test_coverage}.tsv, the difftest result
rows (recovered/compile, for evidence classes; optional), analysis/coverage/
stage_enemy_map.md, oracle/reports/snap/ (which states were captured).
"""
import collections
import csv
import glob
import json
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.figure
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "analysis/claude_notes/images")
os.makedirs(OUT, exist_ok=True)
PREVIEW = os.environ.get("NOTES_PREVIEW")      # dir: also write PNG previews there
_savefig = matplotlib.figure.Figure.savefig


def _save(self, path, *a, **k):
    _savefig(self, path, *a, **k)
    if PREVIEW and path.endswith(".svg"):
        os.makedirs(PREVIEW, exist_ok=True)
        _savefig(self, os.path.join(PREVIEW, os.path.basename(path)[:-4] + ".png"), dpi=90)


matplotlib.figure.Figure.savefig = _save
plt.rcParams.update({"font.size": 9, "svg.fonttype": "none", "figure.facecolor": "white"})

GROUPS = [  # source-file group -> colour
    ("App delegate (scenes, menus, UI)", "MGSTAppDelegate", "#4e79a7"),
    ("Enemies & bosses", "Enemies/", "#e15759"),
    ("Player & weapons", "Player", "#f28e2b"),
    ("Effects & stage objects", ("Effect", "StageEffects", "Objects", "Stage.m", "Wall", "Missile", "Camera"), "#76b7b2"),
    ("Sound library", ("SoundLibrary", "AudioSupport"), "#59a14f"),
    ("Graphics / textures / GL view", ("Texture", "EAGLView", "DWGraphics", "TextureManager"), "#edc948"),
    ("Data, saves, results, utilities", ("GResult", "GSaveCtrl", "DWUtilities", "TableReader", "GameMsg", "DWconnect", "DWWebView", "DebugDisp", "MenuScroll"), "#b07aa1"),
]


def group_of(src):
    for name, key, col in GROUPS:
        keys = key if isinstance(key, tuple) else (key,)
        if any(k in src for k in keys):
            return name, col
    return "Compiler / linker glue", "#9c9c9c"


def load():
    src = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "analysis/symbols/function_map.csv"))):
        src[int(r["address"], 16)] = r["source_file"]
    st, cov = {}, {}
    for l in open(os.path.join(ROOT, "analysis/verification/function_status.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0].startswith("0x"):
            st[int(p[0], 16)] = (p[1], p[4], p[5] if len(p) > 5 else "")
    for l in open(os.path.join(ROOT, "analysis/verification/test_coverage.tsv")):
        p = l.rstrip("\n").split("\t")
        if p[0].startswith("0x"):
            cov[int(p[0], 16)] = (int(p[4]), int(p[5]), int(p[7]))
    return src, st, cov


def evidence():
    """Best evidence class per function from the result rows (current build)."""
    cdir = os.path.join(ROOT, "recovered/compile")
    cur = {os.path.basename(f)[:-3]: open(f).read().strip() for f in glob.glob(os.path.join(cdir, "fn", "*.fp"))}
    ev = collections.defaultdict(set)
    for path in glob.glob(os.path.join(cdir, "difftest_*.jsonl")):
        for l in open(path):
            if '"pass"' not in l:
                continue
            r = json.loads(l)
            if r.get("fp") != cur.get(r["addr"]):
                continue
            d = r.get("detail", "")
            tier = "boundary" if d.startswith(("fw-", "callee", "placeholder")) else "plain"
            ev[int(r["addr"], 16)].add((r.get("source") == "synthetic", tier))
    return ev


def fig_memory_map():
    segs, secs = [], []
    for l in open(os.path.join(ROOT, "analysis/notes/macho_loadcommands.txt")):
        m = re.match(r"\s+(__[A-Z]+)\s+vm=0x([0-9a-f]+)\+0x([0-9a-f]+)", l)
        if m:
            segs.append((m.group(1), int(m.group(2), 16), int(m.group(3), 16)))
        m = re.match(r"\s+(__\w+)\s+addr=0x([0-9a-f]+) size=\s*0x([0-9a-f]+)", l)
        if m:
            secs.append((m.group(1), int(m.group(2), 16), int(m.group(3), 16)))
    fig, ax = plt.subplots(figsize=(11, 2.8))
    lo, hi = 0x1000, 0x89000
    for i, (n, a, s) in enumerate([x for x in segs if x[0] != "__PAGEZERO" and x[2] > 0 and x[1] < hi]):
        ax.add_patch(Rectangle((a, 2.2), s, 0.6, color=["#4e79a7", "#f28e2b"][i % 2], alpha=.85))
        ax.text(a + s / 2, 2.5, "%s  0x%x-0x%x" % (n, a, a + s), ha="center", va="center", color="white", fontsize=9, weight="bold")
    shown = [x for x in secs if x[2] >= 0x400]
    cols = plt.cm.tab20.colors
    small = []
    for i, (n, a, s) in enumerate(shown):
        ax.add_patch(Rectangle((a, 1.1), s, 0.7, color=cols[i % 20]))
        if s >= 0x6000 and n != "__text":
            ax.text(a + s / 2, 1.45, "%s\n%d KB" % (n, s // 1024), ha="center", va="center", fontsize=7)
        elif n != "__text":
            small.append("%s %s" % (n, "%d KB" % (s // 1024) if s >= 1024 else "%d B" % s))
    ax.text(0x1000, 0.55, "smaller sections: " + ", ".join(small), fontsize=7, va="center")
    ax.annotate("1,395 functions\n(Thumb + ARM code)", xy=(0x25bc + 0x2c000, 1.45), ha="center", va="center", fontsize=8, color="white", weight="bold")
    ax.set_xlim(lo, hi); ax.set_ylim(0.3, 3.0); ax.set_yticks([])
    ax.set_xticks(range(0, hi + 1, 0x10000)); ax.set_xticklabels(["0x%x" % x for x in range(0, hi + 1, 0x10000)])
    ax.set_title("MGSTUS v2.3.0 (armv6 Mach-O): memory map of segments and sections")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "memory_map.svg")); plt.close(fig)


def fig_text_map(src, st, cov, ev):
    insns = collections.Counter()
    for l in open(os.path.join(ROOT, "recovered/compile/function_insns.tsv")) if os.path.exists(os.path.join(ROOT, "recovered/compile/function_insns.tsv")) else []:
        p = l.split("\t")
        if p[0] != "function":
            insns[int(p[0], 16)] += 1
    addrs = sorted(st)
    ends = addrs[1:] + [0x5a614]
    fig, ax = plt.subplots(figsize=(12, 3.6))
    for a, e in zip(addrs, ends):
        name, col = group_of(src.get(a, ""))
        ax.add_patch(Rectangle((a, 2.0), e - a, 0.8, color=col, lw=0))
        v = st[a][1]
        if st[a][2]:
            ec = "#7f7f7f"
        else:
            kinds = ev.get(a, set())
            ec = "#1a7f37" if (False, "plain") in kinds else "#7bc96f" if any(not s for s, _ in kinds) else \
                "#f2c14e" if (True, "plain") in kinds else "#f08a24" if kinds else ("#1a7f37" if v == "pass" else "#d62728")
        ax.add_patch(Rectangle((a, 1.0), e - a, 0.8, color=ec, lw=0))
        n, c, _ = cov.get(a, (0, 0, 0))
        pct = c / n if n else 0
        ax.add_patch(Rectangle((a, 0.0), e - a, 0.8, color=plt.cm.viridis(pct), lw=0))
    ax.set_xlim(0x25bc, 0x5a614); ax.set_ylim(-0.1, 2.9)
    ax.set_yticks([0.4, 1.4, 2.4]); ax.set_yticklabels(["test coverage\n(dark 0 % to yellow 100 %)", "proof evidence", "original source group"])
    ax.set_xticks(range(0x10000, 0x5b000, 0x10000)); ax.set_xticklabels(["0x%x" % x for x in range(0x10000, 0x5b000, 0x10000)])
    from matplotlib.patches import Patch
    leg = [Patch(color=c, label=n) for n, _, c in GROUPS] + [Patch(color="#9c9c9c", label="glue / V0 audit")]
    leg += [Patch(color="#1a7f37", label="proven on real game states"), Patch(color="#7bc96f", label="real states, with boundary"),
            Patch(color="#f2c14e", label="proven by synthetic calls"), Patch(color="#f08a24", label="synthetic, with boundary")]
    ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, fontsize=7, frameon=False)
    ax.set_title("Map of the code section __text: every function in address order (width = size)")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "text_layout_map.svg")); plt.close(fig)


def squarify(vals, x, y, w, h):
    """Squarified treemap layout -> list of (x, y, w, h) in input order (vals sorted desc)."""
    rects, vals = [], list(vals)
    total = float(sum(vals)) or 1
    vals = [v * w * h / total for v in vals]

    def worst(row, side):
        s = sum(row)
        return max(max(side * side * r / (s * s), (s * s) / (side * side * r)) for r in row)
    while vals:
        side = min(w, h)
        row = [vals.pop(0)]
        while vals and worst(row + [vals[0]], side) <= worst(row, side):
            row.append(vals.pop(0))
        s = sum(row)
        if w >= h:
            cw = s / h; cy = y
            for r in row:
                rects.append((x, cy, cw, r / cw)); cy += r / cw
            x += cw; w -= cw
        else:
            ch = s / w; cx = x
            for r in row:
                rects.append((cx, y, r / ch, ch)); cx += r / ch
            y += ch; h -= ch
    return rects


def fig_treemap(src, st, cov):
    per = collections.defaultdict(lambda: [0, 0, 0])
    for a, (n, c, _) in cov.items():
        s = src.get(a, "(compiler / linker glue)").replace("Classes/../Classes/", "").replace("Classes/", "")
        per[s][0] += n; per[s][1] += c; per[s][2] += 1
    items = sorted(per.items(), key=lambda kv: -kv[1][0])
    rects = squarify([v[0] for _, v in items], 0, 0, 100, 60)
    fig, ax = plt.subplots(figsize=(12, 7.2))
    for (name, (n, c, k)), (x, y, w, h) in zip(items, rects):
        pct = c / n if n else 0
        ax.add_patch(Rectangle((x, y), w, h, facecolor=plt.cm.RdYlGn(0.15 + 0.7 * pct), edgecolor="white", lw=1.5))
        if w * h > 18:
            label = "%s\n%d fns, %d%% tested" % (name.split("/")[-1], k, round(100 * pct))
            ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=6.5 if w * h < 60 else 8)
    ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.axis("off")
    ax.set_title("The game's 67 original source files (from STABS): area = instructions, colour = share executed by passing tests")
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, norm=plt.Normalize(-15, 115)); sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.02, pad=0.01, ticks=[0, 50, 100]); cb.set_label("% of instructions tested")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "source_treemap.svg")); plt.close(fig)


def fig_evidence(st, ev):
    c = collections.Counter()
    for a, (name, v, v0) in st.items():
        k = ev.get(a, set())
        if v == "pass" and (False, "plain") in k:
            c["real game states"] += 1
        elif v == "pass" and any(not s for s, _ in k):
            c["real states + boundary"] += 1
        elif v == "pass" and (True, "plain") in k:
            c["synthetic calls"] += 1
        elif v == "pass":
            c["synthetic + boundary"] += 1
        else:
            c["manual audit (V0)"] += 1
    order = ["real game states", "real states + boundary", "synthetic calls", "synthetic + boundary", "manual audit (V0)"]
    cols = ["#1a7f37", "#7bc96f", "#f2c14e", "#f08a24", "#7f7f7f"]
    fig, ax = plt.subplots(figsize=(9, 2.6))
    left = 0
    for o, col in zip(order, cols):
        ax.barh(0, c[o], left=left, color=col)
        if c[o] > 25:
            ax.text(left + c[o] / 2, 0, "%s\n%d" % (o, c[o]), ha="center", va="center", fontsize=8,
                    color="white" if col in ("#1a7f37", "#7f7f7f") else "black")
        left += c[o]
    ax.set_xlim(0, left); ax.set_yticks([]); ax.set_xlabel("functions (all %d)" % left)
    ax.set_title("How each function's decompilation was proven (strongest evidence)")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "evidence.svg")); plt.close(fig)
    return c


def fig_progress():
    pts = [("2026-09-30", 0, "first recompile+diff"), ("2026-10-07", 380, "V4 offline diff"), ("2026-10-08 11:00", 419, "per-function ledger"),
           ("2026-10-08 16:20", 672, "frame driver"), ("2026-10-08 17:30", 1236, "synthetic calls"),
           ("2026-10-08 21:45", 1250, ""), ("2026-10-09 00:50", 1266, ""), ("2026-10-09 03:55", 1298, "OS model"),
           ("2026-10-09 09:30", 1319, "gate check"), ("2026-10-09 13:55", 1357, "boundary tiers"),
           ("2026-10-09 15:55", 1383, ""), ("2026-10-09 17:15", 1387, "GATE PASSED"), ("2026-10-11 08:30", 1389, "port-found fixes")]
    import datetime
    xs = [datetime.datetime.fromisoformat(p[0] if " " in p[0] else p[0] + " 12:00") for p in pts]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.plot(xs, [p[1] for p in pts], "-o", color="#4e79a7", ms=4)
    ax.axhline(1395, color="#999", ls="--", lw=1); ax.text(xs[0], 1405, "1,395 functions", fontsize=8, color="#666")
    for x, p in zip(xs, pts):
        if p[2]:
            ax.annotate(p[2], (x, p[1]), textcoords="offset points", xytext=(4, -12 if p[1] > 1300 else 6), fontsize=7)
    ax.set_ylabel("functions proven bit-identical"); ax.set_ylim(-30, 1480)
    ax.set_title("Verification progress: functions proven identical to the original")
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(os.path.join(OUT, "progress.svg")); plt.close(fig)


def fig_cov_hist(cov, st):
    b = collections.Counter()
    for a, (n, c, rows) in cov.items():
        if st.get(a, ("", ""))[1] != "pass" or not rows:
            continue
        p = 100.0 * c / max(1, n)
        b[min(9, int(p // 10)) if p < 100 else 10] += 1
    labels = ["%d-%d" % (i * 10, i * 10 + 9) for i in range(10)] + ["100"]
    fig, ax = plt.subplots(figsize=(9, 2.8))
    ax.bar(range(11), [b[i] for i in range(11)], color=[plt.cm.RdYlGn(0.15 + 0.07 * i) for i in range(11)])
    ax.set_xticks(range(11)); ax.set_xticklabels(labels); ax.set_xlabel("% of the function's instructions executed by passing tests")
    ax.set_ylabel("functions"); ax.set_title("Test coverage per proven function")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "coverage_hist.svg")); plt.close(fig)


def fig_mission_map():
    rows = []
    for l in open(os.path.join(ROOT, "analysis/coverage/stage_enemy_map.md")):
        m = re.match(r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|", l)
        if m:
            rows.append((int(m.group(1)), int(m.group(2)), re.findall(r"([A-Za-z]+)\(\d+\)x(\d+)", m.group(4))))
    classes = []
    for _, _, cl in rows:
        for c, _ in cl:
            if c not in classes:
                classes.append(c)
    snaps = os.listdir(os.path.join(ROOT, "oracle/reports/snap"))
    have = set()
    for s in snaps:
        m = re.match(r"campaign_(\d+)-\d+_dump(_boss|_sub(\d))?", s)
        if m:
            have.add((int(m.group(1)), int(m.group(3) or (1 if m.group(2) == "_boss" else 0))))
    surv = {int(re.match(r"campaign_(\d+)", s).group(1)) for s in snaps if s.endswith("_survival")}
    stages = sorted({(st, sub) for st, sub, _ in rows})
    fig, ax = plt.subplots(figsize=(11, 4.6))
    for j, (stg, sub) in enumerate(stages):
        cl = dict(next((r[2] for r in rows if r[0] == stg and r[1] == sub), []))
        for i, c in enumerate(classes):
            n = int(cl.get(c, 0))
            if n:
                ax.add_patch(Rectangle((j, i), 0.9, 0.9, color=plt.cm.Reds(0.25 + min(0.7, n / 30))))
                ax.text(j + 0.45, i + 0.45, str(n), ha="center", va="center", fontsize=6)
        cap = (stg, sub) in have or (sub == 0 and (stg, 0) in have)
        ax.add_patch(Rectangle((j, -1.1), 0.9, 0.8, color="#1a7f37" if cap else "#dddddd"))
        if stg in surv and sub == 0:
            ax.text(j + 0.45, -0.7, "S", ha="center", va="center", fontsize=7, color="white", weight="bold")
    ax.set_xlim(-0.2, len(stages)); ax.set_ylim(-1.3, len(classes))
    ax.set_xticks([j + 0.45 for j in range(len(stages))])
    ax.set_xticklabels(["%02d%s" % (s, "" if b == 0 else "." + str(b)) for s, b in stages], rotation=90, fontsize=7)
    ax.set_yticks([i + 0.45 for i in range(len(classes))] + [-0.7]); ax.set_yticklabels(classes + ["snapshot captured"], fontsize=7)
    ax.set_xlabel("stage.sub-stage (from the game's own stage tables)")
    ax.set_title("Mission map: enemies per stage (count) and which game states were captured from the original (S = Survival mode)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "mission_map.svg")); plt.close(fig)


def tool_summary(path):
    """First sentence of a tool's own header (docstring / leading comments)."""
    t = open(path, errors="replace").read()
    if path.endswith(".py"):
        m = re.search(r'^(?:#![^\n]*\n)?(?:#[^\n]*\n)*\s*"""(.*?)"""', t, re.S)
        txt = m.group(1) if m else ""
    elif path.endswith(".java"):
        m = re.search(r"/\*(.*?)\*/", t, re.S)
        txt = re.sub(r"^\s*\* ?", "", m.group(1), flags=re.M) if m else ""
    else:
        lines = [l[1:].strip() for l in t.splitlines()[1:40] if l.startswith("#")]
        txt = " ".join(lines)
    txt = " ".join(txt.split())
    txt = re.split(r"(?<=[.!?])\s", txt, maxsplit=1)[0] if txt else ""
    return txt[:260].replace("|", "/")


TOOL_GROUPS = [
    ("Static analysis: binary facts", ["macho.py", "dump_symbols.py", "dump_stabs.py", "build_function_map.py",
                                        "export_ghidra_symbols.py", "objc_meta.py", "objc_types.py", "parse_alrl.py",
                                        "analyze_alrl.py", "decgbi.py", "extract_ground_truth.py", "check_ipa_compat.py"]),
    ("Static analysis: Ghidra (project build, fixups, typing, export, audits)", "ghidra/*.java"),
    ("Decompiler build", ["ghidra_overlay.sh", "install_ghidra.sh", "build_ghidra_project.sh"]),
    ("Recompile + differential testing", ["mgst_recompile.py", "mgst_difftest.py", "mgst_snap.py", "mgst_retest.py",
                                           "mgst_status.py", "mgst_verify.sh", "mgst_audit.py", "mgst_difftest_report.py"]),
    ("Dynamic analysis: the oracle (emulated original)", ["setup_emulator.sh", "inject_app_offline.sh", "extract_guest_tools.py",
                                                           "oracle_live.sh", "oracle_input.py", "oracle_drive.py", "oracle_bot.py",
                                                           "mgst_launch.py", "mgst_gdb.py", "mgst_campaign.sh", "mgst_snapcampaign.sh",
                                                           "mgst_menutour.sh", "mgst_menus.sh", "mgst_probe.py", "mgst_calls.py",
                                                           "mgst_coverage.py", "mgst_aitrace.py", "mgst_gaps.py", "mgst_diffcampaign.sh"]),
    ("Checking the checker", ["mgst_mutation.py", "mgst_testcov.py", "mgst_libcheck.py"]),
    ("Packaging, port prep, publishing", ["port_audio.py", "convert_assets.py", "make_port_handoff.py", "make_github_folder.py",
                                          "prepare_github_repo.sh", "make_claude_notes.py", "install_android_ndk.sh"]),
]


def write_tools_md():
    out = ["# Tool inventory", "",
           "Every tool of the pipeline, with the first sentence of its own header (generated by",
           "`tools/make_claude_notes.py`, so it cannot drift from the code). Paths are relative to the",
           "repository root.", ""]
    seen = set()
    for title, spec in TOOL_GROUPS:
        files = sorted(glob.glob(os.path.join(ROOT, "tools", spec))) if isinstance(spec, str) else \
            [os.path.join(ROOT, "tools", f) for f in spec]
        files = [f for f in files if os.path.exists(f)]
        if not files:
            continue
        out += ["## " + title, "", "| tool | what it does |", "|---|---|"]
        for f in files:
            seen.add(os.path.realpath(f))
            out.append("| `%s` | %s |" % (os.path.relpath(f, ROOT), tool_summary(f) or "-"))
        out.append("")
    rest = [f for f in sorted(glob.glob(os.path.join(ROOT, "tools", "*.py")) + glob.glob(os.path.join(ROOT, "tools", "*.sh")))
            if os.path.realpath(f) not in seen and not f.endswith(("grant_autonomy.sh", "read_mht.py"))]
    if rest:
        out += ["## Other", "", "| tool | what it does |", "|---|---|"]
        out += ["| `%s` | %s |" % (os.path.relpath(f, ROOT), tool_summary(f) or "-") for f in rest]
        out.append("")
    open(os.path.join(ROOT, "analysis/claude_notes/TOOLS.md"), "w").write("\n".join(out))


def main():
    src, st, cov = load()
    ev = evidence()
    fig_memory_map()
    fig_text_map(src, st, cov, ev)
    fig_treemap(src, st, cov)
    c = fig_evidence(st, ev)
    fig_progress()
    fig_cov_hist(cov, st)
    fig_mission_map()
    write_tools_md()
    print("figures ->", OUT, dict(c))


if __name__ == "__main__":
    main()
