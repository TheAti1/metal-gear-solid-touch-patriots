# RecompLauncher support — prepared Touch PC installations

This profile implements **Level 1 launch and Level 2 settings** for the existing Windows x64 Patriots package. It does not install the original iOS game from an IPA. The support update contains no game files, native game executable, save or private settings.

## Use an existing full installation

1. Start from the complete **Touch Patriots PC v1.1.0** folder. A launcher-only source build or this support update alone is not a playable game.
2. Extract the support update into that folder, replacing `Metal Gear Solid Touch.exe` and adding `recomplauncher.json` beside it. Keep `Oyun`, `Arayuz`, `Localization`, existing languages and `Saves` together.
3. In RecompLauncher, enable **Settings → Developers → Developer tools**, choose **Add a build**, and select that complete folder. A local developer build is not automatically downloaded or replaced by RecompLauncher.
4. Check the Developer tab, change a setting and press Play. The Patriots window stays closed; the native game and its existing Discord session run until the game exits.

The ordinary `Metal Gear Solid Touch.exe` entry point, without `--recomplauncher`, still opens its original WPF interface. Use it for community JSON imports, controller remapping and existing backup/restore tools. Changing a setting in either launcher uses the same `settings.json`.

The optional **SDK source bundle** also contains the corresponding launcher source under `Source/`. Its `SDK_source` filename deliberately marks it as an auxiliary asset, so RecompLauncher does not mistake a small add-on for a complete game download. Apply its root launcher/profile files over the prepared package before adding that folder as a local build.

## What the profile describes

- 19 setting rows: independent game/Patriots UI language, fullscreen, V-Sync, render scale, borders, pixel filtering, desktop frame limit, music/effects, audio quality, aiming, deadzone, vibration, keyboard bindings, focus pause, intro and Discord privacy.
- 12 keyboard actions in the existing `Keys` dictionary, using SDL key names. Controller mappings remain configurable in the Patriots interface and retain their SDL detection/defaults.
- `settings.json` is authoritative. The existing `Preferences.Load/Save` code writes `Oyun/desktop.ini` and `Saves/retouched.cfg`; the profile does not edit those generated files independently.
- Save backup paths cover `Saves/SAVE*.data` plus the three small settings files. The entire game data or log directory is not listed as a save.
- `Saves/runtime.log`, `Saves/launcher.log`, useful folder actions, OpenGL identification and real native/adapter exit messages.

On the first external launch, and only if `settings.json` does not yet exist, `RECOMPLAUNCHER_MODE=bigpicture` selects fullscreen and `desktop` selects windowed. Existing preferences are respected. Native SDL controller detection remains authoritative; `RECOMPLAUNCHER_PAD` is logged, not used to rewrite the player's bindings.

## Scope and intentionally omitted fields

The current prepared package already resolves its assets at `Oyun/Assets/MGSTUS.app`. The SDK explicitly permits omitting `game` when the recomp finds its data itself. Accordingly, this profile does not ask for a fake ISO or pretend that the native binary accepts an external IPA path.

There is no separate end-user setup/cache-building step to expose, so `prepare` is absent. `game.dumps` is also absent: the documented 2.3.0 inner Mach-O SHA256 is not an authoritative full-IPA size/CRC32 and is not converted into a made-up verification badge. The build guide and developer IPA validator retain their existing hash checks.

This is **prepared-install integration**, not a claim that the existing asset-bundled distribution meets every Recomp Standard. See [the standards audit and developer report](RECOMPLAUNCHER-REPORT.md). In particular, do not upload the small support update as a standalone automatic-install game release. A fresh Discover installation needs a complete build or a future player-owned-IPA preparation flow.

## Build, package and check

```powershell
./launcher/build.ps1 -PackageRoot 'C:\Games\Touch'
python -m pip install jsonschema==4.23.0
python tools/test_recomplauncher.py
python tools/package_recomplauncher_update.py --package 'C:\Games\Touch' --out dist
```

The launcher build copies `recomplauncher.json` to the package root. The CI artifact and support-update packager include it at the root too. When preparing a full release from a separate staging script, preserve that file beside the root EXE; `tools/include_recomplauncher.py --package <staging-folder>` explicitly performs/validates the same staging step. Never include user settings or saves in a release.

`tools/tests/RecompSettingsProbe.cs` runs against the real C# preferences implementation in an isolated build folder. It checks every profile choice/default, slider bounds and keyboard action through JSON and both generated INI files. `tools/test_recomplauncher.py` checks the official SDK schema and makes an intentionally contaminated fixture to prove that the support archive excludes game data and personal files.

The full RecompLauncher client UI has not been exercised here; schema, real C# setting serialization, native process lifetime and ordinary launcher behavior are checked separately. Open the Developer tab for the final client-side review.

Reference: [official agent/SDK guide](https://recomplauncher.com/sdk-files/recomplauncher-agent.md) and [JSON schema](https://recomplauncher.com/schema/recomplauncher.json).
