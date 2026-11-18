#!/usr/bin/env bash
# Stand up the iOS "oracle": QEMU emulating an iPod touch 2G running iOS 3.1.3,
# with MGST injected, so the original game can be run side by side with the
# Android port.
#
# Built to need ONE invocation. Every stage is idempotent and checks its own
# result, so if a later stage fails, re-running skips everything already done
# rather than starting over. Each stage prints STAGE n/6 so progress is
# visible in launch.log.
#
# Corrections to the handoff guide, all verified against this machine before
# writing (any one of these would have failed a first run):
#   * `libsdl2-devel` does not exist on Fedora 43 - it ships SDL3, and the
#     SDL2 development package is `sdl2-compat-devel`.
#   * The firmware release assets are named bootrom_240_4 / nor_n72ap.bin /
#     nand_n72ap.zip, not bootrom.bin / nor.img / nand.img. The NAND is a ZIP
#     and must be extracted.
#   * The app bundle is MGSTUS.app, not MGST.app.
set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
ORACLE="${PROJECT_DIR}/oracle"
FW="${ORACLE}/firmware"
SRC="${ORACLE}/qemu-ios"
SUDO="${SUDO:-sudo}"

REPO_URL="https://github.com/samhenrigold/qemu-ios.git"
REPO_BRANCH="ipod_touch_2g"

# The handoff guide pointed at devos50's n72ap_v1 release. That image is
# iPhone OS **2.1.1** (build 5F138) — the fork's own RUNNING.md shows
# `ProductVersion: 2.1.1` in its ideviceinfo sample, and its USB mux patch is
# documented as "verified only against 2.1.1 / build 5F138".
#
# The current images live on samhenrigold's own release and are **iOS 3.1.3
# (7E18)**, which is both newer and the target the app-install tooling in
# imgtools/ is written against. `nand-appsync3` is the variant already
# patched to install unsigned (sideloaded) apps; `nand-canonical` is stock and
# cannot install them.
REL="https://github.com/samhenrigold/qemu-ios/releases/download/ipod-touch-2g-2026.08"
# The release's SHA256SUMS predates a re-upload of the NAND archive; GitHub's own
# asset digest (and the copy this project was verified with) is this one.
NAND_VERIFIED_SHA="050c285bf61e15d13cb6f0bc0cc33f086f90325ff7ef98b0eccec8089af22467"

log()  { echo "[$(date -Iseconds)] $*"; }
warn() { echo "[$(date -Iseconds)] WARN: $*" >&2; }
die()  { echo "[$(date -Iseconds)] ERROR: $*" >&2; exit 1; }

mkdir -p "$FW" "${ORACLE}/reports"

# ── STAGE 1/6 — host dependencies ────────────────────────────────────────
log "STAGE 1/6: host dependencies"
PKGS=(
    git gcc gcc-c++ make cmake ninja-build meson flex bison
    glib2-devel pixman-devel libpng-devel libjpeg-turbo-devel
    sdl2-compat-devel openssl-devel
    libusbmuxd-devel libimobiledevice-devel libimobiledevice-utils
    python3-devel python3-pip zlib-ng-devel
    # libslirp-devel is NOT optional if -netdev user is ever needed: the
    # runtime .so is often present without it (other packages pull it in as a
    # shared-lib dependency), but configure only compiles QEMU's slirp glue
    # when the -devel headers are present, and does so SILENTLY — a missing
    # libslirp-devel does not fail configure, it just produces a qemu-system-arm
    # that rejects `-netdev user` at boot with "not compiled into this binary".
    # Cost a rebuild the first time this was needed (OTA app install over the
    # emulated WiFi). See LOG 2026-09-22.
    libslirp-devel
    # ── usbmuxd-qemu bridge build (app install path) ──
    # The forked usbmuxd (samhenrigold/usbmuxd @ qemu-backend) is an autotools
    # project and configure.ac hard-requires libusb-1.0 (the libusb backend
    # usb.c still compiles alongside usb-qemu.c). Without these, autogen.sh /
    # configure cannot run. See LOG 2026-09-22 (app install).
    autoconf automake libtool libusb1-devel
    # Host-side install tooling install-ipa.sh drives: iproxy (ssh tunnel to
    # the guest) ships in libusbmuxd-utils; ideviceinstaller manages the app.
    libusbmuxd-utils ideviceinstaller
    # ── Linux GL host for the guest's GLES (patches/qemu-ios-linux-egl.patch) ──
    # EGL/egl.h + the `egl`/`opengl` pkg-config modules come from
    # libglvnd-devel; Mesa supplies the actual EGL vendor and drivers. Without
    # them meson silently falls back to gles-host-stub.c and every GL app
    # renders black. See LOG 2026-09-27 (step 4).
    libglvnd-devel mesa-libEGL mesa-dri-drivers
    # ssh into the running guest (tools/oracle_live.sh), root/alpine
    sshpass
)
# meson is required and is the dependency most often left out (RUNNING.md
# calls this out explicitly). guestfs-tools/hfsutils are NOT needed: the NAND
# ships as raw chip dumps, not a mountable filesystem image - see stage 2.
MISSING=()
for p in "${PKGS[@]}"; do
    rpm -q "$p" >/dev/null 2>&1 || MISSING+=("$p")
