#!/usr/bin/env bash
# One command for the decompilation-verification loop (PLAN 4b V7).
#
#   tools/mgst_verify.sh [--no-export] [--determinism] [--frames] [--static] [--jobs N] [SNAPDIR ...]
#   --static: no differential tests (no emulator snapshots needed): export,
#             recompile, V1 audits, link, ledger
#
#   export      Ghidra (read-only): human corpus recovered/decompiled,
#               compile inputs recovered/compile, V1 facts
#   recompile   tools/mgst_recompile.py   (every function standalone)
#   audit       tools/mgst_audit.py       (V1 static audits; exit 1 = failing)
#   diff        tools/mgst_snap.py diff   (V4 offline differential, all
#               per-call captures under oracle/reports/snap/ unless SNAPDIRs given)
#   frames      (--frames) tools/mgst_snap.py frames: offline frame driver over
#               every full-process snapshot oracle/reports/snap/*_dump/
#   link        every function linked: fn/<addr>.fp = fingerprint of the tested
#               binary; the ledger ignores result rows for older builds (stale)
#   status      tools/mgst_status.py ->  analysis/verification/{function_status.tsv,status.md}
#   hashes      analysis/verification/pipeline_hashes.tsv: sha256 of the
#               export outputs, the recompile/test inputs and every pipeline
#               script (integrity: what produced these numbers)
# --determinism exports a SECOND time into a scratch dir and requires
#               byte-identical outputs (two order bugs were found 2026-10-07).
set -uo pipefail
cd "$(dirname "$0")/.."
# Default: the project-local overlay with the patched decompiler
# (tools/ghidra_overlay.sh; rebuilt only when the patches change).
if [[ -z ${GHIDRA:-} ]]; then
    tools/ghidra_overlay.sh >/dev/null || { echo "ghidra overlay build failed"; exit 2; }
    GHIDRA=build/ghidra-overlay/support/analyzeHeadless
fi
EXPORT=1 DET=0 FRAMES=0 STATIC=0 JOBS=$(nproc) DIRS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-export) EXPORT=0 ;;
        --determinism) DET=1 ;;
        --frames) FRAMES=1 ;;
        --static) STATIC=1 ;;
        --jobs) JOBS=$2; shift ;;
        *) DIRS+=("$1") ;;
    esac
    shift
done
if [[ ${#DIRS[@]} -eq 0 ]]; then
    for d in oracle/reports/snap/*/; do [[ $d == *_dump/ || $d == *_dump_*/ || $d == *menutour* ]] || DIRS+=("$d"); done
fi
log() { echo "[$(date +%H:%M:%S)] $*"; }
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

export_to() {   # $1 = compile dir, $2 = corpus dir, $3 = facts dir
    "$GHIDRA" analysis/ghidra MGST -process MGSTUS -noanalysis -readOnly -scriptPath tools/ghidra \
        -postScript ExportMgstDecompilation.java "$2" 120 \
        -postScript ExportCompilable.java "$1" -postScript DumpV1Facts.java "$3" > "$TMP/export.log" 2>&1
    grep -o 'functions written.*mismatches: [0-9]*' "$TMP/export.log" || { log "EXPORT FAILED (see $TMP/export.log)"; tail -20 "$TMP/export.log"; exit 2; }
}

if [[ $EXPORT == 1 ]]; then
    log "export"
    export_to "$PWD/recovered/compile" "$PWD/recovered/decompiled" analysis/verification/v1
fi
if [[ $DET == 1 ]]; then
    log "determinism: second export"
    mkdir -p "$TMP/c2" "$TMP/d2" "$TMP/f2"
    export_to "$TMP/c2" "$TMP/d2" "$TMP/f2"
    bad=0
    for f in functions.jsonl mgst_types.gen.h symbols.tsv extslots.tsv; do
        cmp -s "recovered/compile/$f" "$TMP/c2/$f" || { log "NOT DETERMINISTIC: $f"; bad=1; }
    done
    diff -rq recovered/decompiled "$TMP/d2" > /dev/null || { log "NOT DETERMINISTIC: recovered/decompiled"; bad=1; }
    for f in v1_jumptables.tsv v1_msgsend.tsv; do
        cmp -s "analysis/verification/v1/$f" "$TMP/f2/$f" || { log "NOT DETERMINISTIC: $f"; bad=1; }
    done
    [[ $bad == 0 ]] && log "determinism: OK (two exports byte-identical)"
fi
fail() { log "FAILED: $1"; exit 1; }
log "recompile";  rm -f recovered/compile/fn/*; python3 tools/mgst_recompile.py | grep compiled || fail recompile
log "audit";      python3 tools/mgst_audit.py | tail -1 || fail audit
if [[ $STATIC == 0 && ${#DIRS[@]} -gt 0 ]]; then
    log "diff (${DIRS[*]})"
    python3 tools/mgst_snap.py diff "${DIRS[@]}" --jobs "$JOBS" | tail -1
    python3 tools/mgst_difftest_report.py --results recovered/compile/difftest_offline.jsonl \
        --out recovered/compile/difftest_offline_report.md
fi
if [[ $FRAMES == 1 && $STATIC == 0 ]]; then
    log "frames (full-process snapshots)"
    python3 tools/mgst_snap.py frames --jobs "$JOBS" oracle/reports/snap/*_dump* | tail -1
fi
log "link (fingerprints fn/<addr>.fp for every function)"; python3 tools/mgst_snap.py link || fail link
log "status";     python3 tools/mgst_status.py || fail status
{
    echo -e "sha256\tfile"
    sha256sum recovered/compile/functions.jsonl recovered/compile/mgst_types.gen.h recovered/compile/symbols.tsv \
        recovered/compile/extslots.tsv analysis/verification/v1/*.tsv recovered/compile/difftest_offline.jsonl \
        analysis/ghidra/MGST.rep/idata/*/*.prp 2>/dev/null | awk '{print $1"\t"$2}'
    sha256sum tools/ghidra/*.java tools/mgst_*.py tools/mgst_verify.sh analysis/objc/*.tsv analysis/symbols/*.tsv \
        | awk '{print $1"\t"$2}'
} > analysis/verification/pipeline_hashes.tsv
log "done: analysis/verification/status.md"
