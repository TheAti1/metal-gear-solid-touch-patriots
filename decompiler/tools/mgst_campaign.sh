#!/usr/bin/env bash
# One capture chunk for the dynamic decompilation map (LOG 2026-09-29 STEP 5).
#
#   tools/mgst_campaign.sh FIRST LAST [MAX_SECONDS]
#
# Boots the v2.3.0 oracle with the drcov_mgst plugin (coverage + calls=:
# dynamic CFG edges and objc_msgSend receiver/selector), launches MGST, starts
# ACT1 story mode, redirects its first +[Stage setNum:] to FIRST, and lets the
# story run with god mode + HP drain (tools/mgst_gdb.py: enemies lose HP by
# memory write and die through the game's own die state - no aiming, no
# per-boss rules) while tools/oracle_drive.py only presses READY/NEXT/taps. Stops when MGST calls
# setNum:(LAST+1) or MAX_SECONDS pass, detaches gdb, then SIGTERMs QEMU so the
# plugin writes oracle/reports/campaign_FIRST-LAST.{drcov,calls.tsv}.
#
# SNAP=1 also loads the snap_mgst entry-state capture plugin into
# oracle/reports/snap/$TAG (PLAN 4b V3); SNAP_OPTS passes plugin options.
# SNAP=dump: the plugin's full-speed DUMP mode instead (PLAN 4b route step 3):
# a full-process snapshot at -[CrashLandingAppDelegate renderScene] every
# DUMP_EVERY frames and ~20 s after every stage / sub-stage change.
#
# Network: --net is restrict=on (ssh port-forward only, no guest egress).
set -uo pipefail
cd "$(dirname "$0")/.."
FIRST=$1 LAST=$2 MAX=${3:-3600}
TAG=$(printf "campaign_%02d-%02d" "$FIRST" "$LAST")
# capture runs get their own names: never overwrite an earlier coverage run's
# .drcov/.calls.tsv (LOG 2026-10-07: the first SNAP chunk truncated 01-04)
[[ ${SNAP:-0} == 1 ]] && TAG=${TAG}_snap
[[ ${SNAP:-0} == dump ]] && TAG=${TAG}_dump
# SUBSTAGE=N: start the stage in sub-stage N (boss phases; mgst-substage)
# SURVIVAL=1 (or SURVIVAL=<maxHP>): play in Survival mode (mgst-survival;
#   a number also forces +[Player initHP:] to it)
# TAG_SUFFIX (e.g. _boss): a second campaign over the same stages keeps the first
TAG=${TAG}${TAG_SUFFIX:-}
R=oracle/reports
W=${MGST_WORK:-$R/$TAG.work}
mkdir -p "$W"
log() { echo "[$(date +%H:%M:%S)] $*"; }

pgrep -x qemu-system-arm >/dev/null && { echo "QEMU already running" >&2; exit 1; }
SNAPARG=()
[[ ${SNAP:-0} == 1 ]] && SNAPARG=(--snap=$PWD/$R/snap/$TAG)
SNAPDIR=$PWD/$R/snap/$TAG
if [[ ${SNAP:-0} == dump ]]; then
    SNAPARG=(--snap=$SNAPDIR)
    export SNAP_OPTS="dumpfn=a2c0,dumpevery=${DUMP_EVERY:-1800},dumpmax=${DUMP_MAX:-60}"
fi
NAND=$PWD/oracle/firmware/nand-mgst-v230 nohup oracle/scripts/boot_oracle.sh \
    --net --gdb --coverage=$R/$TAG.drcov "${SNAPARG[@]}" > "$W/boot.log" 2>&1 &
# a boot that never reaches ssh must not leave QEMU behind (it blocked every
# later chunk with "QEMU already running", LOG 2026-10-08)
tools/oracle_live.sh wait > /dev/null 2>&1 || {
    log "no ssh - stopping QEMU"
    Q=$(pgrep -x qemu-system-arm); [[ -n $Q ]] && { kill -TERM $Q; while kill -0 $Q 2>/dev/null; do sleep 1; done; }
    exit 1; }
