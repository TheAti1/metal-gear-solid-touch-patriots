#!/usr/bin/env bash
# Install an .app into the guest filesystem OFFLINE, by editing the NAND image.
#
#     sudo tools/inject_app_offline.sh
#
# WHY THIS EXISTS (and not install-ipa.sh over USB):
# iOS 3.1.3's lockdownd speaks SSLv3. OpenSSL 3.x REMOVED SSLv3 entirely - the
# code is gone, so no cipher string, SECLEVEL or legacy-provider setting brings
# it back. usbmuxd carries the pairing conversation to the device correctly
# (verified: real bidirectional USB traffic, device serial enumerated), and the
# handshake then fails in libimobiledevice with lockdown error -5 / SSL error.
# Pairing is a hard prerequisite for installation_proxy and AFC, so
# ideviceinstaller / install-ipa.sh cannot work against this guest from a
# modern Linux host. Fixing it properly means vendoring an old OpenSSL.
#
# Offline injection sidesteps all of it. From imgtools/inject_apps.py:
#   "installd rebuilds the installation cache on every boot by scanning the app
#    directories. That means a bundle only has to be *present* to be
#    discovered; there is no cache file to forge."
# So a bundle dropped into /Applications is picked up on the next boot.
#
# This is the Linux port of imgtools/editimg.py, which is macOS-only (hdiutil /
# diskutil / fsck_hfs). Same three-stage shape, and the two ends are the
# fork's own pure-Python tools, unmodified:
#     dumpvol.py  NAND page files -> flat HFS+ image
#     <edit the mounted image>                       <- macOS: diskutil
#                                                       Linux: mount -t hfsplus
#     packvol.py  changed blocks  -> back into the page files
#
# The volume is UNJOURNALED (attributes 0x80000100, journalInfoBlock 0 - see
# imgtools/hfsfile.py), so Linux mounts it read-write without -o force and
# there is no journal to replay over the edit.
#
# NEVER run this against a NAND that a running emulator has open, and never
# against the pristine base image: it works on a COPY (nand-mgst), leaving
# nand-appsync3 untouched as the golden image.
#
# INSTALL_MODE (see LOG 2026-09-27 AUDIT B for why this matters):
#   container (default)  App Store layout: /private/var/mobile/Applications/
#                        <UUID>/{MGSTUS.app,Documents,Library/Preferences,
#                        Library/Caches,tmp}, all owned mobile (501). This is
#                        what the game ran in on real devices.
#   system               the old layout: /Applications/<app>, root-owned. Only
#                        a fallback. An App Store game installed this way has no
#                        container, so its Documents dir is /var/mobile/Documents;
#                        this mode creates that directory, because without it
#                        GSaveCtrl's fopen("SAVE.data","wb") returns NULL and
#                        fwrite(NULL) kills the app on its first launch.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ORACLE="${PROJECT_DIR}/oracle"
FW="${ORACLE}/firmware"
IMGTOOLS="${ORACLE}/qemu-ios/imgtools"
STATE="${ORACLE}/state"

# All overridable, so each IPA version (v1.0.0, v2.1.0, v2.3.0, ...) can
# be injected into its OWN working NAND (nand-mgst-v1, nand-mgst-v230, etc.)
# without clobbering an already-tested version's state.
NAND_SRC="${FW}/nand-appsync3"                    # golden; never written
NAND_DST="${NAND_DST:-${FW}/nand-mgst}"           # working copy; this is what we edit
IMG="${IMG:-${STATE}/volume.img}"
MNT="${STATE}/mnt"
APP_SRC="${APP_SRC:-${STATE}/ipa-extract/Payload/MGSTUS.app}"
INSTALL_MODE="${INSTALL_MODE:-container}"
MOBILE_UID=501   # "mobile" in the guest's /etc/passwd; apps run as this user

