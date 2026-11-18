#!/usr/bin/env bash
# Boot the emulated iPod touch and (optionally) shut it down cleanly.
#
# Replaces the earlier inject_and_boot.sh. The handoff guide's injection
# method — guestmount the NAND as an HFS+ image and copy MGSTUS.app into
# /Applications — CANNOT work: the NAND ships as a directory of raw chip
# dumps (cs0..cs3) that QEMU's flash controller reads directly, not as a
# mountable filesystem. Injection has to happen through the guest instead
# (AFC/installd over the emulated USB link, via --usb below).
#
# IMPORTANT (from RUNNING.md): guest writes only survive a CLEAN shutdown.
# File data reaches flash promptly but HFS+ holds catalog/directory updates
# in memory, and nothing flushes them on an idle device. Killing QEMU leaves
# the data blocks with no directory entry — the file simply does not exist on
# the next boot. Only unmounting the root volume flushes the catalog, and
# only a real shutdown unmounts it. Use `--shutdown` rather than Ctrl-C.
#
# Usage:
#   boot_oracle.sh                 headless, no USB
#   boot_oracle.sh --display       open an SDL window
#   boot_oracle.sh --usb           also bring up the usbmuxd-qemu bridge, so
#                                   idevice*/install-ipa.sh can reach the guest
#   boot_oracle.sh --shutdown      clean QMP power-down of a running instance
set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
ORACLE="${PROJECT_DIR}/oracle"
FW="${ORACLE}/firmware"
SRC="${ORACLE}/qemu-ios"
STATE="${ORACLE}/state"
QMP_SOCK="/tmp/mgst-ipod.sock"
MUXD_PIDFILE="${STATE}/usbmuxd.pid"
MUXD_SOCK_FILE="${STATE}/usbmuxd.sock_addr"

log() { echo "[$(date -Iseconds)] $*"; }
die() { echo "[$(date -Iseconds)] ERROR: $*" >&2; exit 1; }

# ── parse flags (order-independent, combinable except --shutdown) ─────────
DO_SHUTDOWN=0 DO_DISPLAY=0 DO_USB=0 DO_NET=0 DO_GDB=0 DO_COVERAGE=0
COVERAGE_OUT="" SNAP_OUT=""
for a in "$@"; do
    case "$a" in
        --shutdown) DO_SHUTDOWN=1 ;;
        --display)  DO_DISPLAY=1 ;;
        --usb)      DO_USB=1 ;;
        --net)      DO_NET=1 ;;
        --gdb)      DO_GDB=1 ;;
        --coverage) DO_COVERAGE=1 ;;
        --coverage=*) DO_COVERAGE=1; COVERAGE_OUT="${a#--coverage=}" ;;
        --snap=*) SNAP_OUT="${a#--snap=}" ;;
        *) die "unknown flag: $a" ;;
    esac
done

# ── clean shutdown mode ──────────────────────────────────────────────────
if [[ "$DO_SHUTDOWN" == 1 ]]; then
    [[ -S "$QMP_SOCK" ]] || die "no QMP socket at ${QMP_SOCK} (is it running?)"
    RC=0
    if [[ -x "${SRC}/contrib/it-poweroff.sh" ]]; then
        log "requesting clean shutdown via contrib/it-poweroff.sh"
        "${SRC}/contrib/it-poweroff.sh" "$QMP_SOCK" || RC=$?
    else
        log "contrib/it-poweroff.sh not found; sending system_powerdown over QMP"
        python3 - "$QMP_SOCK" <<'PY' || RC=$?
import json, socket, sys
s = socket.socket(socket.AF_UNIX); s.connect(sys.argv[1])
f = s.makefile("rw")
f.readline()                                   # greeting
f.write(json.dumps({"execute": "qmp_capabilities"}) + "\n"); f.flush(); f.readline()
f.write(json.dumps({"execute": "system_powerdown"}) + "\n"); f.flush()
print(f.readline().strip())
PY
    fi
    # usbmuxd is no longer useful once the guest is down; only ever kill the
    # instance THIS script started (recorded pid), never pkill by name.
    if [[ -f "$MUXD_PIDFILE" ]]; then
        MPID="$(cat "$MUXD_PIDFILE" 2>/dev/null || true)"
        if [[ -n "$MPID" ]] && kill -0 "$MPID" 2>/dev/null; then
            log "stopping usbmuxd bridge (pid $MPID)"
            kill "$MPID" 2>/dev/null || true
        fi
        rm -f "$MUXD_PIDFILE" "$MUXD_SOCK_FILE"
    fi
    exit "$RC"
fi

# ── locate binary and firmware ───────────────────────────────────────────
QEMU_BIN=""
for c in "${SRC}/build/qemu-system-arm" "${SRC}/build/arm-softmmu/qemu-system-arm"; do
    [[ -x "$c" ]] && QEMU_BIN="$c" && break
