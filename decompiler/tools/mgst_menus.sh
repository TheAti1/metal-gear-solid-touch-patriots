#!/usr/bin/env bash
# Capture chunk for code the story campaign never reaches (LOG 2026-09-29
# STEP 5): title sub-menus (SPECIAL, DREBIN'S SHOP, OPTIONS, "?" help) and
# SURVIVAL mode, with the same coverage + calls= capture as mgst_campaign.sh.
#
#   tools/mgst_menus.sh [SURVIVAL_SECONDS]
#
# SURVIVAL appears first in the mission list when SaveData[0x10] > 0
# (title menu code, MGSTAppDelegate ~0x10200); the save is edited over ssh
# (restrict=on net) BEFORE MGST launches, with the original kept as
# SAVE.data.pre_survival next to it.
set -uo pipefail
cd "$(dirname "$0")/.."
SURV=${1:-900}
TAG=campaign_menus
R=oracle/reports
W=$R/$TAG.work
mkdir -p "$W/shots"
log() { echo "[$(date +%H:%M:%S)] $*"; }
shot() { python3 tools/oracle_input.py shot "$W/shots/$1.png" > /dev/null; }
tap() { python3 tools/oracle_input.py tap "$1" "$2" > /dev/null; sleep "${3:-5}"; }

pgrep -x qemu-system-arm >/dev/null && { echo "QEMU already running" >&2; exit 1; }
NAND=$PWD/oracle/firmware/nand-mgst-v230 nohup oracle/scripts/boot_oracle.sh \
    --net --gdb --coverage=$R/$TAG.drcov > "$W/boot.log" 2>&1 &
tools/oracle_live.sh wait > /dev/null 2>&1 || { log "no ssh"; exit 1; }
log "booted"

# enable SURVIVAL: SaveData[0x10] = 2 (2 = newly unlocked, as the game writes it)
DOC=$(tools/oracle_live.sh sh 'ls -d /private/var/mobile/Applications/*/Documents' 2>/dev/null | grep Documents | head -1)
tools/oracle_live.sh sh "cd $DOC && cp -n SAVE.data SAVE.data.pre_survival && cp SAVE.data /tmp/s" > /dev/null 2>&1
sshpass -p alpine scp -O -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -o PreferredAuthentications=password -o PubkeyAuthentication=no -P 2222 \
    "root@127.0.0.1:$DOC/SAVE.data" "$W/SAVE.before" 2>/dev/null
python3 - "$W/SAVE.before" "$W/SAVE.survival" <<'EOF'
import sys
d = bytearray(open(sys.argv[1], "rb").read())
d[0x10] = 2
open(sys.argv[2], "wb").write(d)
EOF
tools/oracle_live.sh put "$W/SAVE.survival" "$DOC/SAVE.data.new" > /dev/null 2>&1
tools/oracle_live.sh sh "cd $DOC && cat SAVE.data.new > SAVE.data && rm SAVE.data.new && sync" > /dev/null 2>&1
log "SaveData[0x10]=2 written"

launched=0
for try in 1 2 3; do
    python3 tools/oracle_input.py orient 1 > /dev/null
    if python3 tools/mgst_launch.py > "$W/launch.log" 2>&1; then launched=1; break; fi
    log "launch attempt $try failed; retrying"
    python3 -c "import sys; sys.path.insert(0,'oracle/qemu-ios/imgtools'); from itqmp import QMP; q=QMP('/tmp/mgst-ipod.sock'); q.cmd('send-key', keys=[{'type':'qcode','data':'home'}])" 2>/dev/null
    sleep 10
done
[[ $launched == 1 ]] || { log "MGST did not launch - abort"; Q=$(pgrep -x qemu-system-arm); kill -TERM $Q; exit 2; }
python3 tools/oracle_input.py orient 3; sleep 30
tap 240 160 8; shot title

MGST_GDB_LOG=$W/gdb.tsv nohup gdb -q -batch -x tools/mgst_gdb.py -ex mgst-connect \
    -ex mgst-godmode -ex mgst-autohit \
    -ex 'mgst-break 0x3f0ec setNum $r2' -ex 'mgst-break 0x3f134 setSubNum $r2' \
    -ex "mgst-run $((SURV + 1500))" > "$W/gdb.log" 2>&1 &
GDB=$!
sleep 12

# --- title sub-menus: each is entered, poked, screenshotted, backed out of
# (back arrow bottom-left on sub pages, down-arrow bottom-right on lists)
for m in "special 345" "drebin 385" "options 425"; do
    set -- $m
    tap "$2" 160 8; shot "$1_0"
    for i in 1 2 3; do
        tap $((240 + 60 * (i - 2))) 160 5; shot "$1_$i"
    done
    for b in "30 300" "460 298"; do tap $b 5; done
    shot "$1_back"
done
tap 460 20 6; shot help_0; tap 425 300 5; shot help_1; tap 30 300 5; tap 460 298 5
shot after_menus

# --- SURVIVAL: first entry of the mission list
tap 305 160 8; shot list
tap 305 160 10; shot survival_0
python3 tools/oracle_drive.py "$SURV" "$W/frames" > "$W/drive.log" 2>&1
log "survival drive ended: $(tail -1 "$W/drive.log")"

kill -INT $GDB 2>/dev/null; while kill -0 $GDB 2>/dev/null; do sleep 1; done
Q=$(pgrep -x qemu-system-arm); kill -TERM $Q; while kill -0 $Q 2>/dev/null; do sleep 1; done
log "stages seen: $(awk -F'\t' '$3=="setNum" && $5==1{printf "%d ", strtonum($11)}' "$W/gdb.tsv")"
ls -l $R/$TAG.drcov $R/$TAG.calls.tsv
