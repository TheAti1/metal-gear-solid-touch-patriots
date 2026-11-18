# Validation and limits

The release includes `Dogrulama.json`. Public copies and focused reports are under `docs/validation/`. Each hash-bound report names the native executable it tested. Older reports remain historical evidence and are not stamped with a new binary hash after a later change.

| Area | Evidence / scope |
|---|---|
| Input / recovery | 1,395-function static handoff; 1,389 compiled game C files; original ARM / wasm32 layout checks |
| Bilingual content | 890 plist records, 52 runtime constants, protected font names and supplied Turkish text preserved |
| Fonts | Three font faces checked for required Turkish glyphs |
| Baseline runtime | English / Turkish boot, first-mission play, audio, M4 / SVD, cover, pause, Unicode-folder run |
| Desktop menus | Selection, confirm/back, controller remapping, result-to-next-mission, pause/resume and quit-cancel defaults |
| Long text / history | Right-stick up/down, wheel/Page keys, history landscape orientation and return to portrait menus |
| Mouse feedback | Button tint and pause hover agree with actual click target |
| Mission 18 | Original doll-equipped shake animation follows a right-stick direction reversal; QA-only original `setDoll` fixture used for this focused check |
| Mission 20 | Original left/right dodge states and protection; neutral rearming, held input, vertical input and pause/loading tested; direction mapping corrected in 1.0.7 |
| Post-game advice | 1.0.8 scene 13 rendered landscape; gamepad confirms original Next; returns to portrait menu in isolated fixture |
| Launcher / Discord | Launcher lifecycle and local Discord IPC protocol tests |

The final boss was also completed in an assisted local session using temporary infinite-life protection. This is not evidence of an unassisted balance test. Assistance is absent from the release defaults and personal completion saves are not distributed.

Not claimed: a fresh full-game build on every Windows version, a complete 20-mission playthrough as a single regression, a clean-room engine rewrite, complete support for every original platform API, or a full dynamic differential rerun. The public full-build workspace layout has not had a fresh clean-machine rebuild; launcher CI is independent of original game input.

GitHub Actions validates repository boundaries / translation metadata and compiles/tests the launcher. Complete game verification requires the matching local original input and graphics/audio environment.