done
[[ -n "$QEMU_BIN" ]] || die "qemu not built — run: run mgstouch"

BOOTROM="${FW}/bootrom_240_4"
NOR="${FW}/nor_7E18.bin"    # 7E18 = iOS 3.1.3
IBOOT="${FW}/iBoot.bin"     # 7E18 iBoot, loaded directly by IT_DIRECT_IBOOT
# setup_oracle.sh records where the extracted NAND landed; the tarball's
# top-level directory name is not guaranteed, so it is discovered by locating
# cs0 rather than hardcoded.
# NAND=<dir> in the environment overrides everything, so an alternate base
# image (e.g. nand-mgst, with the app injected offline) can be booted without
# editing this script. The overlay name is derived from the basename below, so
# each base automatically gets its own overlay — never share one across bases.
NAND="${NAND:-$(cat "${FW}/.nand_path" 2>/dev/null || true)}"
[[ -n "$NAND" ]] || NAND="$(find "$FW" -maxdepth 2 -type d -name cs0 -printf '%h\n' 2>/dev/null | head -1)"

[[ -f "$BOOTROM" ]] || die "missing ${BOOTROM}"
[[ -f "$NOR" ]]     || die "missing ${NOR}"
# iBoot is REQUIRED for 3.1.3 to boot at all. Without IT_DIRECT_IBOOT the
# bootrom finds no next stage, drops to DFU, and spins forever on USB config
# reads (symptom: serial log is nothing but repeated "USB: cfg = ..."). It is a
# separate release asset the first firmware pull missed. See LOG 2026-09-22.
[[ -f "$IBOOT" ]]   || die "missing ${IBOOT} — download iBoot.bin from the ipod-touch-2g-2026.08 release (159744 bytes)"
[[ -n "$NAND" && -d "${NAND}/cs0" ]] \
    || die "NAND not extracted (no cs0 under ${FW}) — run: run mgstouch"

# Headless by default: this box has no display for the agent, and swiftshader
# is already in use by the Android emulator. Pass --display to open a window.
DISPLAY_ARG="-display none"
[[ "$DO_DISPLAY" == 1 ]] && DISPLAY_ARG="-display sdl"

mkdir -p "${ORACLE}/reports" "$STATE"
LOGF="${ORACLE}/reports/boot_$(date +%Y%m%d_%H%M%S).log"
rm -f "$QMP_SOCK"

# ── writable NAND overlay ────────────────────────────────────────────────
# The base NAND (nand-appsync3) is read-only; QEMU records guest writes as a
# block overlay here, so installs/settings persist across boots without ever
# mutating the base image. ONE overlay per base image — an overlay replayed on
# a different base shadows blocks that mean something else there.
OVL="${STATE}/nandrw-$(basename "$NAND")"
mkdir -p "$OVL"

# ── env the fork's own launcher marks "required for 3.1.3 to boot at all" ──
# Ported from contrib/run-ipod-touch.sh (that launcher is macOS-only:
# -display cocoa). We replicate its machine config + env but stay headless.
export IT_LCD_BRIGHT=255                        # backlight scales every pixel
export IT_DIRECT_IBOOT="$IBOOT"                 # load 7E18 iBoot directly
export IT_TVOUT_READY=1                         # TV-out shutdown gates
# Open the kernel code-signing gate so the user's own sideloaded (unsigned) copy
# of MGST can exec. This IPA is not FairPlay-encrypted (cryptid=0); nothing is
# decrypted anywhere in this project.
# 3.1.3's kernel silently refuses anything not Apple-signed otherwise.
export IT_BOOT_ARGS="${IT_BOOT_ARGS:-amfi_allow_any_signature=1 cs_enforcement_disable=1}"
export IT_BOOT_ARGS_DELAY_MS="${IT_BOOT_ARGS_DELAY_MS:-1500}"
export IT_BOOT_ARGS_REPEAT="${IT_BOOT_ARGS_REPEAT:-200}"
export IT_BOOT_ARGS_INTERVAL_MS="${IT_BOOT_ARGS_INTERVAL_MS:-250}"

