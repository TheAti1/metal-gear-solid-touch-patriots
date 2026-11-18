#!/usr/bin/env bash
# Install Ghidra system-wide for the mgstouch RE work.
#
# RULES.md requires tools be installed at system level so every future session
# can use them, so this lands in /opt/ghidra with launchers on PATH, mirroring
# how /opt/android-sdk is already set up on this box (root-created, chowned to
# the invoking user so Ghidra can write its own project/config dirs).
#
# Idempotent: safe to re-run. Re-verifies an existing install rather than
# assuming a present directory means a working one.
set -euo pipefail

GHIDRA_VERSION="11.3.2"
GHIDRA_ZIP_NAME="ghidra_${GHIDRA_VERSION}_PUBLIC_20250415.zip"
GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/${GHIDRA_ZIP_NAME}"
GHIDRA_SHA256="99d45035bdcc3d6627e7b1232b7b379905a9fad76c772c920602e2b5d8b2dac2"

INSTALL_DIR="/opt/ghidra"
STAGED_DIR="/opt/ghidra_${GHIDRA_VERSION}_PUBLIC"
ZIP_PATH="/tmp/ghidra.zip"
BIN_DIR="/usr/local/bin"

SUDO="${SUDO:-sudo}"
TARGET_USER="${SUDO_USER:-$(id -un)}"

log() { echo "[$(date -Iseconds)] $*"; }
die() { echo "[$(date -Iseconds)] ERROR: $*" >&2; exit 1; }

# ── JDK 21 ───────────────────────────────────────────────────────────────
# Ghidra 11.3.2 requires JDK 21 *specifically* — not "21 or newer". The
# launcher validates the version, rejects this box's JDK 25, and then re-execs
# LaunchSupport with `-jdk_home -ask` to prompt for a path. We therefore
# provision 21 alongside the system JDK and pin Ghidra to it, leaving the
# system default and every other tool on this box untouched.
find_jdk21() {
    local home
    for home in /usr/lib/jvm/java-21-openjdk /usr/lib/jvm/java-21-openjdk-*; do
        [[ -x "${home}/bin/java" ]] && { echo "$home"; return 0; }
    done
    return 1
}

provision_jdk21() {
    if JDK21_HOME="$(find_jdk21)"; then
        log "Found JDK 21 at ${JDK21_HOME}"
    else
        log "JDK 21 not present — installing java-21-openjdk-devel ..."
        $SUDO dnf install -y java-21-openjdk-devel >/dev/null 2>&1 \
            || die "dnf install of java-21-openjdk-devel failed"
        JDK21_HOME="$(find_jdk21)" \
            || die "installed java-21-openjdk-devel but no JDK 21 under /usr/lib/jvm"
        log "Installed JDK 21 at ${JDK21_HOME}"
    fi
}

# Must run after extraction — launch.properties ships inside the Ghidra tree.
pin_jdk21() {
    local props="${INSTALL_DIR}/support/launch.properties"
    [[ -f "$props" ]] || die "missing ${props}; install looks incomplete"
    if grep -q "^JAVA_HOME_OVERRIDE=${JDK21_HOME}$" "$props"; then
        log "Already pinned to ${JDK21_HOME}"
    else
        sed -i "s|^JAVA_HOME_OVERRIDE=.*|JAVA_HOME_OVERRIDE=${JDK21_HOME}|" "$props" \
            || die "could not set JAVA_HOME_OVERRIDE in ${props}"
        log "Pinned Ghidra to JDK 21 via JAVA_HOME_OVERRIDE"
    fi
}