done
if [[ ${#MISSING[@]} -eq 0 ]]; then
    log "  all ${#PKGS[@]} packages already installed"
else
    log "  installing ${#MISSING[@]}: ${MISSING[*]}"
    $SUDO dnf install -y "${MISSING[@]}" >/dev/null 2>&1 \
        || die "dnf install failed; run manually: sudo dnf install -y ${MISSING[*]}"
    STILL=()
    for p in "${MISSING[@]}"; do rpm -q "$p" >/dev/null 2>&1 || STILL+=("$p"); done
    [[ ${#STILL[@]} -eq 0 ]] || die "still missing after install: ${STILL[*]}"
    log "  installed OK"
fi

# ── STAGE 2/6 — firmware ─────────────────────────────────────────────────
# Public GitHub release (devos50/qemu-ios, tag n72ap_v1). No Apple download
# and no key extraction is involved.
log "STAGE 2/6: firmware images"

# Exact asset sizes, read from the GitHub API — NOT from its rounded "0.1 MiB"
# display, which is how a 65536-byte bootrom first got a 100000-byte floor and
# was rejected after downloading perfectly.
fetch() {  # url dest exactbytes
    local url="$1" dest="$2" want="$3"
    if [[ -f "$dest" ]] && [[ $(stat -c%s "$dest") -eq $want ]]; then
        log "  $(basename "$dest") already present (${want} bytes)"
        return 0
    fi
    log "  downloading $(basename "$dest") (${want} bytes) ..."
    # --fail so an HTML error page is never saved as if it were firmware;
    # --silent so curl's progress meter does not flood launch.log.
    curl -fsSL --retry 3 --retry-delay 2 -o "${dest}.part" "$url" \
        || { rm -f "${dest}.part"; return 1; }
    local got; got=$(stat -c%s "${dest}.part")
    if [[ $got -ne $want ]]; then
        rm -f "${dest}.part"
        warn "$(basename "$dest"): expected ${want} bytes, got ${got}"
        return 1
    fi
    mv "${dest}.part" "$dest"
    log "  got $(basename "$dest")"
}

fetch "${REL}/SHA256SUMS"    "${FW}/SHA256SUMS"         421 || warn "no SHA256SUMS; skipping verification"
fetch "${REL}/bootrom_240_4" "${FW}/bootrom_240_4"    65536 || die "bootrom download failed"
fetch "${REL}/nor_7E18.bin"  "${FW}/nor_7E18.bin"   1048576 || die "nor download failed"

# The NAND is NOT a mountable disk image. It unpacks to a directory of raw
# chip dumps (cs0..cs3) that the emulated flash controller reads directly, so
# the handoff guide's `guestmount -a nand.img -m /dev/sda1` injection cannot
# work against it. Apps go in over USB instead (imgtools/install-ipa.sh).
NAND_DIR="$(find "$FW" -maxdepth 2 -type d -name 'cs0' -printf '%h\n' 2>/dev/null | head -1)"
if [[ -n "$NAND_DIR" ]]; then
    log "  NAND already extracted: ${NAND_DIR} ($(du -sh "$NAND_DIR" | cut -f1))"
else
    fetch "${REL}/nand-appsync3.tar.gz" "${FW}/nand-appsync3.tar.gz" 272474586 \
        || die "nand download failed"
    # Verify, but distinguish "corrupt download" from "upstream re-uploaded the
    # asset without regenerating SHA256SUMS". Observed 2026-09-21: bootrom and
    # nor verify against this same SHA256SUMS while the NAND does not, yet the
    # NAND is exactly the byte length GitHub reports and passes `gzip -t`.
    # A truncated or mangled transfer fails the gzip CRC; this does not. So the
    # checksum record is stale, not the artifact. Warn loudly and continue
    # rather than blocking, and never skip the check silently.
    if [[ -f "${FW}/SHA256SUMS" ]]; then
        log "  verifying checksum ..."
        if ( cd "$FW" && grep ' nand-appsync3.tar.gz$' SHA256SUMS | sha256sum -c - >/dev/null 2>&1 ); then
            log "  checksum OK"
        else
            if [[ "$(sha256sum "${FW}/nand-appsync3.tar.gz" | cut -d' ' -f1)" == "$NAND_VERIFIED_SHA" ]]; then
                log "  matches the copy this project was verified with (GitHub's digest; SHA256SUMS is stale)"
            else
            warn "nand-appsync3.tar.gz does NOT match the published SHA256SUMS."
            warn "  expected $(grep ' nand-appsync3.tar.gz$' "${FW}/SHA256SUMS" | cut -d' ' -f1)"
            warn "  actual   $(sha256sum "${FW}/nand-appsync3.tar.gz" | cut -d' ' -f1)"
            log  "  falling back to archive integrity ..."
            gzip -t "${FW}/nand-appsync3.tar.gz" 2>/dev/null \
                || die "archive is also corrupt (gzip CRC failed) - delete it and re-run"
            warn "  gzip CRC passes and the size is exact, so the archive is intact;"
            warn "  treating SHA256SUMS as stale upstream metadata."
            fi
        fi
    fi
    log "  extracting NAND (260 MiB) ..."
    tar -xzf "${FW}/nand-appsync3.tar.gz" -C "$FW" || die "nand extract failed"
    NAND_DIR="$(find "$FW" -maxdepth 2 -type d -name 'cs0' -printf '%h\n' 2>/dev/null | head -1)"
    [[ -n "$NAND_DIR" ]] || die "no cs0 directory found after extract; got: $(ls "$FW")"
    log "  extracted ${NAND_DIR}"
fi
echo "$NAND_DIR" > "${FW}/.nand_path"

# ── STAGE 3/6 — clone ────────────────────────────────────────────────────
log "STAGE 3/6: qemu-ios source"
if [[ -d "${SRC}/.git" ]]; then
    log "  repo already cloned"
else
    git clone --branch "$REPO_BRANCH" --depth 1 "$REPO_URL" "$SRC" >/dev/null 2>&1 \
        || die "git clone failed"
    log "  cloned $REPO_BRANCH"
fi
[[ -f "${SRC}/configure" ]] || die "no configure script in ${SRC}"

# Our local changes to the fork, kept as patches so a re-clone cannot lose them.
# qemu-ios-linux-egl.patch: gles-host.c gains a Linux/EGL context backend, so
# the guest's GL ES reaches a real host GL here instead of the stub.
# qemu-ios-plugins-mgst.patch: contrib/plugins/drcov_mgst.c (per-process
# coverage) + snap_mgst.c (entry-state capture, LOG 2026-10-07); formerly
# qemu-ios-drcov-mgst.patch. drcov_mgst.c is the per-process
# (MGSTUS-identity-gated) coverage plugin behind `boot_oracle.sh --coverage`.
for p in "${ORACLE}/patches/"*.patch; do
    [[ -f "$p" ]] || continue
    if git -C "$SRC" apply -R --check "$p" >/dev/null 2>&1; then
        log "  patch $(basename "$p") already applied"
    elif git -C "$SRC" apply "$p"; then
        log "  applied patch $(basename "$p")"
    else
        die "patch $(basename "$p") does not apply to ${SRC}"
    fi
done

# ── STAGE 4/6 — configure ────────────────────────────────────────────────
log "STAGE 4/6: configure"
BUILD="${SRC}/build"

# QEMU's configure builds a Python venv and needs distlib. Python 3.14 on this
# box does not ship it, which fails as the opaque "Ouch! ... found no usable
# distlib" that RUNNING.md warns about. User-site install, no root required.
if ! python3 -c 'import distlib' >/dev/null 2>&1; then
    log "  installing distlib (required by QEMU's venv bootstrap) ..."
    pip install --user distlib >/dev/null 2>&1 \
        || die "could not install distlib; try: pip install --user distlib"
fi
python3 -c 'import distlib' >/dev/null 2>&1 || die "distlib still unimportable"

# configure refuses to reuse a build dir it did not create, and bails with
# "dir already exists and was not previously created by configure" — including
# for `--help`. A half-made directory therefore poisons everything after it.
if [[ -d "$BUILD" && ! -f "${BUILD}/build.ninja" ]]; then
    log "  removing stale build dir"
    rm -rf "$BUILD"
fi

if [[ -f "${BUILD}/build.ninja" ]]; then
    log "  already configured (build.ninja present)"
else
    # Minimal flags on purpose. The handoff guide's extra --disable-* options
    # (capstone/pie/slirp/fuse) are macOS workarounds; none are listed by this
    # configure's --help and none are needed on Fedora. Probing for them was
    # also unreliable — with a stale build dir present, `--help` itself errors
    # and every flag reads as "unsupported".
    log "  configuring (--target-list=arm-softmmu --enable-sdl)"
    ( cd "$SRC" && ./configure --target-list=arm-softmmu --enable-sdl ) \
        > "${ORACLE}/reports/configure.log" 2>&1 \
        || { tail -30 "${ORACLE}/reports/configure.log"; \
             die "configure failed - full log at oracle/reports/configure.log"; }
    [[ -f "${BUILD}/build.ninja" ]] \
        || die "configure exited 0 but produced no build.ninja"
    log "  configured OK"
fi

# Two post-configure fixes, both required on Fedora 43 / GCC 15:
#
# 1. werror. configure writes `werror = true` into the meson cross file
#    whenever .git exists on Linux — which it does, because we cloned. This
#    fork predates several GCC warnings (unused-variable, implicit-fallthrough
#    in hw/intc/pl192.c), so the build dies on warnings that are not defects.
# 2. libcrypto. hw/arm/ipod_touch_pke.c calls BN_free/BN_CTX_free but nothing
#    links OpenSSL, so the final link fails with undefined references. The
#    handoff guide's --extra-ldflags="-lcrypto" was right about this; dropping
#    it when moving to "minimal flags" is what reintroduced the failure.
#    Passing it via `meson configure` works where the cross file's
#    c_link_args does not - the latter is ignored for this target.
if grep -q '^werror = true' "${BUILD}/config-meson.cross" 2>/dev/null; then
    log "  disabling werror (old fork vs modern GCC)"
    sed -i 's/^werror = true/werror = false/' "${BUILD}/config-meson.cross"
    ( cd "$BUILD" && meson setup --reconfigure . .. ) >/dev/null 2>&1 \
        || warn "meson reconfigure after werror change reported an error"
fi
if ! ( cd "$BUILD" && meson configure 2>/dev/null | grep -q 'c_link_args.*lcrypto' ); then
    log "  adding -lcrypto (ipod_touch_pke.c needs OpenSSL BIGNUM)"
    ( cd "$BUILD" && meson configure -Dc_link_args="-lcrypto" ) >/dev/null 2>&1 \
        || warn "could not set c_link_args; link may fail"
fi

# ── STAGE 5/6 — build ────────────────────────────────────────────────────
log "STAGE 5/6: build qemu-system-arm (several minutes)"
QEMU_BIN=""
for c in "${BUILD}/qemu-system-arm" "${BUILD}/arm-softmmu/qemu-system-arm"; do
    [[ -x "$c" ]] && QEMU_BIN="$c" && break
done
if [[ -n "$QEMU_BIN" ]]; then
    log "  already built: $QEMU_BIN"
else
    ninja -C "$BUILD" qemu-system-arm > "${ORACLE}/reports/build.log" 2>&1 \
        || { tail -40 "${ORACLE}/reports/build.log"; \
             die "build failed - full log at oracle/reports/build.log"; }
    for c in "${BUILD}/qemu-system-arm" "${BUILD}/arm-softmmu/qemu-system-arm"; do
        [[ -x "$c" ]] && QEMU_BIN="$c" && break
    done
    [[ -n "$QEMU_BIN" ]] || die "build reported success but no qemu-system-arm found"
    log "  built: $QEMU_BIN"
fi
# the two capture plugins from patches/qemu-ios-plugins-mgst.patch (coverage, snapshots)
ninja -C "$BUILD" contrib/plugins/libdrcov_mgst.so contrib/plugins/libsnap_mgst.so \
    >> "${ORACLE}/reports/build.log" 2>&1 \
    || { tail -40 "${ORACLE}/reports/build.log"; die "plugin build failed - see oracle/reports/build.log"; }
log "  plugins: libdrcov_mgst.so, libsnap_mgst.so"

# ── STAGE 6/6 — verify ───────────────────────────────────────────────────
log "STAGE 6/6: verify"
"$QEMU_BIN" --version 2>&1 | head -2 | sed 's/^/  /' || die "qemu binary will not run"
if "$QEMU_BIN" -M help 2>/dev/null | grep -qi 'ipod'; then
    log "  iPod touch machine type present:"
    "$QEMU_BIN" -M help 2>/dev/null | grep -i ipod | sed 's/^/    /'
else
    warn "  no iPod machine type in -M help; the branch may be wrong"
fi

# ── guest GL engine (MBXGLEngine shim) ───────────────────────────────────
# The guest's GL goes to the host through upstream's MBXGLEngine replacement, an
# armv6 guest binary shipped inside upstream's macOS app, an asset of the same
# release as the firmware (not listed in its SHA256SUMS; GitHub's asset digest is
# MACOS_ZIP_SHA). tools/extract_guest_tools.py explains why it cannot be built
# here. Downloaded by default (262 MB); MGST_MACOS_ZIP=/path uses a local copy,
# MGST_MACOS_ZIP_URL=<url> another source.
MACOS_ZIP_SHA="99c3385da09295473648f0728a7345ee3afb7d5c98ab3f415a0830787f7d0bfb"
MACOS_ZIP="${ORACLE}/downloads/iPod-touch-2G-macOS.zip"
if [[ -f "${FW}/guest-tools/MBXGLEngine" ]]; then
    log "  guest GL engine already extracted"
else
    mkdir -p "${ORACLE}/downloads"
    if [[ ! -f "$MACOS_ZIP" && -n "${MGST_MACOS_ZIP:-}" ]]; then
        cp "$MGST_MACOS_ZIP" "$MACOS_ZIP"
    elif [[ ! -f "$MACOS_ZIP" ]]; then
        url="${MGST_MACOS_ZIP_URL:-${REL}/iPod-touch-2G-macOS.zip}"
        log "  downloading upstream's macOS release zip for the guest GL engine (262 MB) ..."
        curl -fsSL --retry 3 --retry-delay 2 -o "${MACOS_ZIP}.part" "$url" && mv "${MACOS_ZIP}.part" "$MACOS_ZIP" \
            || die "download of ${url} failed (or set MGST_MACOS_ZIP=/path/to/iPod-touch-2G-macOS.zip)"
    fi
    got="$(sha256sum "$MACOS_ZIP" | cut -d' ' -f1)"
    if [[ "$got" == "$MACOS_ZIP_SHA" ]]; then
        log "  macOS zip checksum OK"
    else
        warn "macOS zip hash differs from the verified one (${got}); continuing"
    fi
    python3 "${PROJECT_DIR}/tools/extract_guest_tools.py" "$MACOS_ZIP" "${FW}/guest-tools" \
        || die "could not extract the guest tools"
    log "  guest GL engine extracted"
fi

# ── stage the oracle IPA ─────────────────────────────────────────────────
# The app the oracle runs is YOUR OWN copy of MGS Touch v2.3.0 (the build this
# project decompiles; it runs on the 3.1.3 guest once installed offline with
# tools/inject_app_offline.sh). Pass its path in MGST_IPA; nothing is fetched.
ORACLE_IPA="${MGST_IPA:-}"
APPS="${ORACLE}/apps"
mkdir -p "$APPS"
if [[ -n "$ORACLE_IPA" && -f "$ORACLE_IPA" ]]; then
    if [[ -f "${APPS}/mgst.ipa" ]]; then
        log "  oracle IPA already staged"
    else
        cp "$ORACLE_IPA" "${APPS}/mgst.ipa"
        log "  staged oracle IPA ($(du -h "${APPS}/mgst.ipa" | cut -f1))"
    fi
else
    warn "set MGST_IPA=/path/to/your/MGS-Touch-v2.3.0.ipa to stage the app"
fi

cat > "${ORACLE}/reports/setup_summary.txt" <<EOF
qemu binary : ${QEMU_BIN}
firmware    : ${FW}
nand        : $(cat "${FW}/.nand_path" 2>/dev/null)
source      : ${SRC}
oracle ipa  : ${APPS}/mgst.ipa  (your own copy, v2.3.0)
generated   : $(date -Iseconds)
EOF

log ""
log "SUCCESS: oracle toolchain ready."
log "  qemu     : ${QEMU_BIN}"
log "  firmware : ${FW}"
log "Next: sudo tools/inject_app_offline.sh  (installs the app into the NAND image)"
