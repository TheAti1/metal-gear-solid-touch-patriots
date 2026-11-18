#!/usr/bin/env bash
# Root shell into the RUNNING emulated iPod, over the slirp port-forward that
# `oracle/scripts/boot_oracle.sh --net` sets up (127.0.0.1:$SSH_PORT -> guest
# 10.0.2.15:22). The image's sshd starts at boot (launchd label
# com.openssh.sshd); the root password is upstream's default, alpine.
#
#   tools/oracle_live.sh wait              block until sshd answers (<= ~3 min)
#   tools/oracle_live.sh sh '<command>'    run a command as root, print output
#   tools/oracle_live.sh put <local> <remote>
#   tools/oracle_live.sh shim-on           GL engine -> shim (live)
#   tools/oracle_live.sh shim-off          GL engine -> stock (live)
#
# shim-on/shim-off swap the GL engine on a RUNNING guest, the way upstream's
# install-ipa.sh does over ssh: only processes started afterwards load the new
# file. The normal path is simpler -- tools/inject_app_offline.sh installs the
# shim offline and it works from boot (verified 2026-09-27) -- so these are for
# A/B-testing stock vs shim without re-injecting.
#
# NO CLEAN POWER-OFF with the keep-awake prefs: SBDontLockEver disables the Lock
# button that boot_oracle.sh --shutdown's "slide to power off" gesture needs,
# and the image has no halt/reboot binary. Use `sh 'sync; sync'` (forces HFS+
# to write its catalog and volume header), then stop QEMU.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SSH_PORT="${SSH_PORT:-2222}"
PASS="${DEVICE_PASSWORD:-alpine}"
SHIM="${SHIM:-${PROJECT_DIR}/oracle/firmware/guest-tools/MBXGLEngine}"
B=/System/Library/Frameworks/OpenGLES.framework/MBXGLEngine.bundle

OPTS=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
      -o LogLevel=ERROR -o PreferredAuthentications=password
      -o PubkeyAuthentication=no -o ConnectTimeout=15)

gsh()  { sshpass -p "$PASS" ssh "${OPTS[@]}" -p "$SSH_PORT" root@127.0.0.1 "$@"; }
gput() { sshpass -p "$PASS" scp -O "${OPTS[@]}" -P "$SSH_PORT" "$1" "root@127.0.0.1:$2"; }

case "${1:-}" in
    wait)
        # sshd is one of the last things a fresh boot starts.
        for _ in $(seq 36); do
            if out=$(gsh 'uname -m; sw_vers 2>/dev/null || true' 2>&1); then
                echo "$out"; exit 0
            fi
            sleep 5
        done
        echo "no ssh answer on 127.0.0.1:${SSH_PORT}: ${out:-}" >&2; exit 1 ;;
    sh)   shift; gsh "$*" ;;
    put)  gput "$2" "$3" ;;
    shim-on)
        [[ -f "$SHIM" ]] || { echo "no shim at $SHIM (python3 tools/extract_guest_tools.py)" >&2; exit 1; }
        gput "$SHIM" /tmp/MBXGLEngine.new
        gsh "cp -n $B/MBXGLEngine $B/MBXGLEngine.stock; cp /tmp/MBXGLEngine.new $B/MBXGLEngine && chmod 755 $B/MBXGLEngine && ls -l $B" ;;
    shim-off)
        gsh "[ -f $B/MBXGLEngine.stock ] && cp $B/MBXGLEngine.stock $B/MBXGLEngine && chmod 755 $B/MBXGLEngine; ls -l $B" ;;
    *)
        sed -n '2,12p' "$0"; exit 2 ;;
esac
