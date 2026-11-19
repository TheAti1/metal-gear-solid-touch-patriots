# RecompLauncher developer report

## What I added

- **Levels 1 and 2 for prepared Windows installations:** a root `recomplauncher.json`, 19 settings with 12 keyboard bindings, exact save paths, log/folder actions, OpenGL identification and native/adapter exit messages.
- An explicitly requested **`--recomplauncher`** mode. It shares the existing `Preferences` and process-creation path with WPF, starts no WPF window, retains the existing Discord session and returns the native exit code only after the game has closed. Without this argument, normal startup and WPF game lifecycle are unchanged.
- Manifest inclusion in the launcher build, CI artifact, staging helper and an **asset-free support-update ZIP**. That ZIP updates a complete prepared installation; it is deliberately not advertised as a standalone automatic-install build.
- The exact theme-aware README badge from the SDK, linked to the RecompLauncher home page. The checked public catalog had no entry matching `TheAti1/metal-gear-solid-touch-patriots` on 2026-11-19; no catalog ID was invented.
- Product code is committed separately from profile, packaging and documentation. No Mobile files, native gameplay/graphics code, save format, config format, original game files or keys were added/changed for this integration.

## What I checked, and how

- Read the complete agent guide, both worked examples and its embedded schema before editing. The profile is validated against the published Draft 7 schema.
- Built the actual WPF launcher with .NET Framework. The existing 161-launcher / 549-game catalogue coverage, protected metadata and tokens remain unchanged.
- A real prepared Windows native game was launched through the new mode in an isolated test folder. The parent had no WPF window, stayed alive while the native process ran, returned its successful exit code and did not reopen the Patriots window.
- Started the executable **without arguments**: the original Patriots WPF interface still opened and closed normally. The existing `--test-lifecycle` native/WPF regression also passed.
- The C# settings probe exercises all profile choices/defaults, slider endpoints and 12 bindings using the real `Preferences.Load/Save`, including both generated INIs and unchanged synthetic save bytes. The schema/packager test injects fake game and personal files and checks they are excluded from the update archive.
- No `dumps` values were supplied. The project documents only the expected inner MGSTUS executable SHA256; it does not provide an independently verified full-IPA CRC32/size suitable for that SDK field.

## Things that would make this recomp better

| Standard / gap | Why it matters | Approximate work |
|---|---|---|
| Player-owned game setup and asset-free standalone releases | Existing prepared releases bundle game assets. A clean install should accept the player's decrypted iOS 2.3.0 IPA or extracted app, validate it and build required locale resources locally. No new game files were added in this adapter; that existing distribution boundary is not silently relabelled as compliant. | **Large:** reusable IPA/folder setup, version/hash checks, localization resource generation, release migration and fresh-install tests. |
| `--game <path>` and packaged IPA input | The native host still reads its installed asset directory. An explicit path and an opt-in windowless setup step would remove manual placement and enable a real Easy Setup input screen. CHD, RVZ, console keys and other-console formats do not apply to this iOS port. | **Medium**, as part of the setup work above. |
| Authoritative dump verification | The current binary hash validates the developer input, but it cannot establish a full archive's CRC32 or award a verified-dump badge. | **Small/medium research:** document a legitimate verified archive variant before adding `dumps`; do not guess one. |
| Standalone platform-labelled release assets | Current full PC ZIP names say PC, not Windows/x64. The new support ZIP has explicit platform/architecture but must not be mistaken for a full install. | **Small** naming/packaging change after standalone setup is ready. |
| Linux / Steam Deck and macOS releases | The desktop port still uses WPF and Windows-specific host code; upstream Android support does not supply these desktop builds. | **Large:** cross-platform launcher/host work and hardware validation. |
| Per-user fallback for read-only installs | Saves/settings are portable in a writable folder; an unwritable folder still fails rather than moving consistently to a per-user location. | **Medium:** one shared location resolver across native game, WPF, profile and migration tests. |
| Rotating runtime/launcher logs | The native runtime replaces its log and the WPF log appends; players can lose useful prior-run evidence or accumulate a long log. | **Small:** bounded rotation before each session, retaining the existing locations. |
| Fully verified controller-only flow | SDL3, remapping, game menus, retry and text scrolling already exist, but the whole 20-mission game and all Patriots setup/import dialogs were not validated without a keyboard. RecompLauncher currently edits keyboard bindings; numeric controller mappings remain in Patriots. | **Medium:** controller UI/adapter mapping and a full controller regression pass. |
| Recomp Achievements | No achievement adapter exists. Achievements, Beaten/Mastered status and leaderboards would give players persistent goals beyond the existing save/Discord telemetry. | **Medium/large:** integrate [RecompAchievements](https://github.com/elripalda/RecompAchievements), define reliable game events and validate unlocks. |

Already present: versioned GitHub releases and notes, readable JSON/INI configuration, portable saves in writable installs, known log paths, SDL3 controls, a ZIP-based no-admin install, no automatic Windows first-start downloads, and a short README play guide. Gameplay timing, shaders, upscalers, achievements and platform formats were not invented or altered by this adapter.

## Anything I was not sure about

- **Client UI:** the complete RecompLauncher desktop client was not run. Its schema and raw JSON-value contract are checked, and the actual launcher/native process path is tested. The Developer tab should still be reviewed in the real client.
- **Listing:** no matching public catalog entry was found. The README badge therefore does not imply listing or approval.
- **Fresh install:** this support update needs an existing complete prepared package. It must not replace the current full game download or be selected as a standalone automatic-install asset. `game`, `prepare` and verified-dump claims are intentionally absent.
- **External visual filters:** the profile declares the real OpenGL backend. ReShade presets themselves have not been visually tested, so compatibility with every preset is not certified.
- No physical controller matrix, full twenty-mission playthrough or new Android release is claimed.

## Make it yours on RecompLauncher

A free [developer account](https://recomplauncher.com/dev), using GitHub sign-in, lets you claim the repository. After approval the page can show the Verified developer badge; you can manage its art/page, see statistics and player reports with logs, and have new releases reach players sooner. Submit/claim the project and describe this as **prepared-install Levels 1/2 support** until the player-owned-IPA setup and asset-free standalone release work is finished. No account, claim or submission was made on your behalf.
