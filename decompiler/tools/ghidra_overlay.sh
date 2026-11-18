#!/usr/bin/env bash
# Build the project-local Ghidra overlay used by the decompilation pipeline.
#
# The system install (/opt/ghidra) is never modified. The overlay is a full
# copy of it (~0.7 GB; a symlink tree does not work: the launcher and Java
# canonicalise paths back to /opt/ghidra and load its decompiler), in which
# the native decompiler (os/linux_x86_64/decompile) is rebuilt from the
# shipped C++ source with the patches in tools/ghidra/patches/ applied.
#
# Usage: tools/ghidra_overlay.sh [--force]
# Output: build/ghidra-overlay/ (gitignored); analyzeHeadless at
#         build/ghidra-overlay/support/analyzeHeadless
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=${GHIDRA_INSTALL:-/opt/ghidra}
OUT=build/ghidra-overlay
WORK=build/ghidra-decompile-src
PATCHES=(tools/ghidra/patches/*.patch)
DEC=Ghidra/Features/Decompiler

stamp=$( (readlink -f "$SRC"; sha256sum "${PATCHES[@]}" "$0") | sha256sum | cut -c1-16)
if [[ "${1:-}" != --force && -f $OUT/.overlay_stamp && $(cat $OUT/.overlay_stamp) == "$stamp" ]]; then
    echo "overlay up to date ($OUT, stamp $stamp)"; exit 0
fi

rm -rf "$OUT" "$WORK"
mkdir -p build
cp -a "$(readlink -f "$SRC")" "$OUT"

# Rebuild the decompiler from the shipped source plus our patches.
mkdir -p "$WORK/$DEC/src/decompile"
cp -r "$SRC/$DEC/src/decompile/cpp" "$WORK/$DEC/src/decompile/"
[[ -d $SRC/$DEC/src/decompile/zlib ]] && cp -r "$SRC/$DEC/src/decompile/zlib" "$WORK/$DEC/src/decompile/"
for p in "${PATCHES[@]}"; do patch -d "$WORK" -p1 --forward < "$p"; done
make -C "$WORK/$DEC/src/decompile/cpp" -j"$(nproc)" ghidra_opt >"$WORK/build.log" 2>&1 \
    || { tail -30 "$WORK/build.log"; exit 1; }
rm -f "$OUT/$DEC/os/linux_x86_64/decompile"
install -m755 "$WORK/$DEC/src/decompile/cpp/ghidra_opt" "$OUT/$DEC/os/linux_x86_64/decompile"
echo "$stamp" > "$OUT/.overlay_stamp"
sha256sum "$OUT/$DEC/os/linux_x86_64/decompile" "${PATCHES[@]}" > "$OUT/.overlay_manifest"
echo "overlay built: $OUT (decompiler patched with ${#PATCHES[@]} patch(es))"
