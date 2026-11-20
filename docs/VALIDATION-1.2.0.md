# Validation · 1.2.0 PC / 1.1.0 Android

- Incoming contributor JSONs match the 161/549-row source templates. All rows are nonempty; IDs, protected metadata, format tokens and wording are retained.
- The compiled Portuguese binary plist is parsed independently: all 445 localized replacements match exactly; all 635 PC runtime pairs are checked. Normal/iPad HUD pixels outside the VIDA rectangles are unchanged.
- Liberation Sans regular/bold plus Droid fallback cover all translated code points. A small original vector U+203B mark is added using the supplied font tool; no Windows font glyphs are copied.
- Real .NET launcher build, importer/self-tests and five-language-page render sets pass. The 74-case real Preferences probe runs in a fresh isolated directory; it now refuses a prepared game installation.
- Official vendored RecompLauncher schema and 19-setting/12-binding contract checks pass. PT-BR is included in both language selectors. The Windows native executable remains SHA256 `807ce36865ccc7915fbaeca7169df20c433844f1beac82f97c81d86f9b421bba`.
- A hidden Windows native run opens the Portuguese title/act menu, produces screenshots, mixes non-silent audio and exits 0 using an isolated save directory.
- Android: actual signed x86_64 APK boots the PT-BR game, advances original touch tutorial/story screens, presents a landscape story/advice scene upright and returns to the launcher. Pure C tests cover both inclinations, pause rotation retention, all pointer transform round trips and natural-landscape sensor axes.
- Both Android launchers are checked at 1280×800 tablet landscape, 800×1280 tablet portrait, 720×1280 phone and 600×800 narrow window/font scale 1.3. Play remains reachable; the launcher uses the whole window. Narrow-window sizing is simulated; OEM split-screen, foldable posture and physical ARM device performance are untested.
- ARM64, ARMv7 and x86_64 libraries are built; release APK signatures and 16 KB ZIP/native LOAD alignment are verified. Existing app data is retained by signed replacement. Playing the game can naturally rewrite its own save, so update-preservation hashes are measured before resuming gameplay.

No full playthrough, every translated screen, real gamepad on an Android device or RecompLauncher client UI rerun is claimed by this update. Existing Windows native/controller/Discord behavior is retained.
