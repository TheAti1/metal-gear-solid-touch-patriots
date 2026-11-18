#!/usr/bin/env bash
# Menu tour: full-process snapshots of the title-menu screens that the mission
# campaign never shows (PLAN 4b route step 2, LOG 2026-10-08).
#
#   tools/mgst_menutour.sh [SETTLE_SECONDS] [SCENE ...]
#
# Boots the v2.3.0 oracle with snap_mgst in DUMP mode (only requested dumps),
# launches MGST, taps title -> menu, then `mgst-tour` (tools/mgst_gdb.py)
# switches -[CrashLandingAppDelegate GameScene]'s _Scene the way the title menu
# does and requests one snapshot per scene after SETTLE seconds.
# Scenes (from GameScene's switch): 10 Drebin shop, 24 shop announce,
# 5/9 shooting-mode stage select, 14/17 manual, 15 options, 18 credits,
# 19 radio, 20 movies, 21 history, 12/13/22 small screens.
# MGST_TOUR_TAPS="x,y;x,y" (landscape 480x320): after each reached scene, tap
# each point and snapshot the next frame (natural in-screen states).
# Snapshots: oracle/reports/snap/menutour_dump/. Network: --net restrict=on.
set -uo pipefail
cd "$(dirname "$0")/.."
SETTLE=${1:-20}; shift || true
SCENES=("$@")
[[ ${#SCENES[@]} -gt 0 ]] || SCENES=(15 18 21 17 14 19 20 10 24 5 9 12 13 22)
TAG=menutour_dump${TAG_SUFFIX:-}
R=oracle/reports
W=$R/$TAG.work
SNAPDIR=$PWD/$R/snap/$TAG
mkdir -p "$W"
log() { echo "[$(date +%H:%M:%S)] $*"; }

pgrep -x qemu-system-arm >/dev/null && { echo "QEMU already running" >&2; exit 1; }
export SNAP_OPTS="dumpfn=a2c0,dumpevery=100000000,dumpmax=${DUMP_MAX:-120}"
NAND=$PWD/oracle/firmware/nand-mgst-v230 nohup oracle/scripts/boot_oracle.sh \
    --net --gdb --coverage=$R/$TAG.drcov --snap=$SNAPDIR > "$W/boot.log" 2>&1 &
tools/oracle_live.sh wait > /dev/null 2>&1 || { log "no ssh"; exit 1; }
log "booted"
launched=0
for try in 1 2 3; do
    python3 tools/oracle_input.py orient 1 > /dev/null
    if python3 tools/mgst_launch.py > "$W/launch.log" 2>&1; then launched=1; break; fi
    log "launch attempt $try failed; pressing Home and retrying"
    python3 -c "import sys; sys.path.insert(0,'oracle/qemu-ios/imgtools'); from itqmp import QMP; q=QMP('/tmp/mgst-ipod.sock'); q.cmd('send-key', keys=[{'type':'qcode','data':'home'}])" 2>/dev/null
    sleep 10
done
stop_qemu() { Q=$(pgrep -x qemu-system-arm); [[ -n $Q ]] && { kill -TERM $Q; while kill -0 $Q 2>/dev/null; do sleep 1; done; }; }
if [[ $launched == 0 ]]; then log "MGST did not launch - aborting"; stop_qemu; exit 2; fi
python3 tools/oracle_input.py orient 3; sleep 30
python3 tools/oracle_input.py tap 240 160; sleep 8      # title -> menu
python3 tools/oracle_input.py shot "$W/title.png" > /dev/null
log "touring scenes ${SCENES[*]} (settle ${SETTLE}s)"
NTAPS=$(echo "${MGST_TOUR_TAPS:-}" | tr ';' '\n' | grep -c ,)
export MGST_TOUR_TAPS=${MGST_TOUR_TAPS:-}
MGST_GDB_LOG=$W/gdb.tsv timeout $(( ${#SCENES[@]} * (SETTLE + 20 + NTAPS * 6) + 120 )) \
    gdb -q -batch -x tools/mgst_gdb.py -ex mgst-connect \
    -ex "mgst-tour $SNAPDIR $SETTLE ${SCENES[*]}" > "$W/gdb.log" 2>&1
grep "mgst-tour" "$W/gdb.log"
python3 tools/oracle_input.py shot "$W/last.png" > /dev/null
sleep 10
stop_qemu
log "done: $(ls $SNAPDIR 2>/dev/null | wc -l) file(s) in $SNAPDIR"
