#!/usr/bin/env bash
# Campaign-wide differential testing chunk (next-step 1 after step 7').
#
#   tools/mgst_diffcampaign.sh START_STAGE SECONDS
#
# Boots the oracle (--net restrict=on, --gdb), launches MGST, starts ACT1 story
# mode, runs tools/oracle_drive.py (taps only) and tools/mgst_difftest.py with
# --stage START_STAGE --godmode --drain 20, so the story advances by itself
# while every function the game calls is tested. Results append to
# recovered/compile/difftest_results.jsonl; a progress line is appended to
# LOG.md so a cut-off session can resume.
set -uo pipefail
cd "$(dirname "$0")/.."
START=$1 SECS=$2
W=oracle/reports/diffcampaign_$(printf %02d "$START").work
mkdir -p "$W"
log() { echo "[$(date +%H:%M:%S)] $*"; }

pgrep -x qemu-system-arm >/dev/null && { echo "QEMU already running" >&2; exit 1; }
NAND=$PWD/oracle/firmware/nand-mgst-v230 setsid nohup oracle/scripts/boot_oracle.sh --net --gdb \
    > "$W/boot.log" 2>&1 < /dev/null &
tools/oracle_live.sh wait > /dev/null 2>&1 || { log "no ssh"; exit 1; }
ok=0
for try in 1 2 3; do
    python3 tools/oracle_input.py orient 1 > /dev/null
    python3 tools/mgst_launch.py > "$W/launch.log" 2>&1 && { ok=1; break; }
    python3 -c "import sys; sys.path.insert(0,'oracle/qemu-ios/imgtools'); from itqmp import QMP; q=QMP('/tmp/mgst-ipod.sock'); q.cmd('send-key', keys=[{'type':'qcode','data':'home'}])" 2>/dev/null
    sleep 10
done
if [[ $ok == 0 ]]; then
    log "MGST did not launch - abort"; kill -TERM $(pgrep -x qemu-system-arm); exit 2
fi
python3 tools/oracle_input.py orient 3; sleep 30
python3 tools/oracle_input.py tap 240 160; sleep 8     # title -> menu
python3 tools/oracle_input.py tap 305 160; sleep 8     # START -> mission list
python3 tools/mgst_difftest.py --seconds "$SECS" --samples 2 --batch 256 \
    --stage "$START" --godmode --drain 20 --warmup 90 > "$W/difftest.log" 2>&1 &
DT=$!
sleep 15
python3 tools/oracle_input.py tap 305 160              # ACT1 (story) -> redirected to START
sleep 5
setsid nohup python3 tools/oracle_drive.py "$SECS" "$W/frames" > "$W/drive.log" 2>&1 < /dev/null &
DRV=$!
wait $DT
kill $DRV 2>/dev/null
kill -TERM $(pgrep -x qemu-system-arm) 2>/dev/null; sleep 5
N=$(grep -c -E "^(pass|fail|untestable|return-unverified|link-failed) " "$W/difftest.log")
python3 tools/mgst_difftest_report.py > "$W/report_tail.txt" 2>&1
TOTAL=$(grep -o "tested | [0-9]*" recovered/compile/difftest_report.md | grep -o "[0-9]*$" || true)
LINE="- $(date '+%Y-%m-%d %H:%M') chunk start-stage $START (${SECS}s): $N samples; $(grep -o 'injections: .*' "$W/difftest.log" | cut -c1-200); cumulative: $(sed -n 's/^| hit on the oracle and tested (samples: \([0-9]*\)) | \([0-9]*\) |/\2 functions (\1 samples)/p' recovered/compile/difftest_report.md), $(sed -n 's/^| \*\*pass\*\* (identical returns, memory writes, boundary calls) | \*\*\([0-9]*\)\*\* |/\1 pass/p' recovered/compile/difftest_report.md), $(sed -n 's/^| fail | \([0-9]*\) |/\1 fail/p' recovered/compile/difftest_report.md)"
python3 - "$LINE" <<'EOF'
import sys
s = open("LOG.md").read()
k = "**If cut off:**"
i = s.index(k)
j = s.index("\n", i)
s = s[:j + 1] + sys.argv[1] + "\n" + s[j + 1:]
open("LOG.md", "w").write(s)
EOF
log "$LINE"
