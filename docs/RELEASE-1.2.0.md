# Patriots PC 1.2.0 · Português (Brasil)

Brazilian Portuguese is bundled alongside Turkish and English in the launcher and game, translated by [(Sanju Vinho e Fumaça)](https://steamcommunity.com/id/SanjiVinsmokeBRASIL/).

- 161 launcher and 549 game/runtime/HUD entries; submitted wording, IDs, tokens and author credit retained.
- VIDA HUD in both original/iPad atlas sizes; complete translated character coverage including a drawn U+203B reference mark in the open Droid fallback.
- Remapped keyboard/gamepad controls, boss gestures, Discord and community JSON import remain available. RecompLauncher language settings now include pt-br.
- The Windows native executable and recovered game module are unchanged. This release adds localization and launcher metadata.

New players: extract **MGS_Touch_Patriots_PC_v1.2.0.zip** and run **Metal Gear Solid Touch.exe**. Existing players: extract **MGS_Touch_Patriots_PC_v1.2.0_Guncelleme.zip** over the current installation. The update excludes saves and personal settings; it includes the new official Portuguese overlay and fallback font. Keep your existing Saves folder and settings.

The translation kit includes the completed Portuguese reference plus blank English source templates for other languages. Runtime/font generation tools and source remain available in Git and the corresponding source archives.

Android has its separate **android-v1.1.0** release: three languages, PC-style adaptive launcher and upright landscape presentation on tablets. It is not the Windows ZIP.

Validation: real launcher/importer, rendered UI, Unicode binary plist/runtime/HUD/font checks, 74 compiled C# Preferences round trips, SDK schema, real native Portuguese menu boot, and Android phone/tablet layout checks. Physical Android devices, every translated screen and a complete playthrough remain untested. See [validation scope](VALIDATION-1.2.0.md).
