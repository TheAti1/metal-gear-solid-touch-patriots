# Add a language to MGS Touch

Version 1.1 supports independent launcher and game language packs. English and Turkish remain the completed bundled languages. **The Brazilian Portuguese files are untranslated contributor templates**, ready to send to a translator. Portuguese becomes a bundled official language after the actual completed files and in-game layouts are reviewed.

## Send exactly two JSONs

- [pt-BR.launcher.json](../localization/launcher/pt-BR.launcher.json): **161 launcher texts**, including settings, language import/export and messages.
- [pt-BR.game.json](../localization/game/pt-BR.game.json): **549 game texts**: 445 localized game strings, 52 existing runtime constant candidates, 51 desktop/control/boss/Discord labels and the bitmap HUD's LIFE label.

Every entry in these two files is translatable. Protected font names, empty records, paths and other technical data from the older extraction catalogue are excluded. The importer reconstructs all 890 original binary-plist records and preserves those technical values internally.

Translate only each entry's **`text`**. Use **`source`** as the English reference and preserve `id`, `category`, `record_id` and `required_tokens`. Keep format placeholders such as `%s`, `%d`, `%@`, `{0}`, their occurrence counts and intentional line breaks. Copy unchanged names into `text`; a blank field deliberately falls back to English. Keep short control hints concise. `language`, `native_name` and `culture` are already set for Brazilian Portuguese; the contributor may add their credit to `author`.

Return both completed JSON files. For another language, start with the corresponding [launcher](../localization/launcher/launcher.en.json) / [game](../localization/game/game.en.json) templates and change the header's language code, display name and culture.

## Import and select

Close the running game, then use **LANGUAGES → IMPORT LANGUAGE PACK**. Launcher and game JSONs can be imported independently, in either order. Use the same language code in both files. The launcher selector and game-language selector remain independent. Missing/blank launcher strings use English; a missing game component cannot replace the current game language. Saves, control mappings, native boss gestures and Discord remain available.

To import both at once, ZIP **`launcher.json` and `game.json` directly at the archive root**. Other paths, modified source metadata, duplicate IDs and lost tokens are rejected. Component imports preserve the other installed component. Validation/compilation happens in staging folders; a failed import leaves the installed pack intact.

Installed JSONs live in `Localization/Languages/<tag>/`. Compiled game assets live in `Oyun/languages/<tag>/`: `English.lproj/Localizable.strings`, optional localized HUD atlases and `runtime_text.bin`. Keeping the internal English lookup name lets the original game fall back to its English visual resources. Original shared assets and built-in Turkish files remain separate. The old `patriots.mgs-touch.localization.v1` Turkish JSON importer is still supported.

```powershell
& '.\Metal Gear Solid Touch.exe' --import-language '.\pt-BR.launcher.json'
& '.\Metal Gear Solid Touch.exe' --import-language '.\pt-BR.game.json'
& '.\Metal Gear Solid Touch.exe' --export-language-kit 'C:\Translations\Touch'
```

No Python, compiler or iPhone is needed to import/play a translated JSON.

## Fonts and bitmap text

The packaged Liberation Sans regular/bold fonts contain the Brazilian Portuguese accented characters. The JSON's `hud_life` entry rebuilds the LIFE label in the normal/iPad atlases using the bundled font. Pixels outside that label's rectangle are preserved. The unmodified English atlas references are distributed under `Oyun/languages/en/English.lproj/`, outside Git history.

Other scripts may require font/shaping work. Original instructional illustrations and credit graphics are separate visual resources, not editable font-name records; their diagrams/names should be reviewed before declaring a full new-language release. Long dialogue, history scrolling, HUD widths, pause/retry, control-device changes and the mission 18/20 hints need an in-game language review. Text translation alone does not prove all layouts fit.

## Updating completed translations

```powershell
python tools/refresh_language_json.py --input 'pt-BR.launcher.completed.json' --out 'pt-BR.launcher.updated.json'
```

The tool preserves completed text and credits by stable ID, adds new entries blank, and rejects unexpected source changes. From the standalone kit, pass `--template launcher/launcher.en.json` (or the matching game template). Do not overwrite a completed translation with a blank template.

## Validation

`tools/check_language_templates.py` checks source coverage, stable IDs, protected tokens and synchronized native build inputs. `--test-language-packs` exercises the actual importer in an isolated temporary folder without user saves. The release's language validation report records focused native/UI/Discord/font checks; the complete twenty-mission game is not rerun for each localization infrastructure change.