# GL engine replacement (contrib/it-gles/mbxshim.c). The stock MBXGLEngine
# drives the MBX GPU, which is not emulated: a GL app's main thread blocks in it
# on its first present and SpringBoard's watchdog kills it (LOG 2026-09-27 step
# 1). The shim forwards GL to QEMU's host renderer (hw/arm/gles-host.c, which
# now has a Linux/EGL backend) instead. Verified 2026-09-27: installed offline
# and loaded from boot, SpringBoard unlocks normally and MGST renders (300/300
# presents ok). An earlier "the shim freezes SpringBoard" reading was the
# idle-sleep hang below, not the shim. GL_SHIM=none keeps the stock engine;
# tools/oracle_live.sh shim-on/shim-off swaps it on a running guest.
GL_SHIM="${GL_SHIM:-${FW}/guest-tools/MBXGLEngine}"
# KEEP THE GUEST AWAKE. Measured 2026-09-27 (kernel msgbuf via imgtools/klog.py):
# ~1 min after boot the locked device runs "System Going to sleep" -> "System
# Sleep", powers the MBX and the multitouch down, and the kernel parks in its
# sleep loop (`dsb; b .` at 0xc0061eb0) waiting for a PMU power-off that this
# emulator never completes -- so the guest never wakes, buttons do nothing, and
# every run looked like a random hang (upstream lists native idle sleep/wake as
# unsolved, docs/ipod-ui-reliability.md). Step 1's "failed to suspend in time"
# kill was the same transition. SBAutoLockTime alone is not enough: the lock
# screen has its own short sleep timer. These are SpringBoard's own keys (all
# present as strings in the 7E18 binary):
#   SBDisableIdleSleep  no system idle sleep        SBDontLockEver  never lock
#   SBDisableAutoDim    no dimming                  SBDisableCABlanking  no blank
#   SBAutoLockTime -1   Settings' "Never" (General.plist)
# Upstream dropped SBDontLockEver/SBDisableCABlanking only because they break
# the Lock button, which an oracle never presses. KEEP_AWAKE=0 skips all this.
KEEP_AWAKE="${KEEP_AWAKE:-${AUTOLOCK_NEVER:-1}}"
case "$INSTALL_MODE" in container|system) ;; *) echo "INSTALL_MODE must be container or system" >&2; exit 1 ;; esac

# The volume is 1835008 blocks of 4096 (7.52 GB), read from its own header.
# The tools default to 128000, which would truncate it to 524 MB and destroy
# the filesystem - pass the real count.
BLOCKS=1835008

log() { echo "[$(date -Iseconds)] $*"; }
die() { echo "[$(date -Iseconds)] ERROR: $*" >&2; exit 1; }

[[ "$(id -u)" == "0" ]] || die "must run as root (mount): sudo $0"

# Refuse to touch a NAND an emulator has open - the guest's own writes are in
# flight and interleaving with them corrupts the volume.
if pgrep -f "qemu-system-arm.*iPod-Touch" >/dev/null 2>&1; then
    die "an emulator is running; shut it down first:
    oracle/scripts/boot_oracle.sh --shutdown"
fi

[[ -d "$APP_SRC" ]] || die "no app bundle at ${APP_SRC}
    extract it first:  cd ${STATE} && mkdir -p ipa-extract && cd ipa-extract \\
        && unzip -qq -o ${ORACLE}/apps/mgst-v2.1.0.ipa 'Payload/*'"
[[ -d "$NAND_SRC/cs0" ]] || die "no base NAND at ${NAND_SRC}"

mkdir -p "$STATE"

# ── 1. working copy of the NAND ──────────────────────────────────────────
if [[ ! -d "${NAND_DST}/cs0" ]]; then
    log "[1/6] copying base NAND -> $(basename "$NAND_DST") (~1 GB, one time)"
    rm -rf "$NAND_DST"
    cp -a "$NAND_SRC" "$NAND_DST"
else
    log "[1/6] reusing existing working NAND $(basename "$NAND_DST")"
fi

# ── 2. reassemble the page files into a flat volume ──────────────────────
log "[2/6] dumpvol: NAND pages -> ${IMG} (${BLOCKS} blocks, 7.5 GB)"
python3 "${IMGTOOLS}/dumpvol.py" --nand "$NAND_DST" --out "$IMG" --blocks "$BLOCKS"

