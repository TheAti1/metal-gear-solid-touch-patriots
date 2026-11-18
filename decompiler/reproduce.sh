#!/usr/bin/env bash
# One command: your own IPA in, the verified decompilation out.
#
#   ./reproduce.sh /path/to/your.ipa              decompile (about 15 minutes + one-time installs)
#   ./reproduce.sh /path/to/your.ipa --verify     also prove it: emulator, captures, differential
#                                                 tests (several hours, unattended, resumable)
# Options: --yes (install missing tools without asking)   --jobs N   --no-audio
#
# This toolkit ships no game data. Everything it produces is derived from the
# IPA you supply and lands in git-ignored folders (work/, recovered/, build/,
# oracle/), because most of it is copyrighted material that must not be
# redistributed. Every stage skips work that is already done, so after an
# interruption just run the same command again.
set -euo pipefail

IPA="" VERIFY=0 YES=0 AUDIO=1 JOBS=$(nproc)
while [[ $# -gt 0 ]]; do
    case "$1" in
        --verify) VERIFY=1 ;;
        --yes|-y) YES=1 ;;
        --no-audio) AUDIO=0 ;;
        --jobs) JOBS=$2; shift ;;
        -h|--help) sed -n 2,13p "$0"; exit 0 ;;
        *) IPA="$1" ;;
    esac
    shift
done
OUT="$(cd "$(dirname "$0")" && pwd)/out"

EXPECT_IPA_SHA="7c9904ea40eb190b3be7af2a3cdfaccb67f8440b1605e2edadefb92c425a1f8a"
EXPECT_BIN_SHA="07ac5db07fb8909a95b23c791d20800237bf14a51de1cec32cd0be8e37773a9c"

log() { echo "[*] $*"; }
die() { echo "[!] $*" >&2; exit 1; }
ask() {   # ask "question" -> 0 = yes
    [[ $YES == 1 ]] && return 0
    [[ -t 0 ]] || return 1
    read -r -p "[?] $1 [Y/n] " a; [[ -z $a || $a == [Yy]* ]]
}

[[ -n "$IPA" ]] || die "usage: $0 /path/to/your.ipa [--verify] [--yes]"
[[ -f "$IPA" ]] || die "not found: $IPA"
IPA="$(cd "$(dirname "$IPA")" && pwd)/$(basename "$IPA")"

# ── 0. prerequisites (checked up front, so nothing fails halfway) ────────
GHIDRA_OK=0
[[ -x /opt/ghidra/support/analyzeHeadless ]] || command -v analyzeHeadless >/dev/null 2>&1 && GHIDRA_OK=1
python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null || die "Python 3.11 or newer is required"
PKGS=() PYMODS=()
for t in unzip:unzip make:make g++:gcc-c++ bison:bison flex:flex clang:clang \
         arm-none-eabi-gcc:arm-none-eabi-gcc-cs arm-none-eabi-objdump:arm-none-eabi-binutils-cs; do
    command -v "${t%%:*}" >/dev/null || PKGS+=("${t#*:}")
done
[[ $VERIFY == 1 ]] && ! command -v gdb >/dev/null && PKGS+=(gdb)
[[ $AUDIO == 1 ]] && ! command -v ffmpeg >/dev/null && log "ffmpeg not found: the optional lossless audio step will be skipped"
for m in unicorn:"unicorn>=2.1,<2.2" capstone:"capstone>=5.0,<5.1" numpy:numpy; do
    python3 -c "import ${m%%:*}" 2>/dev/null || PYMODS+=("${m#*:}")
