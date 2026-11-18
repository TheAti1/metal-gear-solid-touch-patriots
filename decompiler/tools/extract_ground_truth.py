#!/usr/bin/env python3
"""Extract gameplay ground truth from the game's OWN shipped data.

Built to validate the Android port against the original. External walkthroughs
are secondary sources and were not usable here anyway (neoseeker returns 403
to automated fetches, and video can't be read), but they would be weaker
evidence regardless: the bundle contains the authoritative tables.

Sources, all inside MGSTUS.app:
  English.lproj/Localizable.strings  binary plist, numeric keys -> UI text
  shstage<NN>_<p>.data               per-stage/phase config tables (ASCII CSV)
  shstage<NN>_<p>_ap.data            per-stage/phase spawn ("appear") tables
  Imagestage<NN>.data                per-stage background image tables

Writes analysis/verification/ground_truth.json for the test matrix to compare
against, and prints a human-readable summary.
"""
import json
import plistlib
import re
from collections import defaultdict
from pathlib import Path

APP = Path("work/extracted/Payload/MGSTUS.app")
OUT = Path("analysis/verification")

# Verified by inspection: stage titles are at a fixed stride in the string
# table, 20 entries covering 5 areas x 4 stages.
STAGE_NAME_BASE = 385
STAGE_NAME_STRIDE = 8
STAGE_COUNT = 20

# Mission objective strings occupy a contiguous block, interleaved with the
# font name each is rendered in. The objective->stage mapping is NOT assumed
# here: the game pre-renders these to textures, so the runtime index could not
# be traced from the draw code. Collected as an unordered set pending that RE.
COND_RANGE = range(545, 583)


def load_strings():
    p = APP / "English.lproj" / "Localizable.strings"
    with p.open("rb") as f:
        return plistlib.load(f)


def stage_names(d):
    out = {}
    for n in range(STAGE_COUNT):
        key = str(STAGE_NAME_BASE + STAGE_NAME_STRIDE * n)
        raw = d.get(key, "").strip()
        # Titles ship wrapped in dashes: "- MIDDLE EAST: RED ZONE -"
        title = raw.strip("- ").strip()
        area, _, loc = title.partition(":")
        out[n + 1] = {
            "title": title,
            "area": area.strip(),
            "location": loc.strip(),
        }
    return out


def objectives(d):
    seen = []
    for i in COND_RANGE:
        v = d.get(str(i), "").strip()
        # Skip the interleaved font names and any non-objective entries.
        if not v or len(v) > 80:
            continue
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9\-]*", v):   # e.g. "Helvetica-Bold"
            continue
        if not any(c.isascii() and c.isalpha() for c in v):
            continue
        seen.append({"id": i, "text": v})
    return seen


def stage_files():
    """Group stage data files by stage number and phase."""
    stages = defaultdict(lambda: {"phases": set(), "data": [], "ap": []})
    for p in sorted(APP.glob("shstage*.data")):
        m = re.match(r"shstage(\d+)_(\d+)(_ap)?\.data$", p.name)
        if not m:
            continue
        num, phase, is_ap = int(m.group(1)), int(m.group(2)), bool(m.group(3))
        s = stages[num]
        s["phases"].add(phase)
        (s["ap"] if is_ap else s["data"]).append(p.name)
    return stages


def parse_ap(path):
    """Spawn table: header row (count, ?), then one row per spawn entry.

    Row layout (9 fields), inferred from consistent column behaviour across
    all stages -- column meanings are a hypothesis, the row COUNT is not:
      [kind, x1, y1, z1, x2, y2, z2, time, n]
    """
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [int(x) for x in line.split(",") if x.strip().lstrip("-").isdigit()]
        rows.append(parts)
    if not rows:
        return {"header": [], "spawns": []}
    return {"header": rows[0], "spawns": [r for r in rows[1:] if len(r) >= 9]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = load_strings()
    names = stage_names(d)
    objs = objectives(d)
    files = stage_files()

    gt = {"stageCount": STAGE_COUNT, "stages": {}, "objectives": objs}

    for n in range(1, STAGE_COUNT + 1):
        f = files.get(n, {"phases": set(), "data": [], "ap": []})
        phases = sorted(f["phases"])
        total_spawns = 0
        for ap in f["ap"]:
            total_spawns += len(parse_ap(APP / ap)["spawns"])
        gt["stages"][str(n)] = {
            **names[n],
            "phases": len(phases),
            "dataFiles": sorted(f["data"]),
            "apFiles": sorted(f["ap"]),
            "totalSpawnEntries": total_spawns,
            # Stages with several phases are multi-part encounters; on this
            # data that is a strong boss signal but it is a HYPOTHESIS until
            # confirmed against the enemy tables.
            "multiPhase": len(phases) > 1,
        }

    (OUT / "ground_truth.json").write_text(json.dumps(gt, indent=2))

    areas = []
    for n in range(1, STAGE_COUNT + 1):
        a = gt["stages"][str(n)]["area"]
        if a not in areas:
            areas.append(a)

    print(f"stages: {STAGE_COUNT}   areas: {len(areas)}")
    for a in areas:
        ns = [n for n in range(1, STAGE_COUNT + 1)
              if gt["stages"][str(n)]["area"] == a]
        print(f"  {a:<16} stages {ns[0]}-{ns[-1]}")
    print()
    print(f"{'#':>3} {'location':<30} {'ph':>3} {'spawns':>7}  multi")
    for n in range(1, STAGE_COUNT + 1):
        s = gt["stages"][str(n)]
        print(f"{n:>3} {s['location']:<30} {s['phases']:>3} "
              f"{s['totalSpawnEntries']:>7}  {'YES' if s['multiPhase'] else ''}")
    print(f"\nobjective strings found: {len(objs)}")
    print(f"wrote {OUT/'ground_truth.json'}")


if __name__ == "__main__":
    main()
