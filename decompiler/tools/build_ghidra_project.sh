#!/usr/bin/env bash
# Build the Ghidra project from scratch: import MGSTUS, seed every function
# entry, then apply every typing / fixup script in dependency order
# (LOG 2026-10-09; before this the project existed only as an accumulated
# local database).
#
#   tools/build_ghidra_project.sh [PROJECT_DIR] [BINARY]
#     PROJECT_DIR  default analysis/ghidra   (project name MGST, program MGSTUS)
#     BINARY       default work/extracted/Payload/MGSTUS.app/MGSTUS
#
# The project dir must not already contain MGST.gpr (no overwrite).
# Ghidra: the project-local overlay with the patched decompiler
# (tools/ghidra_overlay.sh). Inputs are all tracked files under analysis/.
# Order constraints (from LOG.md):
#   - ApplyMgstSymbols is a PRE-script of the import: every STABS/symbol-table
#     entry is seeded before auto-analysis runs.
#   - ApplyObjcTypes before ApplyCppTypes (re-running it afterwards wiped the
#     C++ class layouts, LOG 2026-10-04 regression); SizeCppClasses and
#     FixCppThis after ApplyCppTypes.
#   - ApplyCallsiteSignatures, then ApplyVarargCallsites (it replaces the
#     override at variadic sites).
#   - signature fixes (FixApcsStorage, FixVoidReturns, SetUnusedReturnsVoid)
#     before the call-site prototypes that read them.
set -euo pipefail
cd "$(dirname "$0")/.."
PROJ=${1:-analysis/ghidra}
BIN=${2:-work/extracted/Payload/MGSTUS.app/MGSTUS}
[[ -f $BIN ]] || { echo "binary not found: $BIN (extract the IPA first)"; exit 2; }
[[ -e $PROJ/MGST.gpr ]] && { echo "$PROJ/MGST.gpr exists - choose an empty directory"; exit 2; }
mkdir -p "$PROJ"
tools/ghidra_overlay.sh >/dev/null
G=build/ghidra-overlay/support/analyzeHeadless
LOGDIR=${LOGDIR:-build/ghidra-build-logs}
mkdir -p "$LOGDIR"
log() { echo "[$(date +%H:%M:%S)] $*"; }

step() {   # step NAME SCRIPT [ARGS...]
    local name=$1; shift
    log "$name"
    "$G" "$PROJ" MGST -process MGSTUS -noanalysis -scriptPath tools/ghidra -postScript "$@" \
        > "$LOGDIR/$name.log" 2>&1 || { echo "FAILED: $name (see $LOGDIR/$name.log)"; tail -20 "$LOGDIR/$name.log"; exit 1; }
    grep -E "^INFO .*\.java> " "$LOGDIR/$name.log" | sed 's/^INFO  */    /' | tail -3 || true
}

log "import + auto-analysis (symbols seeded first)"
"$G" "$PROJ" MGST -import "$BIN" -scriptPath tools/ghidra \
    -preScript ApplyMgstSymbols.java "$PWD/analysis/symbols/ghidra_symbols.tsv" > "$LOGDIR/00_import.log" 2>&1 \
    || { echo "FAILED: import"; tail -20 "$LOGDIR/00_import.log"; exit 1; }

# --- code structure
step 01_InstallSwitchCallFixup   InstallSwitchCallFixup.java
step 02_InstallSoftFloatFixup    InstallSoftFloatCallFixup.java
# after the fixups: its jumptable overrides are written only where the
# decompiler (with the switch call-fixup) reports "Could not recover jumptable"
step 03_FixSplitsAndStubs        FixSplitsAndStubs.java
step 04_ApplyDynamicCalls        ApplyDynamicCalls.java analysis/dynamic
step 05_ApplySwitchComments      ApplySwitchComments.java
# --- types
step 06_ApplyObjcTypes           ApplyObjcTypes.java analysis/objc/types.spec
step 07_ApplyCppTypes            ApplyCppTypes.java
# right after ApplyCppTypes, while `this` still points at the C++ layout it
# filled: FixDuplicateTypes keeps the struct `this` uses (run after FixCppThis,
# the opaque /_objc2_ SoundResourceManager won and the V1 size audit failed)
step 08_FixDuplicateTypes        FixDuplicateTypes.java
step 09_SizeCppClasses           SizeCppClasses.java
step 10_FixCppThis               FixCppThis.java
step 11_TypeStaticProcs          TypeStaticProcs.java
step 12_ApplyGlobalTypes         ApplyGlobalTypes.java
step 13_ApplyGlobalNames         ApplyGlobalNames.java
step 14_ApplyExternalPrototypes  ApplyExternalPrototypes.java
# --- signatures
step 15_FixApcsStorage           FixApcsStorage.java
step 16_FixStackStructLocals     FixStackStructLocals.java
step 17_CommitInferredSignatures CommitInferredSignatures.java
step 18_FixVoidReturns           FixVoidReturns.java "$LOGDIR/void_returns.tsv"
step 19_SetUnusedReturnsVoid     SetUnusedReturnsVoid.java analysis/symbols/unused_returns.tsv
step 19b_ApplyFloatReturns       ApplyFloatReturns.java analysis/symbols/float_returns.tsv
# --- call sites and variables
step 20_ApplyCallsiteSignatures  ApplyCallsiteSignatures.java
step 21_ApplyVarargCallsites     ApplyVarargCallsites.java
step 22_ApplyVarTypes            ApplyVarTypes.java analysis/symbols/var_types.tsv
log "done: $PROJ/MGST.gpr (logs in $LOGDIR)"
