# Metal Gear Solid Touch · Patriots PC v1.1.0

## Community language packs

The launcher now imports independent **launcher/game JSONs** and combined ZIP packs from **LANGUAGES**. New locale IDs appear in the selectors. Launcher and game language remain independently selectable. Blank/missing text uses English; existing Turkish JSONs remain compatible.

- **161 launcher texts** and **549 game/runtime/HUD texts** in separate contributor files.
- Protected source IDs, format tokens and original font data; full UTF-16 binary-plist reconstruction.
- Localized PC help, Mantis doll/right-stick hints, final-boss dodge hints and Discord mission/status labels.
- Automatic LIFE bitmap label rendering using the bundled font, preserving the remaining atlas pixels.
- Template export, component progress, failed-import rollback, English fallback and a completed-JSON upgrade tool.
- Existing saves, input mappings and AOT game/boss logic are retained.

**English and Turkish remain the completed bundled languages. Brazilian Portuguese files are blank contributor templates.** Official Portuguese support follows review of the actual completed translation.

## Translator handoff — just two files

[pt-BR.launcher.json](https://github.com/TheAti1/metal-gear-solid-touch-patriots/blob/main/localization/launcher/pt-BR.launcher.json) · [pt-BR.game.json](https://github.com/TheAti1/metal-gear-solid-touch-patriots/blob/main/localization/game/pt-BR.game.json)

Translate only `text`, preserve all source/ID fields and placeholders, and return both files. Font names and other technical records are excluded. Unchanged proper names should be copied into `text`. [Translation guide](https://github.com/TheAti1/metal-gear-solid-touch-patriots/blob/main/docs/TRANSLATING.md).

## Downloads

- **MGS_Touch_Patriots_PC_v1.1.0.zip** — complete Windows x64 package.
- **MGS_Touch_Patriots_PC_v1.1.0_Guncelleme.zip** — update for 1.0.8; close the launcher/game and replace matching files. No personal save/settings file is included. Back up any edited translation templates.
- **MGS_Touch_Translation_Kit_v1.1.0.zip** — separate launcher/game JSONs, guides and the upgrade tool.
- Matching SHA256 sidecars verify each ZIP. Corresponding launcher/native integration source is included with the playable packages; original IPA/generated game C is not added to Git.

## Türkçe

Mobile'daki çeviri teslimi Touch'a uyarlandı: çevirmene **161 metinlik launcher** ve **549 metinlik oyun JSON'unu** gönder. İkisinde de yalnızca `text` alanları çevrilir. Tamamlanan dosyalar DİLLER bölümünden kurulabilir. Klavye/gamepad yardımı, boss ipuçları, LIFE göstergesi ve Discord metinleri de bu yapıya dâhildir. Portekizce henüz hazır resmî dil değildir; gelen çeviri incelendikten sonra eklenecek.

Focused importer, native locale, HUD pixel preservation, font coverage and mock Discord checks passed. The complete twenty-mission game was not replayed for this update. [Validation details](https://github.com/TheAti1/metal-gear-solid-touch-patriots/blob/main/docs/VALIDATION-1.1.0.md).
