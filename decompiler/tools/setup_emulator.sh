#!/usr/bin/env bash
# Allow the Android emulator to run under SELinux, and create the test AVD.
#
# ROOT CAUSE (from the audit log, not guesswork):
#   AVC avc: denied { execheap } for comm="RenderThread"
#       exe=".../qemu-system-x86_64-headless"  sig=11
#
# The emulator's software GL renderer (swiftshader) JIT-compiles shaders into
# heap memory and then executes it. SELinux denies executable heap to
# unconfined user processes by default, so the render thread is SIGSEGV'd the
# moment it starts — the emulator dies partway through boot every time, with
# nothing in its own log to explain why.
#
# SECURITY NOTE: `selinuxuser_execheap` is a system-wide relaxation. It lets
# ANY unconfined user process mark its heap executable, weakening a hardening
# measure against certain memory-corruption exploits. That is a normal and
# widely-accepted trade-off on a development workstation running the Android
# emulator, but it is a real trade-off and should be a deliberate choice.
# If you would rather not make it, test on a physical device over adb instead
# and skip this script entirely.
set -euo pipefail

SUDO="${SUDO:-sudo}"
SDK_ROOT="${ANDROID_HOME:-/opt/android-sdk}"
AVD_NAME="mgst"
AVD_HOME="${HOME}/.android/avd"
SYS_IMAGE="system-images/android-34/default/x86_64"

log() { echo "[$(date -Iseconds)] $*"; }
die() { echo "[$(date -Iseconds)] ERROR: $*" >&2; exit 1; }

# ── SELinux ──────────────────────────────────────────────────────────────
if command -v getenforce >/dev/null 2>&1 && [[ "$(getenforce)" == "Enforcing" ]]; then
    if [[ "$(getsebool selinuxuser_execheap 2>/dev/null | awk '{print $3}')" == "on" ]]; then
        log "selinuxuser_execheap already enabled."
    else
        log "Enabling selinuxuser_execheap (required by the emulator's GL renderer)..."
        $SUDO setsebool -P selinuxuser_execheap 1 \
            || die "setsebool failed"
        log "Enabled."
    fi
else
    log "SELinux not enforcing — nothing to change."
fi

# ── AVD ──────────────────────────────────────────────────────────────────
# Written directly rather than via avdmanager: avdmanager on this box throws
# a Java string error reading stdin and silently creates nothing.
[[ -d "${SDK_ROOT}/${SYS_IMAGE}" ]] || die "missing system image ${SYS_IMAGE}"

if [[ -f "${AVD_HOME}/${AVD_NAME}.avd/config.ini" ]]; then
    log "AVD '${AVD_NAME}' already exists."
else
    log "Creating AVD '${AVD_NAME}' ..."
    mkdir -p "${AVD_HOME}/${AVD_NAME}.avd"
    cat > "${AVD_HOME}/${AVD_NAME}.ini" <<EOF
avd.ini.encoding=UTF-8
path=${AVD_HOME}/${AVD_NAME}.avd
path.rel=avd/${AVD_NAME}.avd
target=android-34
EOF
    cat > "${AVD_HOME}/${AVD_NAME}.avd/config.ini" <<EOF
avd.ini.encoding=UTF-8
AvdId=${AVD_NAME}
abi.type=x86_64
avd.ini.displayname=${AVD_NAME}
hw.cpu.arch=x86_64
hw.cpu.ncore=4
hw.ramSize=2048
hw.gpu.enabled=yes
hw.gpu.mode=swiftshader_indirect
hw.lcd.density=320
hw.lcd.width=720
hw.lcd.height=1280
hw.keyboard=yes
disk.dataPartition.size=6G
image.sysdir.1=${SYS_IMAGE}/
tag.id=default
tag.display=Default
EOF
    log "Created ${AVD_HOME}/${AVD_NAME}.avd"
fi

command -v adb >/dev/null 2>&1 && adb start-server >/dev/null 2>&1 || true

log "SUCCESS: emulator prerequisites ready."
log "Launch with:"
log "  ${SDK_ROOT}/emulator/emulator -avd ${AVD_NAME} -no-window -no-audio -gpu swiftshader_indirect"
