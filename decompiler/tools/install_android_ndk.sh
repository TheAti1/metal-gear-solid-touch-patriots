#!/usr/bin/env bash
# Install the Android NDK + CMake needed for the mgstouch native core.
#
# The port strategy is a portable C++ core mirroring the 67 recovered source
# files behind a JNI boundary, so the NDK is a hard requirement. The SDK on
# this box already has build-tools 34 and platform-34 but no NDK.
#
# /opt/android-sdk is owned by the invoking user, so sdkmanager runs
# unprivileged — no $SUDO needed here, unlike the Ghidra installer.
#
# Idempotent: exits 0 if the pinned NDK is already present.
set -euo pipefail

SDK_ROOT="${ANDROID_HOME:-/opt/android-sdk}"

# NDK r27 is the current long-term-support line. Pinned rather than "latest"
# so a future session rebuilds against exactly this toolchain.
NDK_VERSION="27.3.13750724"
# The CMake version Android Gradle Plugin expects to find in the SDK.
CMAKE_VERSION="3.22.1"

log() { echo "[$(date -Iseconds)] $*"; }
die() { echo "[$(date -Iseconds)] ERROR: $*" >&2; exit 1; }

SDKMANAGER="${SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager"
if [[ ! -x "$SDKMANAGER" ]]; then
    SDKMANAGER="$(find "${SDK_ROOT}/cmdline-tools" -name sdkmanager -type f \
                  2>/dev/null | head -1)"
fi
[[ -x "$SDKMANAGER" ]] || die "no sdkmanager under ${SDK_ROOT}/cmdline-tools"

# sdkmanager needs a JDK; Gradle on this box runs on /opt/jdk-17 and the SDK
# tools are happiest there too. Do NOT let this pick up the JDK 21 that
# Ghidra is pinned to, or the JDK 25 system default.
if [[ -d /opt/jdk-17 ]]; then
    export JAVA_HOME=/opt/jdk-17
fi
log "sdkmanager: ${SDKMANAGER}"
log "JAVA_HOME : ${JAVA_HOME:-<unset>}"

NDK_DIR="${SDK_ROOT}/ndk/${NDK_VERSION}"
TOOLCHAIN="${NDK_DIR}/build/cmake/android.toolchain.cmake"
CLANG="${NDK_DIR}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang"
CMAKE_BIN="${SDK_ROOT}/cmake/${CMAKE_VERSION}/bin/cmake"

# Presence of the directory is NOT proof of installation. The NDK is a ~700 MB
# download; if it is interrupted, sdkmanager leaves an empty version directory
# behind. Testing `-d` there would report "already installed" on every future
# run, skip the download, and then die at verification — permanently wedged
# with no path to recovery. Test for the artifacts that only exist once the
# archive is fully unpacked, and clear a partial tree so the retry is clean.
ndk_complete() {
    [[ -f "$TOOLCHAIN" && -x "$CLANG" && -f "${NDK_DIR}/source.properties" ]]
}

cmake_complete() {
    [[ -x "$CMAKE_BIN" ]]
}

NEED=()
if ndk_complete; then
    log "NDK ${NDK_VERSION} already installed and complete."
else
    if [[ -d "$NDK_DIR" ]]; then
        log "NDK dir exists but is incomplete ($(du -sh "$NDK_DIR" 2>/dev/null \
            | cut -f1)) — removing partial install before retry."
        rm -rf "$NDK_DIR"
    fi
    NEED+=("ndk;${NDK_VERSION}")
fi

if cmake_complete; then
    log "CMake ${CMAKE_VERSION} already installed and complete."
else
    rm -rf "${SDK_ROOT}/cmake/${CMAKE_VERSION}"
    NEED+=("cmake;${CMAKE_VERSION}")
fi

if [[ ${#NEED[@]} -gt 0 ]]; then
    log "Accepting SDK licenses ..."
    # sdkmanager reads one y/N per license from stdin; `yes` answers them all.
    # It exits non-zero when there is nothing left to accept, which is not an
    # error here, hence the guard.
    yes 2>/dev/null | "$SDKMANAGER" --licenses >/dev/null 2>&1 || true

    log "Installing: ${NEED[*]}"
    log "NOTE: the NDK is ~700 MB. Do not interrupt — a killed download"
    log "      leaves a partial tree (this run will clear and retry it)."

    # Output goes to a file, not through a pipe. Piping into grep/tail would
    # let THEIR exit status become the pipeline's under `set -o pipefail`, so
    # a successful install with no matching lines would report as a failure —
    # the same trap that made the Ghidra smoke test lie earlier.
    SDK_OUT="$(mktemp)"
    rc=0
    "$SDKMANAGER" --install "${NEED[@]}" >"$SDK_OUT" 2>&1 || rc=$?
    # Collapse the progress spinner: unfiltered it writes tens of thousands of
    # \r-separated frames into launch.log as one unreadable line.
    tr '\r' '\n' <"$SDK_OUT" | grep -viE '^\s*\[=*\s*\]|^\s*$' | tail -15 || true
    rm -f "$SDK_OUT"
    [[ "$rc" -eq 0 ]] || die "sdkmanager install failed (exit ${rc})"
fi

# ── Verify ───────────────────────────────────────────────────────────────
ndk_complete || die "NDK still incomplete at ${NDK_DIR} after install \
(expected ${TOOLCHAIN} and ${CLANG})"
cmake_complete || die "CMake still incomplete at ${CMAKE_BIN}"

log "NDK       : ${NDK_DIR}"
log "toolchain : ${TOOLCHAIN}"
log "clang     : $("$CLANG" --version 2>&1 | head -1)"
log "cmake     : ${SDK_ROOT}/cmake/${CMAKE_VERSION}"
log "SUCCESS: Android NDK ${NDK_VERSION} ready."