log "booted"
launched=0
for try in 1 2 3; do
    python3 tools/oracle_input.py orient 1 > /dev/null
    if python3 tools/mgst_launch.py > "$W/launch.log" 2>&1; then launched=1; break; fi
    log "launch attempt $try failed; pressing Home and retrying"
    python3 -c "import sys; sys.path.insert(0,'oracle/qemu-ios/imgtools'); from itqmp import QMP; q=QMP('/tmp/mgst-ipod.sock'); q.cmd('send-key', keys=[{'type':'qcode','data':'home'}])" 2>/dev/null
    sleep 10
done
if [[ $launched == 0 ]]; then
    log "MGST did not launch - aborting chunk (no blind driving)"
    Q=$(pgrep -x qemu-system-arm); kill -TERM $Q; while kill -0 $Q 2>/dev/null; do sleep 1; done
    exit 2
fi
python3 tools/oracle_input.py orient 3; sleep 30
python3 tools/oracle_input.py tap 240 160; sleep 8      # title -> menu
python3 tools/oracle_input.py tap 305 160; sleep 8      # START -> mission list
python3 tools/oracle_input.py shot "$W/menu.png" > /dev/null

MGST_GDB_LOG=$W/gdb.tsv nohup gdb -q -batch -x tools/mgst_gdb.py -ex mgst-connect \
    -ex mgst-godmode -ex "mgst-drain ${DRAIN_PCT:-20}" -ex "mgst-bleed ${BLEED_PERIOD:-10} ${BLEED_PCT:-5}" -ex "mgst-stage $FIRST" ${SUBSTAGE:+-ex "mgst-substage $SUBSTAGE"} ${SURVIVAL:+-ex "mgst-survival $([[ $SURVIVAL == 1 ]] || echo $SURVIVAL)"} \
    -ex 'mgst-break 0x3f0ec setNum $r2' -ex 'mgst-break 0x3f134 setSubNum $r2' \
    -ex "mgst-run $((MAX + 120))" > "$W/gdb.log" 2>&1 &
GDB=$!
sleep 12
python3 tools/oracle_input.py tap 305 160                # ACT1 (story mode)
sleep 8
python3 tools/oracle_drive.py "$MAX" "$W/frames" > "$W/drive.log" 2>&1 &
DRV=$!
log "running stages $FIRST..$LAST (max ${MAX}s)"

NEXT=$(printf "0x%x" $((LAST + 1)))
T0=$(date +%s)
LASTN=0; TPROG=$T0
while kill -0 $DRV 2>/dev/null; do
    N=$(awk -F'\t' '$5==1 && ($3=="setNum" || $3=="setSubNum")' "$W/gdb.tsv" 2>/dev/null | wc -l)
    if (( N != LASTN )); then
        LASTN=$N; TPROG=$(date +%s)
        # dump mode: snapshot each new stage / sub-stage once it is running
        [[ ${SNAP:-0} == dump ]] && ( sleep 20; touch "$SNAPDIR/dump.request" ) &
    fi
    if (( $(date +%s) - TPROG > ${STALL:-1800} )); then
        log "STALL: no stage/sub-stage change for ${STALL:-1800}s - ending chunk (data kept)"; break
    fi
    if awk -F'\t' -v n="$NEXT" '$3=="setNum" && $5==1 && $11==n' "$W/gdb.tsv" 2>/dev/null | grep -q .; then
        log "setNum($NEXT) seen - chunk done"; sleep 20; break
    fi
    (( $(date +%s) - T0 > MAX )) && { log "timeout"; break; }
    sleep 15
done
kill $DRV 2>/dev/null
kill -INT $GDB 2>/dev/null; while kill -0 $GDB 2>/dev/null; do sleep 1; done
Q=$(pgrep -x qemu-system-arm); kill -TERM $Q; while kill -0 $Q 2>/dev/null; do sleep 1; done
log "stages seen: $(awk -F'\t' '$3=="setNum" && $5==1{printf "%d ", strtonum($11)}' "$W/gdb.tsv")"
grep -E "autohit|godmode|shake|rangegate" "$W/gdb.log" | tail -20
ls -l $R/$TAG.drcov $R/$TAG.calls.tsv
