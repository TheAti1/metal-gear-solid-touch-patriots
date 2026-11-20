# Português (Brasil)

Official on PC 1.2.0 and Android 1.1.0. Translation: [(Sanju Vinho e Fumaça)](https://steamcommunity.com/id/SanjiVinsmokeBRASIL/).

- 161/161 launcher and 549/549 game/runtime/HUD entries are nonempty. Incoming JSON wording, protected metadata, IDs, placeholders and intentional line breaks are retained.
- The importer reconstructs the 890-record binary plist, replaces 445 localized records and compiles 635 runtime source/translation pairs. Technical font/path records remain protected.
- VIDA replaces LIFE in normal and iPad atlases; pixels outside the label rectangles are verified unchanged. Liberation Sans plus Droid fallback cover all translated characters. A small drawn U+203B reference mark was added to the Apache-licensed fallback using tools/add_pt_reference_glyph.py.
- The Windows native executable and game module are unchanged. Remapped controls, boss gestures and Discord remain available. RecompLauncher independently selects pt-br for launcher and game.
- Android uses the reviewed contributor text plus localization/android/pt-BR.android.json for platform-only launcher/updater/options messages. Shared reviewed text has priority over supplemental defaults.

Select Português (Brasil) in the launcher. Existing saves are shared across languages. Original names and unchanged technical/proper-noun text are retained as submitted; this does not mean every original texture has been redrawn.