# ── usbmuxd-qemu bridge ─────────────────────────────────────────────────
# QEMU is the TCP CLIENT here and dials OUT to usbmuxd when the guest's USB
# core comes up — so usbmuxd must already be listening, or (per install-ipa.sh's
# own warning) the guest never attaches for the rest of that boot. Hence this
# runs BEFORE qemu is started, matching contrib/run-ipod-touch.sh's ordering.
if [[ "$DO_USB" == 1 ]]; then
    MUXD_BIN="${ORACLE}/usbmuxd-qemu/src/usbmuxd"
    [[ -x "$MUXD_BIN" ]] || die "usbmuxd not built at ${MUXD_BIN} — build oracle/usbmuxd-qemu (autogen.sh && ./configure && make)"

    QEMU_ADDR="127.0.0.1:1235"   # usbmuxd listens here; QEMU dials out to it
    CLIENT_SOCK="127.0.0.1:27015" # idevice*/install-ipa.sh connect here
    MUXD_CONF="${STATE}/usbmuxd-conf"
    mkdir -p "$MUXD_CONF"

    USBMUXD_QEMU_ADDR="$QEMU_ADDR" USBMUXD_QEMU_DELAY=100 \
        "$MUXD_BIN" -f -v -v -p -S "$CLIENT_SOCK" -P NONE -C "$MUXD_CONF" \
        > "${LOGF}.usbmuxd" 2>&1 &
    MUXD_PID=$!
    sleep 1
    if ! kill -0 "$MUXD_PID" 2>/dev/null; then
        die "usbmuxd died immediately; see ${LOGF}.usbmuxd"
    fi
    echo "$MUXD_PID" > "$MUXD_PIDFILE"
    echo "$CLIENT_SOCK" > "$MUXD_SOCK_FILE"
    export IT_USB_TCP="$QEMU_ADDR"
    log "usbmuxd bridge up (pid $MUXD_PID): clients -> $CLIENT_SOCK, guest -> $QEMU_ADDR"
    log "  connect libimobiledevice tools with: USBMUXD_SOCKET_ADDRESS=$CLIENT_SOCK ideviceinfo"
fi

# ── networking (emulated BCM4325 WiFi + slirp) ──────────────────────────
# `wifi=on` is a machine option, not an env var, so it has to be assembled
# into the -M string. Per docs/networking.md, the CURRENT 7E18 image
# auto-associates and gets DHCP/DNS/TCP via slirp with no guest-side Settings
# toggle needed. The guest reaches the host at the slirp alias 10.0.2.2.
MACHINE_EXTRA=""
NETDEV_ARGS=()
# The image runs sshd at boot (launchd label com.openssh.sshd, root/alpine), and
# slirp hands the guest 10.0.2.15, so a host port forwarded there is a root
# shell with no usbmuxd/lockdown in the path (docs/networking.md shows the same
# forwarding reaching lockdownd). This is how the GL shim is installed AFTER
# boot -- see tools/oracle_live.sh.
SSH_PORT="${SSH_PORT:-2222}"
if [[ "$DO_NET" == 1 ]]; then
    MACHINE_EXTRA=",wifi=on"
    # restrict=on: the guest cannot open ANY outbound connection (RULES.md: no
    # network calls); only the ssh hostfwd below works. Without it, a stray tap
    # in MGST opened Safari and fetched google.com (LOG 2026-09-29 STEP 5).
    NETDEV_ARGS=(-netdev "user,id=wifi0,restrict=on,hostfwd=tcp:127.0.0.1:${SSH_PORT}-10.0.2.15:22")
    log "  net    : wifi=on, slirp restrict=on — ssh port-forward only, no guest egress"
    log "  ssh    : 127.0.0.1:${SSH_PORT} -> guest 10.0.2.15:22 (root/alpine)"
fi

log "booting emulated iPod touch 2G (iOS 3.1.3 / 7E18)"
log "  qemu   : ${QEMU_BIN}"
log "  iBoot  : ${IBOOT}"
log "  nand   : ${NAND}  (overlay ${OVL})"
log "  serial : ${LOGF}"
log "  qmp    : ${QMP_SOCK}"
log "  NOTE   : SpringBoard needs ~100s of emulated boot before USB is up."
log "  NOTE   : shut down with '$0 --shutdown', NOT Ctrl-C, or writes are lost."

# No -cpu / -m 2G / -d unimp: the iPod-Touch machine sets its own armv6 CPU and
# 128 MiB is the real device's RAM. An earlier hand-rolled line overrode all
# three and, with no iBoot, never left DFU. Guest serial goes to the per-boot
# log; QEMU's own stdout/stderr to a sibling .qemu file. Control is via QMP.
# ── GDB stub ────────────────────────────────────────────────────────────
# Debugs the CPU, not a process: breakpoints are on addresses the core
# executes, so a userspace VA can in principle be hit by ANY process that has
# that address mapped. With MGST in the foreground that is nearly always MGST,
# but confirm with mgst_probe.py's context check before trusting a hit.
# NOTE: the guest is armv6 and almost all MGST code is THUMB (1388 Thumb vs 7
# ARM), so tell gdb: `set arm force-mode thumb` before placing breakpoints.
GDB_ARGS=()
if [[ "$DO_GDB" == 1 ]]; then
    GDB_ARGS=(-gdb "tcp::1234")
    log "  gdb    : tcp::1234  (target remote :1234)"
fi

