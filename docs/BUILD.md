# Build guide

## Launcher only (no game input required)

On Windows with .NET Framework 4.x:

```powershell
./launcher/build.ps1
$test = Start-Process './package/Metal Gear Solid Touch.exe' -ArgumentList '--test-launcher' -PassThru -Wait -WindowStyle Hidden
if ($test.ExitCode -ne 0) { throw 'Self-test failed' }
```

This compiles the launcher and copies its UI assets. It does not build the game or create a complete playable package. The same check runs in GitHub Actions. Native game files and language assets are needed for normal PLAY / `--validate`.

## Original input and upstream revisions

- MGSTUS iOS **2.3.0**, unencrypted ARMv6 Mach-O (`cryptid=0`).
- Inner `MGSTUS` SHA256: `07ac5db07fb8909a95b23c791d20800237bf14a51de1cec32cd0be8e37773a9c`.
- Decompiler: `9441736930437cd1c6866463dc5b23f2f6412453`.
- mgs-retouched: `d4edb7bc1b2ea3a2ec4114a413cb86f7a5cca7ed`.

Supply your matching input locally. It is not fetched from an unofficial download site or included in Git. Other versions, including 2.3.1, can have different addresses and are not validated by this pipeline.

## Native developer workspace

These are the actual Windows development scripts, with dependency paths adjusted to this repository. The full source-to-game pipeline has substantial local prerequisites; a clean-machine full build has not been rerun from this new public layout. The already-tested delivered binaries and hash-bound reports are in Releases. Do not treat the launcher CI as a full game build.

The default working directory remains **D:\Patriots_MGS_Touch_PC**. Review script constants if using another drive. Some regression scripts intentionally capture to that default QA directory.

Repository dependencies (not committed):

```text
dependencies/
  llvm-mingw/bin/       # LLVM-MinGW 20261104 UCRT x64, Clang 23.1.5
  SDL3/include/
  SDL3/lib/x64/SDL3.lib
  SDL3/lib/x64/SDL3.dll
  ninja.exe
```

Working-directory dependencies:

```text
D:\Patriots_MGS_Touch_PC/
  tools/ghidra_11.3.2_PUBLIC/
  tools/wasi-sdk-27.../bin/clang.exe
  tools/wabt-1.0.37/build-patriots/wasm2c.exe
  tools/freetype-2.13.3/
  tools/zlib-1.3.1/
  tools/liberation-fonts-ttf-2.1.5/
  downloads/           # source archives checked by the build scripts
  mgs-decomp/
  mgs-retouched/
  package/
```

Install CMake and Python 3.11+, Pillow, fonttools and lz4 as needed by the extraction/localization tools. Ghidra uses JDK 21; review `JAVA_HOME` in its Windows scripts. SDL3 is the desktop input/audio dependency, not SDL2. WABT's wasm2c runtime, winpthreads, FreeType and zlib are linked by the native builder; component notices must accompany distribution.

## Pipeline

1. Copy `runtime/` to the working directory's `mgs-retouched/` and `decompiler/` to `mgs-decomp/`, or use `prepare_windows_work.py` after reviewing the locally supplied IPA path. Existing directories are preserved.
2. Extract the matching IPA to `mgs-decomp/work/extracted/` and verify the inner executable hash with `validate_mgs_touch_ipa.py`.
3. Build / patch Ghidra with `build_ghidra_windows.py`; run the resumable static pipeline with `decompile_windows.py`. Inspect its logs, the handoff and the readiness stamps. Generated original game material stays local.
4. Run `install_pc_bridge.py`, then `build_wasm_windows.py`. Layout checks compare original ARM and wasm32 records before linking and generating C with wasm2c.
5. Prepare `package/Arayuz/game.ico` from the launcher assets, then run `build_native_windows.py` **after** the wasm stage finishes. Never overwrite a game EXE while it is still being copied or tested.
6. Build the launcher with `launcher/build.ps1 -PackageRoot D:\Patriots_MGS_Touch_PC\package`. Copy the localization catalogue / REX plugin to `package/Localization` and required language assets to `package/Oyun/languages`.
7. Use the language-pack importer for modern launcher/game JSONs; the supplied legacy Turkish catalogue is also supported. Preserve English assets and verify font coverage. `localization_tool.py` documents the extraction/import format.
8. Start with a fresh save directory and run focused scene/input checks before producing a clean package. Include third-party notices and corresponding source.

The `.ready` files support resuming stages; an absent prerequisite can make a script wait rather than guess. Read its log instead of launching several dependent build stages concurrently.

## Useful checks

```powershell
python tools/check_repository.py
./launcher/build.ps1
```

Native developer scripts accept `--script`, `--save-dir`, `--test-seconds`, `--windowed` and `--hidden-test`. Use isolated save copies for regression tests. Test scripts / verifiers under `tools/windows/` cover menus, remapping, camera, story/history scroll, hover, Mantis gestures, the final boss dodge and post-game advice.

The post-game advice fixture initializes the original scene; it does not fabricate a boss victory. A full 20-mission playthrough or ARM-vs-native dynamic differential suite is not provided by these focused checks.

## Community language infrastructure (1.1)

The launcher build embeds the English launcher/game templates and frozen original source catalogue. `--test-language-packs` needs no original game and uses an isolated temporary directory. CI also runs `python tools/check_language_templates.py`.

Native changes are confined to the Windows host locale/overlay/text path; the generated game module remains unchanged. Both `runtime/windows/main.c` and the copied build input `tools/windows/windows_main.c` must stay synchronized. A prepared package additionally carries standard PNG English atlas references under `Oyun/languages/en/English.lproj/` for the optional HUD label generator. Those are release data, not Git inputs. See [TRANSLATING.md](TRANSLATING.md).
