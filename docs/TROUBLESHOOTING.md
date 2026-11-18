# Troubleshooting / Sorun giderme

## Save and update safety

Back up `Saves/` before updates. Keep `Saves/SAVE.data`, `settings.json` and `Oyun/desktop.ini` from your own installation. Update archives contain no personal save or settings. Do not copy a developer QA save into a new distribution. Switching language uses the same user save.

## Cheats / Hileler

The downloadable clean package uses the original gameplay rules by default. Infinite life and one-hit kills are off. To explicitly disable modifiers, close the game and set these lines in `Saves/retouched.cfg`:

```ini
cheat_infinite_life=0
cheat_one_hit_kills=0
cheat_open_all_missions=0
cheat_open_all_wallpapers=0
```

This stops modifiers; it does not erase earned/unlocked progress or undo an already-completed mission. The boss assistance used during development is not part of ordinary launch behavior.

## Cannot confirm after death

Use the mapped confirm button or release and press RT again. Wait for the result animation; very early input may expire. Versions 1.0.5+ expose the retry advice as well as the result and Ready screens. Check for duplicate/remapped bindings in the launcher.

## Final-boss dodge feels reversed

Use 1.0.7 or later. Dodge is enabled only in mission 20. Centre the right stick and push left/right again. Holding the stick does not repeat. Do not confuse the Mantis left/right shake gesture in mission 18 with the final-boss dodge.

## Sideways post-game advice / İleri does nothing

Use **1.0.8 or later** and restart the game to load the updated EXE. The Survival unlock advice is a separate game scene; it now receives landscape presentation and the original Next button mapping. Existing saves remain compatible.

## Long text / special history

Scroll with right-stick Y, wheel or Page Up / Page Down. Left stick changes selection. History picture/text pages use landscape; their menus return to portrait. F1 toggles input help if it covers text.

## Black screen, scaling or fullscreen

Extract the entire ZIP and keep `Oyun`, `Arayuz`, `Localization` and the root EXE together. Use a writable folder. Update the GPU's OpenGL driver if needed, lower render scale and try windowed mode. F11 toggles fullscreen. Borders preserve the original image proportions; Fill does not add new world geometry.

## Discord

Keep the desktop Discord client open and enable presence in the launcher. Mission sharing has a separate toggle. No bot or secret token is required. The launcher stays alive in the background while its window is hidden during the game; starting the native EXE directly bypasses that launcher-managed presence process.

## Report a bug

Include release version, mission / screen, language, bindings, controller type and reproduction steps. Add a screenshot or a short redacted log excerpt. Do not publish an IPA, original executable, save, credentials or unredacted personal paths.