# ── 3. mount read-write ──────────────────────────────────────────────────
mkdir -p "$MNT"
LOOP="$(losetup --find --show "$IMG")"
log "[3/6] mounting ${LOOP} read-write at ${MNT}"
cleanup() {
    mountpoint -q "$MNT" && umount "$MNT" || true
    [[ -n "${LOOP:-}" ]] && losetup -d "$LOOP" 2>/dev/null || true
}
trap cleanup EXIT

mount -t hfsplus -o rw "$LOOP" "$MNT" \
    || die "mount failed - is the hfsplus module available? (modprobe hfsplus)"

# ── 4. install the bundle ────────────────────────────────────────────────
# installd rebuilds its cache by scanning BOTH /Applications and
# /var/mobile/Applications/*/ on every boot, so either location is found.
APP_NAME="$(basename "$APP_SRC")"
USER_APPS="${MNT}/private/var/mobile/Applications"

# Remove any earlier copy of this bundle from either location first: two
# bundles with the same identifier make SpringBoard pick one arbitrarily.
rm -rf "${MNT}/Applications/${APP_NAME}"
for old in "$USER_APPS"/*/"$APP_NAME"; do
    [[ -d "$old" ]] || continue
    log "      removing earlier container $(basename "$(dirname "$old")")"
    rm -rf "$(dirname "$old")"
done

if [[ "$INSTALL_MODE" == container ]]; then
    UUID="$(python3 -c 'import uuid; print(str(uuid.uuid4()).upper())')"
    CONTAINER="${USER_APPS}/${UUID}"
    DEST="${CONTAINER}/${APP_NAME}"
    log "[4/6] installing ${APP_NAME} as a user app: /private/var/mobile/Applications/${UUID}/"
    mkdir -p "$CONTAINER"/{Documents,Library/Preferences,Library/Caches,tmp}
    cp -a "$APP_SRC" "$CONTAINER/"
    OWNER_ROOT="$CONTAINER"
    OWNER="${MOBILE_UID}:${MOBILE_UID}"
else
    DEST="${MNT}/Applications/${APP_NAME}"
    log "[4/6] installing ${APP_NAME} into /Applications (system app)"
    cp -a "$APP_SRC" "${MNT}/Applications/"
    OWNER_ROOT="$DEST"
    OWNER="0:0"
    # A system app's Documents directory is /var/mobile/Documents. The stock
    # image does not have one; without it the game's first save kills it.
    mkdir -p "${MNT}/private/var/mobile/Documents"
    chown "${MOBILE_UID}:${MOBILE_UID}" "${MNT}/private/var/mobile/Documents"
    chmod 755 "${MNT}/private/var/mobile/Documents"
    log "      created /private/var/mobile/Documents (mobile, 0755)"
fi

# Ownership and modes are not cosmetic. A bundle owned by the host user is not
# owned by anyone real in the guest, and an executable stored 0644 fails
# posix_spawn with EACCES - which SpringBoard reports as "exited abnormally with
# exit status 1" and writes NO crash report, reading exactly like an emulator bug.
chown -R "$OWNER" "$OWNER_ROOT"
find "$OWNER_ROOT" -type d -exec chmod 755 {} +
find "$OWNER_ROOT" -type f -exec chmod 644 {} +
EXE="$(python3 - "$DEST/Info.plist" <<'PY'
import plistlib, sys
print(plistlib.load(open(sys.argv[1], "rb")).get("CFBundleExecutable", ""))
PY
)"
[[ -n "$EXE" ]] || die "could not read CFBundleExecutable"
chmod 755 "${DEST}/${EXE}"
log "      executable ${EXE} -> 0755, owner ${OWNER}"

# GL engine replacement. The stock binary is kept beside it as
# MBXGLEngine.stock exactly as upstream's install-ipa.sh does, and is never
# overwritten once saved, so re-running cannot lose the original.
GLB="${MNT}/System/Library/Frameworks/OpenGLES.framework/MBXGLEngine.bundle"
if [[ "$GL_SHIM" != none ]]; then
    [[ -f "$GL_SHIM" ]] || die "GL shim not found at ${GL_SHIM} (run: python3 tools/extract_guest_tools.py, or GL_SHIM=none)"
    [[ -f "${GLB}/MBXGLEngine.stock" ]] || cp -p "${GLB}/MBXGLEngine" "${GLB}/MBXGLEngine.stock"
    cp "$GL_SHIM" "${GLB}/MBXGLEngine"
    chown 0:0 "${GLB}/MBXGLEngine" "${GLB}/MBXGLEngine.stock"
    chmod 755 "${GLB}/MBXGLEngine" "${GLB}/MBXGLEngine.stock"
    log "      GL shim installed from $(basename "$GL_SHIM") (stock kept as MBXGLEngine.stock)"
fi

if [[ "$KEEP_AWAKE" == 1 ]]; then
    PREFS="${MNT}/private/var/mobile/Library/Preferences"
    if [[ ! -d "$PREFS" ]]; then
        mkdir -p "$PREFS"
        chown "${MOBILE_UID}:${MOBILE_UID}" "$PREFS"
    fi
    python3 - "${PREFS}/com.apple.springboard.plist" <<'PY'
import os, plistlib, sys
p = sys.argv[1]
d = {}
if os.path.exists(p):
    with open(p, "rb") as f:
        d = plistlib.load(f)
d.update({"SBAutoLockTime": -1, "SBDisableIdleSleep": True,
          "SBDontLockEver": True, "SBDisableAutoDim": True,
          "SBDisableCABlanking": True})
with open(p, "wb") as f:
    plistlib.dump(d, f, fmt=plistlib.FMT_BINARY)
PY
    chown "${MOBILE_UID}:${MOBILE_UID}" "${PREFS}/com.apple.springboard.plist"
    chmod 600 "${PREFS}/com.apple.springboard.plist"
    log "      keep-awake prefs set (no idle sleep, never lock, no dim/blank, auto-lock Never)"
fi

# Diagnostic: which engine the image now carries.
if [[ -f "${GLB}/MBXGLEngine" ]]; then
    log "      MBXGLEngine: $(stat -c%s "${GLB}/MBXGLEngine") bytes$([[ -f "${GLB}/MBXGLEngine.stock" ]] && echo ' (shim installed)' || echo ' (STOCK - no shim)')"
fi

df -h "$MNT" | tail -1 | sed 's/^/      /'
sync

# ── 5. unmount and check before writing anything back ────────────────────
log "[5/6] unmounting and checking the volume"
umount "$MNT"
FSCK_OUT="$(fsck.hfsplus -f -n "$LOOP" 2>&1 || true)"
echo "$FSCK_OUT" | tail -5 | sed 's/^/      /'
case "$FSCK_OUT" in
    *"appears to be OK"*|*"appears OK"*) ;;
    *) die "fsck is not happy; REFUSING to write back. The working NAND is unchanged." ;;
esac

# ── 6. write the changed blocks back into the page files ─────────────────
log "[6/6] packvol: changed blocks -> NAND page files"
python3 "${IMGTOOLS}/packvol.py" --img "$IMG" --nand "$NAND_DST" --blocks "$BLOCKS" --apply

# Hand the NAND back to the user who invoked sudo, or QEMU (unprivileged)
# cannot read it and the next boot dies with a permissions error.
if [[ -n "${SUDO_UID:-}" ]]; then
    chown -R "${SUDO_UID}:${SUDO_GID:-$SUDO_UID}" "$NAND_DST"
    [[ -f "$IMG" ]] && chown "${SUDO_UID}:${SUDO_GID:-$SUDO_UID}" "$IMG"
fi

# The overlay for this NAND recorded guest writes against the PREVIOUS
# contents of these blocks; replayed over the new ones it would shadow them.
OVL="${STATE}/nandrw-$(basename "$NAND_DST")"
if [[ -d "$OVL" ]]; then
    log "      discarding stale overlay $(basename "$OVL") (it describes the old base)"
    rm -rf "$OVL"
fi

log "DONE. Boot it:"
log "    NAND=${NAND_DST} oracle/scripts/boot_oracle.sh"
