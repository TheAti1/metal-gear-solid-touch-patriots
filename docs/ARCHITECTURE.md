# Architecture

## Source layout

| Path | Purpose |
|---|---|
| `launcher/` | Prepared C# / WPF launcher source corresponding to 1.0.8, translation import and Discord IPC |
| `runtime/` | Modified etruj mgs-retouched source, Windows SDL host, platform compatibility runtime |
| `decompiler/` | Pinned decompiler source/tooling and published upstream metadata |
| `upstream/mgs-retouched/` | Clean pinned patch baselines used by the Windows scripts |
| `tools/windows/` | Windows Ghidra, wasm32/wasm2c, host build, localization and focused regression scripts |
| `localization/` | Frozen English catalogue, supplied Turkish translation, protected font names and REX plugin |
| `assets/` | Launcher branding / UI art |
| `docs/validation/` | Release report and historical hash-bound test reports |

## Game code and runtime

The matching ARMv6 input is recovered locally to C. A wasm32 intermediate preserves the original 32-bit object and structure layout before wasm2c and the x64 compiler produce native Windows code. Objective-C messaging, UIKit-like input, image/text rendering, OpenGL ES calls, files, timers and sound use compatibility implementations. This preserves recovered game logic without interpreting the original ARM instructions at runtime.

The local handoff includes 1,395 recovered functions, of which 1,389 game C files enter the build; six switch/entry implementations are replaced. This is not proof that every platform API or every mission has complete behavioral coverage. Nil import thunks and compatibility limitations are documented by upstream tools.

## Desktop input

`patriots_pc.c` exports the desktop bridge. `patriots_fields.c` reads recovered typed state, menu targets and scroll objects. The SDL host in `windows_main.c` and shared `windows_navigation.inc` maps physical inputs to game actions and original UIKit targets.

Relative aim rebases the original touch anchor each game tick. Without rebasing, large accumulated movement could produce negative previous-touch coordinates that the recovered game interprets as no finger. Firing, cooldowns, cover, collisions and damage remain in original game logic.

Menu targets follow the game's actual scene/menu data. Pause uses a semantic desktop overlay; story, advice, Ready, result and post-game advice confirm their original button rectangles. Text scrolling drives the original scroll object and clamps to its actual extent.

## Localization and Discord

The frozen JSON contains 890 plist entries (445 text records and 445 protected font records), plus 52 runtime constants. Only text fields are editable. Turkish font coverage is reported separately. Launcher import produces the game locale files and runtime string overrides; English remains available.

The launcher reads local native game telemetry for Discord activity. Discord's desktop IPC connection is used with public Application ID `1572290325937004574`. No bot token or account password is required. Users can disable presence or mission sharing. The launcher stays alive in the background while its window is hidden during play.

## Publication boundaries

The source tree excludes the original IPA/Mach-O, generated recovered game C, build products, personal saves, logs and credentials. The downloadable prepared game package includes its required game assets, font dependencies and component notices. The full package and update are versioned separately from Git source history.
