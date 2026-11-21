# Changelog / Sürüm notları

## Android 1.1.1 · 2026-11-21

- Fix persistent clipping/displacement after rotating the native game: refresh real EGL drawable dimensions during presentation and after swaps, and service surface redraw callbacks.
- Keep GL resources across surface loss, preserve upright scene axes independently of window shape, and use stable natural sensor axes.
- Reconstruct the legacy renderer's clean game canvas before updates; paused redraws never re-capture the already composited screen. Fit small fallback drawables.
- Cancel touch/overlay/controller/gyro state on rotation and focus/surface loss; align controller cursor axes with the current view in menus as well as missions.
- Reproduce the old failure, test 20 actual OS rotations across both rendering paths, and exercise paused mission/resume/aiming round trips. Add C cancellation regression and a real-device rotation script. [Validation scope](docs/ANDROID-ROTATION.md).

## PC 1.2.0 / Android 1.1.0 · 2026-11-21

- Rebuild the Android launcher with the PC artwork, palette, navigation and a fixed Play footer.
- Remove the launcher portrait lock; support full-width landscape tablets, portrait tablets, narrow windows and larger fonts.
- Add separate display, controls, audio, language/credit, save export and update pages, preserving native preferences and save storage.
- Bundle reviewed Brazilian Portuguese as the third official PC/Android language: 161 launcher and 549 game/runtime/HUD texts, credited to [(Sanju Vinho e Fumaça)](https://steamcommunity.com/id/SanjiVinsmokeBRASIL/).
- Keep submitted wording/tokens, generate VIDA in both atlas sizes, add missing reference-mark font coverage and include pt-br in the RecompLauncher language choices.
- Present Touch landscape scenes upright in actual Android windows; transform touch coordinates and tablet sensor axes with the presentation.
- Retain the Windows native executable, recovered game module, controls and Discord integration.

## RecompLauncher support update · 2026-11-19

- Add a prepared-install Levels 1/2 profile with 19 settings, 12 keyboard bindings, exact save locations, log/folder actions, OpenGL detection and native exit messages.
- Add the opt-in `--recomplauncher` mode using the existing preferences/native launch path and Discord session, with no WPF window and no launcher reopening after game exit. Normal entry points and native gameplay/graphics are unchanged.
- Include the profile in launcher builds, CI artifacts and an asset/save-free support-update package; add the theme-aware README badge and an explicit standards audit.
- Check the official schema, all settings through 72 actual C# preference/INI round trips, real native game lifetime, no-argument WPF startup and the existing lifecycle regression. Full RecompLauncher client UI, fresh player-owned-IPA setup and new standalone game distribution are outside this update.

## Android 1.0.2

- Correct the Android system/installer application label.


## Android 1.0.1 · 2026-11-18

- Standalone Android 9+ universal APK for ARM64, ARMv7 and x86_64, with bundled game data and Turkish / English selection.
- Startup/manual release checks, ranged downloads with retry, SHA256/package/signature checks and Android installer handoff.
- Native game lifetime isolated from the launcher, with save data kept separate from immutable assets.


## 1.1.0 — 2026-11-18
- Added generic community language IDs and independent launcher/game JSON or combined ZIP import, component coverage and template export.
- Separated 161 launcher strings and 549 translatable game/runtime/HUD entries into stable contributor JSONs. Font names and other original technical records remain protected internally.
- Added dynamic locale overlays and desktop hint/boss/Discord text lookup while retaining the original AOT game module and existing control behavior.
- Added automatic bitmap LIFE-label localization from bundled English atlas references; other atlas pixels are preserved.
- Added Brazilian Portuguese contributor templates, translation guides, a completed-JSON upgrade tool and isolated importer/source/Unicode/IPC checks. Portuguese is not a completed official language yet.
- Kept the older Turkish JSON importer, shared saves, remapped keyboard/gamepad controls and original English/Turkish data.

## 1.0.8 — 2026-11-18
- Post-game Survival unlock advice uses landscape orientation.
- Controller confirm / RT / Enter target its original Next / İleri button.
- Focused test verifies original advice exit and portrait-menu restoration.

## 1.0.7 — 2026-11-18
- Corrected the final-boss dodge direction inversion from the original phone gesture coordinates.

## 1.0.6 — 2026-11-18
- Mission 20 only: right-stick left/right invokes the original dodge.
- Requires neutral rearming; held, vertical, post-loading and post-pause inputs do not repeat a dodge.

## 1.0.5 — 2026-11-18
- Mantis doll uses actual right-stick direction reversals or the mapped shake action.
- Animated R-stick prompt while the doll is equipped, localized for English/Turkish.
- Shake is queued to the original game tick instead of disappearing between desktop accelerometer calls.
- Early result confirmation waits for the result animation; RT can confirm menus.
- Retry advice receives controller confirmation; held fire through death does not auto-retry.

## 1.0.4
- Hover/selection colors replace outline boxes.
- Special/history picture and text pages render landscape and return to portrait menus.
- History scroll supports right stick, wheel and page keys; pause hover matches the clicked action.

## 1.0.3
- Right-stick scrolling for long story/help text.
- Removed virtual-pointer/selection boxes.
- Loading no longer produces unintended analog touches or held-confirm state.

## 1.0.2
- Rebuilt menu input around actual game targets and separate selection / confirm / back / pause actions.
- Fixed pause hit testing, resume defaults, result/next-mission input and remapping conflicts.
- Held axes must return to neutral in new contexts; quit confirmation defaults to No.

## 1.0.1
- Rebased relative aim to prevent negative previous-touch coordinates and camera lockups.
- Added native taskbar/window icons, launcher hide/restore lifecycle and in-game website links.

## 1.0
- Windows x64 AOT game host, bilingual WPF launcher, supplied Turkish translation, Turkish fonts, native input/audio/graphics integration and Discord presence.
