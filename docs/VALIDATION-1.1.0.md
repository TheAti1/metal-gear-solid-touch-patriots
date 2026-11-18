# Language infrastructure validation — 1.1.0

Windows x64, Intel HD Graphics 620, 2026-11-18.

| Check | Result |
|---|---|
| WPF launcher + embedded templates | Built successfully |
| Windows native host | Rebuilt main.c and linked successfully; generated AOT game module unchanged |
| Source template coverage/IDs/tokens | 161 launcher / 549 game entries passed |
| Isolated importer | UI-only/game-only, combined ZIP, UTF-8 runtime table and binary plist passed |
| Protected data | Source changes, duplicate/unknown IDs, font-record injection, lost format tokens and path traversal rejected |
| Failed compile rollback | Missing HUD dependency left previous installed game bytes intact |
| Component update/cache | Launcher reimport refreshed text and preserved compiled game |
| Fallback/export | Missing game component, broken installed UI and template export passed |
| Native community locale | Loaded pt-qa overlay and all 890 binary-plist rows; desktop control heading rendered from the imported game JSON |
| Portuguese font coverage | Liberation Sans regular/bold contain ÁáÀàÂâÃãÉéÊêÍíÓóÔôÕõÚúÜüÇç |
| HUD generation | VIDA generated for normal/iPad atlases; all pixels outside the LIFE rectangle remained identical |
| Launcher UI | English, Turkish and partial test-locale pages rendered; community locale/independent game selection reviewed |
| Discord protocol | Existing handshake/activity/heartbeat/clear mock passed; custom game locale passed including translated mission/status text |
| Existing launcher binding/plist check | Passed |

The deliberately partial `pt-qa` fixture is not a Brazilian Portuguese translation release and is not shipped. Contributor JSONs have blank text values, with language headers preset to pt-BR. The original English/Turkish catalogues retain their frozen source/ID/font metadata.

This change modifies the desktop host's locale/text lookup and launcher. It does not regenerate or alter the recovered game module, boss logic, camera or input-navigation code. Existing historical reports retain their original executable hashes. The twenty-mission playthrough, all boss fights and every original illustration were not rerun/reviewed for this infrastructure release; the actual completed translation still needs an in-game layout review before being bundled as official support.
