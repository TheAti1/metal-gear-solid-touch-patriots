# Changelog / Sürüm notları

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