done
if (( ${#PKGS[@]} )); then
    log "missing system packages: ${PKGS[*]}"
    command -v dnf >/dev/null || die "install them with your package manager (names above are Fedora's;
  Debian/Ubuntu: build-essential bison flex clang gcc-arm-none-eabi binutils-arm-none-eabi gdb-multiarch unzip)"
    ask "install them now with sudo dnf?" || die "install them, then re-run: sudo dnf install -y ${PKGS[*]}"
    sudo dnf install -y "${PKGS[@]}"
fi
if (( ${#PYMODS[@]} )); then
    log "missing Python modules: ${PYMODS[*]}"
    ask "install them now with pip (--user)?" || die "install them, then re-run: python3 -m pip install --user ${PYMODS[*]}"
    python3 -m pip install --user "${PYMODS[@]}"
fi
if [[ $GHIDRA_OK == 0 ]]; then
    log "Ghidra 11.3.2 + JDK 21 not found (needed to decompile)"
    ask "install them now (tools/install_ghidra.sh: /opt/ghidra, uses sudo)?" \
        || die "install them, then re-run: tools/install_ghidra.sh"
    "$(dirname "$0")/tools/install_ghidra.sh"
fi

# ── 1. verify ────────────────────────────────────────────────────────────
log "Hashing IPA ..."
GOT="$(sha256sum "$IPA" | awk '{print $1}')"
if [[ "$GOT" != "$EXPECT_IPA_SHA" ]]; then
    log "WARNING: IPA hash differs from the reference build."
    log "  expected ${EXPECT_IPA_SHA}"
    log "  got      ${GOT}"
    log "  Analysis may still work, but offsets in docs/ assume the reference."
fi

# ── 2. extract ───────────────────────────────────────────────────────────
mkdir -p "$OUT"
APP_PARENT="$OUT/extracted"
if [[ -d "$APP_PARENT/Payload" ]]; then
    log "Already extracted."
else
    log "Extracting ..."
    unzip -q -o "$IPA" -d "$APP_PARENT"
fi

APP="$(find "$APP_PARENT/Payload" -maxdepth 1 -name '*.app' | head -1)"
[[ -n "$APP" ]] || die "no .app found inside Payload/"
BIN="$APP/MGSTUS"
[[ -f "$BIN" ]] || die "executable not found at $BIN"

VER="$(python3 -c 'import plistlib,sys; p=plistlib.load(open(sys.argv[1],"rb")); print(p.get("CFBundleIdentifier"), p.get("CFBundleVersion"))' "$APP/Info.plist" 2>/dev/null || echo "unknown")"
log "Bundle: $VER"
GOTBIN="$(sha256sum "$BIN" | awk '{print $1}')"
if [[ "$GOTBIN" == "$EXPECT_BIN_SHA" ]]; then
    log "Executable hash matches reference (v2.3.0)."
elif [[ "${MGST_ALLOW_OTHER:-0}" == 1 ]]; then
    log "WARNING: executable hash differs (${GOTBIN}); continuing (MGST_ALLOW_OTHER=1)."
    log "  analysis/ and the tests describe v2.3.0 only; results for this build will not match."
else
    die "executable is not v2.3.0's (${GOTBIN}). This repository decompiles v2.3.0 only
  (see README step 1). Set MGST_ALLOW_OTHER=1 to run the static steps anyway."
fi

# The tools resolve paths relative to the working directory, matching the
# layout they were written against.
cd "$(dirname "$0")"
mkdir -p work/extracted analysis/{symbols,notes,verification} recovered/decompiled
[[ -e work/extracted/Payload ]] || ln -sfn "$APP_PARENT/Payload" work/extracted/Payload

# ── 3. static analysis (no Ghidra needed) ────────────────────────────────
log "Parsing Mach-O load commands ..."
python3 tools/macho.py > analysis/notes/macho_loadcommands.txt
grep -A2 'ENCRYPTION' analysis/notes/macho_loadcommands.txt || true

log "Dumping symbol table ..."
python3 tools/dump_symbols.py

log "Decoding STABS debug records ..."
python3 tools/dump_stabs.py > analysis/notes/stabs_summary.txt
tail -n +1 analysis/notes/stabs_summary.txt | head -20

log "Reconstructing original source tree ..."
python3 tools/build_function_map.py

log "Exporting Ghidra symbols (with ARM/Thumb modes) ..."
python3 tools/export_ghidra_symbols.py

log "Validating .al / .rl parsers ..."
python3 tools/parse_alrl.py

log "Extracting gameplay ground truth ..."
python3 tools/extract_ground_truth.py

# ── 4. decompile: patched Ghidra, project, export, recompile, audits (README steps 3-5) ──
log "Building the patched decompiler overlay ..."
tools/ghidra_overlay.sh
if [[ -e analysis/ghidra/MGST.gpr ]]; then
    log "Ghidra project exists - not rebuilding (delete analysis/ghidra/ to rebuild)."
else
    log "Building the Ghidra project from scratch (about 12 minutes) ..."
    tools/build_ghidra_project.sh analysis/ghidra "$BIN"
fi
log "Export, recompile, static audits, ledger ..."
tools/mgst_verify.sh --static --jobs "$JOBS"

# ── 5. optional: lossless audio for a port ───────────────────────────────
if [[ $AUDIO == 0 ]]; then
    :
elif [[ -d build/port_assets/audio ]]; then
    log "Audio already converted."
elif command -v ffmpeg >/dev/null 2>&1; then
    log "Converting audio losslessly (CAF -> FLAC, bit-exact check; a few minutes) ..."
    python3 tools/port_audio.py --src "$APP" --out build/port_assets/audio || log "audio conversion failed"
else
    log "ffmpeg not found - skipping audio conversion."
fi

# ── 6. optional: prove it (README steps 6-9) ─────────────────────────────
if [[ $VERIFY == 1 ]]; then
    log "Setting up the emulator (QEMU iOS fork, firmware, our patches; first run ~20 minutes) ..."
    MGST_IPA="$IPA" oracle/scripts/setup_oracle.sh
    NAND=oracle/firmware/nand-mgst-v230
    if [[ -d $NAND ]]; then
        log "App already installed in the emulator's NAND image."
    else
        log "Installing your MGSTUS.app into the emulator's NAND image (needs root once: it mounts the image) ..."
        sudo env APP_SRC="$APP" NAND_DST="$PWD/$NAND" tools/inject_app_offline.sh
    fi
    tools/mgst_capture_all.sh
    log "Differential tests over every captured state (hours; resumable) ..."
    tools/mgst_verify.sh --no-export --frames --jobs "$JOBS"
    python3 tools/mgst_snap.py calls --also untestable --jobs "$JOBS" oracle/reports/snap/*_dump*
    python3 tools/mgst_status.py
    sed -n '/^| | functions/,/^\*\*Gate/p' analysis/verification/status.md
fi

cat <<EOF

[*] Done. Output under: $(pwd)

    analysis/symbols/     function map, source tree, symbol dumps
    analysis/notes/       Mach-O layout, STABS summary
    analysis/verification/ stage/objective ground truth
    recovered/decompiled/ decompiled C, by original source file   (LOCAL ONLY)
    recovered/compile/    one compilable C file per function     (LOCAL ONLY)
    build/port_assets/    lossless audio                         (LOCAL ONLY)

    Proofs: re-run with --verify (emulator + differential tests), or compare with
    the reference results in docs/STATUS.md.

    Items marked LOCAL ONLY are derived from copyrighted material.
    Keep them local; do not redistribute.
EOF
