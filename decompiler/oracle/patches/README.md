# Patches to qemu-ios (QEMU): licence

These patches modify and extend [QEMU](https://www.qemu.org/) as forked by the community
`qemu-ios` project. QEMU is licensed under the **GNU GPL, version 2** (with parts GPL-2.0-or-later);
these patches are derivative works of it and are therefore licensed under the
**GNU General Public License, version 2 or (at your option) any later version**, *not* under
the MIT licence of the rest of this repository.

| patch | content | origin |
|---|---|---|
| `qemu-ios-plugins-mgst.patch` | TCG plugins `drcov_mgst.c` (per-process coverage + dynamic call graph) and `snap_mgst.c` (state capture) | `drcov_mgst.c` is based on QEMU's `contrib/plugins/drcov.c`, Copyright (C) 2021 Ivanov Arkady, GPL-2.0-or-later; the notice is kept in the file header |
| `qemu-ios-linux-egl.patch` | Linux EGL backend for the emulated GPU (`hw/arm/gles-host.c`) | modifies qemu-ios source files |

The patches contain no Apple or Konami code.