# ── per-process coverage plugin (step 5) ─────────────────────────────────
# contrib/plugins/drcov_mgst.c: the SAME per-block VA drcov.c records, but
# gated per-execution on the identical Mach-O-header identity check
# mgst_probe.py's check_context() uses (reads guest memory through whichever
# context is current, not a trusted-but-unverified TTBR0/CP15 register) - so
# a block only counts as covered if MGSTUS itself was the scheduled process
# at that exact execution. Fixes the exact caveat two comments above this
# one: "a userspace VA can in principle be hit by ANY process."
PLUGIN_ARGS=()
if [[ "$DO_COVERAGE" == 1 ]]; then
    PLUGIN_LIB="${SRC}/build/contrib/plugins/libdrcov_mgst.so"
    [[ -f "$PLUGIN_LIB" ]] || die "coverage plugin not built — ninja contrib/plugins/libdrcov_mgst.so in ${SRC}/build"
    REF_EXE="${MGST_REF_EXE:-${PROJECT_DIR}/oracle/state/ipa-extract-v230/Payload/MGSTUS.app/MGSTUS}"
    [[ -f "$REF_EXE" ]] || die "coverage ref binary not found: ${REF_EXE} (set MGST_REF_EXE)"
    [[ -n "$COVERAGE_OUT" ]] || COVERAGE_OUT="${ORACLE}/reports/coverage_$(date +%Y%m%d_%H%M%S).drcov"
    mkdir -p "$(dirname "$COVERAGE_OUT")"
    # calls=: dynamic CFG edges + objc_msgSend (site, class, selector) - LOG STEP 5
    CALLS_OUT="${COVERAGE_OUT%.drcov}.calls.tsv"
    PLUGIN_ARGS=(-plugin "${PLUGIN_LIB},ref=${REF_EXE},filename=${COVERAGE_OUT},calls=${CALLS_OUT}")
    log "  coverage: ${COVERAGE_OUT}  (ref ${REF_EXE})"
    log "  calls   : ${CALLS_OUT}  (edges + msgSend receiver/selector)"
    log "  NOTE   : written on clean shutdown (plugin atexit) or QEMU exit — kill -TERM flushes it too, SIGKILL does not."
fi

# ── entry-state capture plugin (PLAN 4b V3, LOG 2026-10-07 STEP 5) ─────────
# contrib/plugins/snap_mgst.c: at sampled MGSTUS function entries, registers
# + every page the call touches (first touch), never pausing the guest.
# Decoded by tools/mgst_snap.py. Loads alongside --coverage.
if [[ -n "$SNAP_OUT" ]]; then
    SNAP_LIB="${SRC}/build/contrib/plugins/libsnap_mgst.so"
    [[ -f "$SNAP_LIB" ]] || die "snap plugin not built — ninja contrib/plugins/libsnap_mgst.so in ${SRC}/build"
    SNAP_REF="${MGST_REF_EXE:-${PROJECT_DIR}/oracle/state/ipa-extract-v230/Payload/MGSTUS.app/MGSTUS}"
    SNAP_FUNCS="${PROJECT_DIR}/analysis/symbols/function_entries.txt"
    PLUGIN_ARGS+=(-plugin "${SNAP_LIB},ref=${SNAP_REF},funcs=${SNAP_FUNCS},out=${SNAP_OUT}${SNAP_OPTS:+,${SNAP_OPTS}}")
    log "  snap    : ${SNAP_OUT}  (entry states; opts '${SNAP_OPTS:-}')"
fi

QEMU_ARGS=(
    -M "iPod-Touch,bootrom=${BOOTROM},nand=${NAND},nor=${NOR},nandrw=${OVL}${MACHINE_EXTRA}"
    -m 128M
    -serial "file:${LOGF}"
    -qmp "unix:${QMP_SOCK},server,nowait"
    $DISPLAY_ARG
    "${NETDEV_ARGS[@]}"
    "${PLUGIN_ARGS[@]}"
    "${GDB_ARGS[@]}"
)

# NOT `exec` when --usb is set: usbmuxd was started as this shell's background
# job, and a $MUXD_PID we already recorded to disk is enough to clean it up
# later regardless of exec, but keeping this a plain foreground run (not exec)
# means a Ctrl-C here also reaps usbmuxd via the EXIT trap below rather than
# leaking it. Without --usb this still execs, preserving the old contract.
if [[ "$DO_USB" == 1 ]]; then
    trap '[[ -n "${MUXD_PID:-}" ]] && kill "$MUXD_PID" 2>/dev/null; rm -f "$MUXD_PIDFILE" "$MUXD_SOCK_FILE"' EXIT
    "$QEMU_BIN" "${QEMU_ARGS[@]}" > "${LOGF}.qemu" 2>&1
else
    exec "$QEMU_BIN" "${QEMU_ARGS[@]}" > "${LOGF}.qemu" 2>&1
fi
