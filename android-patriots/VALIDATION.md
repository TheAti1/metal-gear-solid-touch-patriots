# Android 1.0.0 validation

- NDK 29 release builds: arm64-v8a, armeabi-v7a, x86_64.
- Signed universal APK: v2/v3 verification; ZIP integrity; 16 KB ZIP and ELF LOAD alignment.
- Android 15/API 35 x86_64 emulator: installation, Turkish launcher glyphs, native game boot, Turkish main menu and touch navigation into Act 1.
- Shared update policy: tag ordering, Android/PC channel isolation, trusted release URLs and SHA256 syntax pass.
- Game assets contain no personal saves. Saved progress/settings live outside the APK's immutable assets.

Physical ARM phones, all missions and every controller have not been tested here. Performance and OpenGL driver behavior vary by device. The Windows-specific launcher integrations are not an Android compatibility guarantee.

The Android host is based on the pinned mgs-retouched Android host. It uses the original touch/orientation behavior, the local recovered game module, FreeType fonts and the Patriots Turkish asset overlay. Devices lacking OES framebuffer objects use a window-copy presentation fallback; that fallback is separate from the validated hardware-backed emulator FBO path.
