#!/usr/bin/env bash
# Campaign-wide capture (PLAN 4b): runs tools/mgst_campaign.sh chunk by chunk.
# SNAP=1 (default): per-call entry states (slow); SNAP=dump: full-process
# snapshots at full speed - use one short chunk per mission (stage injection
# starts any mission; it need not be completed), e.g.
#   SNAP=dump tools/mgst_snapcampaign.sh 300 $(seq -f '%g-%g' 1 20 | ...) Captures land in
# oracle/reports/snap/campaign_FIRST-LAST/; each chunk appends a progress
# line to LOG.md (resume: rerun with the chunks not yet listed).
# TAG_SUFFIX=_x names a second campaign over the same stages (no overwrite).
#
#   tools/mgst_snapcampaign.sh [MAX_SECONDS_PER_CHUNK] [FIRST-LAST ...]
set -uo pipefail
cd "$(dirname "$0")/.."
MAX=${1:-3600}; shift || true
CHUNKS=("$@")
[[ ${#CHUNKS[@]} -gt 0 ]] || CHUNKS=(1-4 5-8 9-12 13-16 17-17 18-18 19-20)
for c in "${CHUNKS[@]}"; do
    a=${c%-*}; b=${c#*-}
    tag=$(printf "campaign_%02d-%02d" "$a" "$b")
    [[ ${SNAP:-1} == dump ]] && tag=${tag}_dump
    tag=${tag}${TAG_SUFFIX:-}
    t0=$(date +%s)
    SNAP=${SNAP:-1} tools/mgst_campaign.sh "$a" "$b" "$MAX" > "oracle/reports/$tag.snaprun.log" 2>&1
    rc=$?
    q=$(ls -t oracle/reports/boot_*.log.qemu 2>/dev/null | head -1)
    summary=$(grep -h 'snap_mgst: .*samples started' "$q" 2>/dev/null | tail -1 | sed 's/^snap_mgst: //')
    nsnap=$(grep -c 'snap_mgst: snapshot ' "$q" 2>/dev/null)
    [[ ${SNAP:-1} == dump ]] && summary="$nsnap full-process snapshot(s); $summary"
    stages=$(grep -h 'stages seen' "oracle/reports/$tag.snaprun.log" | sed 's/.*stages seen: //')
    python3 - "$tag" "$rc" "$(( $(date +%s) - t0 ))" "$stages" "$summary" <<'PY'
import sys, datetime, os
tag, rc, secs, stages, summ = sys.argv[1:6]
p = "LOG.md"; s = open(p).read() if os.path.exists(p) else ""
anchor = os.environ.get("LOG_ANCHOR", "- Snapshot campaign progress (newest last):")
line = "  - %s %s: rc=%s, %ss, stages seen [%s]; %s" % (
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), tag, rc, secs, stages.strip(), summ.strip() or "no plugin summary")
with open("oracle/reports/campaign_progress.log", "a") as w:     # always (no LOG.md in a fresh checkout)
    w.write(line.strip()[2:] + "\n")
if anchor in s:
    i = s.index(anchor) + len(anchor)
    j = s.find("\n\n", i)
    s = s[:j] + "\n" + line + s[j:]
    open(p, "w").write(s)
PY
done
