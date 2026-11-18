# Metal Gear Solid Touch · Patriots PC v1.0.8

**Windows x64 · English / Türkçe · iOS 2.3.0-derived AOT port**

## İndir / Download

- **MGS_Touch_Patriots_PC_v1.0.8.zip** — complete playable package. Extract all files, open **Metal Gear Solid Touch.exe**.
- **MGS_Touch_Patriots_PC_v1.0.8_Guncelleme.zip** — update for an existing Patriots Touch installation; not a standalone game. Back up `Saves/`, then extract over the installation.
- Matching `.sha256` files verify the two downloads.
- Corresponding launcher and PC tool sources are attached separately and included in the full package.

## Dahil / Included

Independent English/Turkish launcher and game languages; display/audio/input/save/Discord settings; configurable keyboard and SDL gamepads; relative mouse aim; long-text scrolling; hover tint; aspect-ratio-preserving fullscreen; Turkish font coverage and JSON/REX localization workflow. The launcher hides while playing and returns after exit.

## Son düzeltmeler / Latest fixes

- **1.0.8:** post-game Survival advice is landscape and its Next / İleri button works through controller confirm, RT and Enter.
- **1.0.7:** corrected left/right final-boss dodge direction.
- **1.0.6:** mission-20 right-stick dodge, neutral rearming and held-input protection.
- **1.0.5:** Mantis doll shake with animated R-stick prompt; result/retry/advice confirmation and held-fire protection.
- Earlier: history orientation, long-text scrolling, hover colors, menu/pause mappings, camera freeze, native icons and launcher lifecycle.

## Kayıtlar ve hileler / Saves and modifiers

This distribution contains **no personal save**. Modifiers are off by default. Switching language shares your save. Existing installations retain `Saves/`, `settings.json` and `Oyun/desktop.ini` when using the update archive.

## Technical scope

Based on etruj's decompilation and mgs-retouched foundation. The matching iOS/ARMv6 game is recovered to C locally, compiled through wasm32/wasm2c and delivered as Windows x64 code. No runtime ARM instruction emulator or iOS emulator is required.

Focused tests and their executable hashes are documented in `Dogrulama.json` and the repository validation notes. Historical tests retain their original hashes. The full game was not played through as one fresh unassisted regression, and full native game compilation does not run in CI without original matching inputs. Launcher/source checks run independently in GitHub Actions.

Original game and game material: Konami / Kojima Productions. Platform/decompilation: etruj. Windows integration and Turkish translation: Patriots Çeviri. Component licenses and corresponding source accompany the package. This is an independent fan release.