# ── Smoke test ───────────────────────────────────────────────────────────
# Run with no args: analyzeHeadless prints usage and exits non-zero, which is
# a successful launch. Output goes to a file rather than a pipe — piping into
# head/grep closes the pipe early and SIGPIPEs the JVM, which under
# `set -o pipefail` returns 141 and reads as failure even when the text matched.
smoke_test() {
    local out rc
    out="$(mktemp)"
    # stdin from /dev/null is load-bearing: it turns the `-ask` JDK prompt into
    # an immediate EOF. Without it, a bot/tmux session with no readable TTY
    # takes SIGTTIN on that read and the process group is *stopped* (state T),
    # waiting forever instead of failing.
    timeout 180 "${INSTALL_DIR}/support/analyzeHeadless" </dev/null >"$out" 2>&1 || rc=$?
    rc="${rc:-0}"
    if [[ "$rc" -eq 124 ]]; then
        log "--- captured output ---"; head -20 "$out"; rm -f "$out"
        die "analyzeHeadless timed out after 180s"
    fi
    if grep -qiE "Headless Analyzer|Usage:.*analyzeHeadless" "$out"; then
        rm -f "$out"; return 0
    fi
    log "--- captured output (exit ${rc}) ---"; head -20 "$out"; rm -f "$out"
    return 1
}

verify_or_die() {
    log "Smoke-testing analyzeHeadless (up to 180s; first launch is slow) ..."
    smoke_test || die "analyzeHeadless did not launch — see captured output above"
    log "SUCCESS: Ghidra ${GHIDRA_VERSION} running on JDK 21."
    log "ghidraRun       -> $(command -v ghidraRun || echo MISSING)"
    log "analyzeHeadless -> $(command -v analyzeHeadless || echo MISSING)"
}

# ── Main ─────────────────────────────────────────────────────────────────
provision_jdk21

if [[ -x "${INSTALL_DIR}/support/analyzeHeadless" ]]; then
    log "Ghidra already present at ${INSTALL_DIR} — repairing config and re-verifying."
    [[ -L "${BIN_DIR}/analyzeHeadless" ]] || \
        $SUDO ln -sf "${INSTALL_DIR}/support/analyzeHeadless" "${BIN_DIR}/analyzeHeadless"
    [[ -L "${BIN_DIR}/ghidraRun" ]] || \
        $SUDO ln -sf "${INSTALL_DIR}/ghidraRun" "${BIN_DIR}/ghidraRun"
    pin_jdk21
    verify_or_die
    exit 0
fi

# ── Fetch (reuse the existing download when it is intact) ────────────────
need_download=1
if [[ -f "$ZIP_PATH" ]]; then
    log "Found existing ${ZIP_PATH}, checking hash..."
    actual="$(sha256sum "$ZIP_PATH" | awk '{print $1}')"
    if [[ "$actual" == "$GHIDRA_SHA256" ]]; then
        log "Hash matches — reusing download."
        need_download=0
    else
        log "Hash mismatch (got ${actual}) — re-downloading."
    fi
fi

if [[ "$need_download" -eq 1 ]]; then
    log "Downloading ${GHIDRA_ZIP_NAME} ..."
    curl -fsSL -o "$ZIP_PATH" "$GHIDRA_URL" || die "download failed"
    actual="$(sha256sum "$ZIP_PATH" | awk '{print $1}')"
    [[ "$actual" == "$GHIDRA_SHA256" ]] || \
        die "SHA-256 mismatch: expected ${GHIDRA_SHA256}, got ${actual}"
    log "Download verified."
fi

unzip -tq "$ZIP_PATH" >/dev/null || die "archive failed integrity test"

# ── Install ──────────────────────────────────────────────────────────────
log "Extracting to /opt (~1.4 GB unpacked)..."
$SUDO rm -rf "$STAGED_DIR"
$SUDO unzip -q -o "$ZIP_PATH" -d /opt/
[[ -d "$STAGED_DIR" ]] || die "expected ${STAGED_DIR} after extraction"

$SUDO rm -rf "$INSTALL_DIR"
$SUDO mv "$STAGED_DIR" "$INSTALL_DIR"

# Ghidra writes project data, caches and user config inside its own tree, so it
# must be owned by the user that runs it — not root.
$SUDO chown -R "${TARGET_USER}:${TARGET_USER}" "$INSTALL_DIR"

$SUDO ln -sf "${INSTALL_DIR}/ghidraRun" "${BIN_DIR}/ghidraRun"
$SUDO ln -sf "${INSTALL_DIR}/support/analyzeHeadless" "${BIN_DIR}/analyzeHeadless"

log "Installed to ${INSTALL_DIR}, owned by ${TARGET_USER}"
pin_jdk21
verify_or_die
