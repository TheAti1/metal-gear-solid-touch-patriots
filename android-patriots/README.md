# Patriots Android · Touch

Android APK v1.0.2, Android 9/API 28 or newer. The distributed universal APK includes arm64-v8a, armeabi-v7a and an x86_64 build for emulators/compatible devices. Actual performance depends on the device and OpenGL driver.

## Play

Install the APK and open the Patriots launcher. Choose Turkish/English and press PLAY. Game data is bundled; no emulator setup or separate ROM installation is required. Touch retains the original touch gestures/phone orientation. Mobile provides virtual controls and its native settings overlay. Saves are stored separately from immutable game assets.

The launcher checks GitHub Releases on startup (can be disabled) and has a manual check button. A newer **android-vMAJOR.MINOR.PATCH** release with the correctly named APK triggers a download prompt. The app verifies the asset SHA256, app package, increasing versionCode and signing certificate before opening Android's installer. Android installation permission/confirmation still belongs to the user. Offline/check errors do not block PLAY.

**Pushing a source commit alone does not update a phone. Publish a newly built and signed APK release.** PC version tags/assets are ignored. Keep the signing key: losing/changing it prevents an in-place update and save-preserving replacement.

## Build prerequisites (Windows)

- JDK 21 (`JAVA_HOME`), Python 3.11+ + Pillow, CMake/Ninja on PATH.
- Android SDK platform 35, build-tools 35.0.0, NDK 29.0.14206865 (`ANDROID_HOME`).
- `PATRIOTS_ANDROID_WORK` defaults to `D:/Patriots_Android`. It holds caches/dependencies/signing material, never inside Git.
- A prepared Windows game package in `PATRIOTS_PC_PACKAGE` (default `package/`), providing the locally supplied game assets. No game bundle is committed here.
- SDL3-3.4.18 and unicorn-2.1.4 sources under `PATRIOTS_ANDROID_WORK/deps/` for Mobile; source URLs/checksums remain pinned in `runtime/android/build.py`.
- Mobile's Unicorn configure needs a POSIX shell/strings; default scripts use MSYS2 at `C:/msys64/usr/bin`. Build Windows-compatible shims for `strings`/`pkg-config` if needed. On Windows Unicorn's archive post-build symlink may be replaced with a regular copy; no administrator permission is needed.
- Touch needs the locally recovered `mgst_w2c.c` / matching headers (`PATRIOTS_TOUCH_GEN`), WABT wasm2c runtime (`PATRIOTS_WABT`) and FreeType 2.13.3 sources (`PATRIOTS_FREETYPE`). Defaults refer to the existing `D:/Patriots_MGS_Touch_PC` developer workspace. Recovered original game C stays local.

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21.0.10'
$env:ANDROID_HOME='D:\Patriots_Android\sdk'
$env:PATRIOTS_ANDROID_WORK='D:\Patriots_Android'
$env:PATRIOTS_PC_PACKAGE='C:\Games\MGS Touch'
$env:PATRIOTS_ANDROID_ABIS='arm64-v8a,armeabi-v7a,x86_64'
python android-patriots/build.py 1.0.2
```

The builder writes the APK and SHA256 to `outputs/Android/`, verifies APK signatures and 16 KB native-library alignment, and uses the stable private key in the work folder's `signing/`. **Back up that folder privately. Do not upload it.** The Android launcher/updater is MIT-licensed; native runtime component licenses remain as documented in the repository.

## Publish an update

1. Build a higher version, e.g. `python android-patriots/build.py 1.0.3` using the same private key.
2. Create a non-draft, non-prerelease GitHub release tagged `android-v1.0.3` in this repository. It need not become the latest PC release.
3. Upload `MGS_Touch_Patriots_Android.apk` plus its `.apk.sha256` sidecar. Keep the filename stable between updates.
4. On next launcher startup, installed older versions offer the new APK. Game assets may be refreshed but personal save files/settings are not part of the update payload.

## Checks

`UpdatePolicyTest.java` covers Android tag ordering, PC-channel exclusion, trusted asset URLs and checksum syntax. Compile/run it with `UpdatePolicy.java` using javac/java. Android device/emulator checks cover launcher, native boot, save preservation and package installation separately. APK signature/ZIP checks are build-time checks; they do not establish performance on every physical phone.

Large APK downloads use bounded 4 MiB HTTP ranges and up to four connection attempts per range. A transient connection failure resumes from the bytes already written in the current download; final SHA256 and signature verification still cover the complete APK.

Automatic checks also run when the launcher returns to the foreground, at most once per minute. Returning from installation permission settings resumes the pending install without showing another update offer.
