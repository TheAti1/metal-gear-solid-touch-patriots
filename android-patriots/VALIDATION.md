# Android 1.0.2 validation

- NDK 29 release builds: arm64-v8a, armeabi-v7a, x86_64.
- Signed universal APK: v2/v3 verification; ZIP integrity; 16 KB ZIP and ELF LOAD alignment.
- Android 15/API 35 x86_64 emulator: installation, Turkish launcher glyphs, native game boot, Turkish main menu and touch navigation into Act 1.
- Shared update policy: tag ordering, Android/PC channel isolation, trusted release URLs and SHA256 syntax pass.
- Game assets contain no personal saves. Saved progress/settings live outside the APK's immutable assets.

Physical ARM phones, all missions and every controller have not been tested here. Performance and OpenGL driver behavior vary by device. The Windows-specific launcher integrations are not an Android compatibility guarantee.

The Android host is based on the pinned mgs-retouched Android host. It uses the original touch/orientation behavior, the local recovered game module, FreeType fonts and the Patriots Turkish asset overlay. Devices lacking OES framebuffer objects use a window-copy presentation fallback; that fallback is separate from the validated hardware-backed emulator FBO path.

Shared updater integration: an older signed Mobile test build downloaded the live GitHub APK in HTTP ranges, verified it and completed Android permission/installer confirmation. The actual savedata.i3d SHA256 remained aa3cded8a5ca612f3b46007b8cf0eefceaa359c3f2c66a5269ce1c4fb6e964c1; the English language preference survived. Touch transferred over 40 MB through the same ranged client and retained its real SAVE.data through in-place APK installs.
