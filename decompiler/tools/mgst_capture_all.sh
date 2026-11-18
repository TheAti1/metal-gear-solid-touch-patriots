#!/usr/bin/env bash
# Capture the reference set of game states (README step 7) in one run:
# the 41 snapshot sets of the reference run the published results were proven on
# (missions, boss fights, boss phases, survival, menu screens).
#
#   tools/mgst_capture_all.sh            (about 7 hours, unattended)
#   DRY=1 tools/mgst_capture_all.sh      list what would be captured
#
# Every set already captured (its samples.bin exists and is non-empty) is
# skipped, so after an interruption just run it again. Output:
# oracle/reports/snap/<set>/ (git-ignored: it is the game's memory).
set -uo pipefail
cd "$(dirname "$0")/.."
S=oracle/reports/snap
log() { echo "[capture $(date +%H:%M:%S)] $*"; }
done_() { [[ -s $S/$1/samples.bin ]]; }
step() {   # step TAG command...
    local tag=$1; shift
    if done_ "$tag"; then log "$tag: already captured"; return; fi
    if [[ ${DRY:-0} == 1 ]]; then log "$tag: would run: $*"; return; fi
    log "$tag: capturing ..."
    "$@" || log "$tag: run ended with an error (re-run this script to retry)"
    done_ "$tag" && log "$tag: ok" || log "$tag: NO snapshots"
}

# per-call entry states, mission 1 (slow capture, used by `mgst_snap.py diff`)
step campaign_01-01_snap env SNAP=1 tools/mgst_campaign.sh 1 1 900
# one full-process snapshot set per mission
for m in $(seq 1 20); do
    c=$(printf "%d-%d" "$m" "$m"); t=$(printf "campaign_%02d-%02d_dump" "$m" "$m")
    step "$t" env SNAP=dump tools/mgst_snapcampaign.sh 300 "$c"
done
# boss fights (longer runs, denser snapshots)
for m in 8 9 12 14 15 16 18 20; do
    t=$(printf "campaign_%02d-%02d_dump_boss" "$m" "$m")
    step "$t" env SNAP=dump DUMP_EVERY=900 TAG_SUFFIX=_boss tools/mgst_snapcampaign.sh 900 "$m-$m"
done
# boss phases: start the stage in a later sub-stage
for ms in 8:2 8:3 12:2 14:3 16:3 16:5 18:3; do
    m=${ms%:*} n=${ms#*:}; t=$(printf "campaign_%02d-%02d_dump_sub%d" "$m" "$m" "$n")
    step "$t" env SNAP=dump DUMP_EVERY=600 SUBSTAGE=$n TAG_SUFFIX=_sub$n tools/mgst_campaign.sh "$m" "$m" 360
done
# survival mode
for m in 16 20; do
    t=$(printf "campaign_%02d-%02d_dump_survival" "$m" "$m")
    step "$t" env SNAP=dump SURVIVAL=8 TAG_SUFFIX=_survival tools/mgst_campaign.sh "$m" "$m" 480
done
# menu screens, and taps inside them
step menutour_dump_2 env TAG_SUFFIX=_2 tools/mgst_menutour.sh 25 15 18 21 17 14 19 20 10 24 5 9 12 13 22
step menutour_dump_3 env TAG_SUFFIX=_3 tools/mgst_menutour.sh 25 5 9 12 13 22 24
step menutour_dump_taps env MGST_TOUR_TAPS="80,60;400,60;240,160;80,280;240,280;400,280" TAG_SUFFIX=_taps \
    tools/mgst_menutour.sh 20 15 12 5 9 21 20 19 13 22 14 10

n=0; for d in $S/*/; do [[ -s $d/samples.bin ]] && n=$((n + 1)); done
log "$n snapshot sets in $S"
