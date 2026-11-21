# Patriots PC 1.2.1 · Verified Windows build

This release responds to the VBA32 `Downloader.MSIL.gen.rexp` report on the two PC 1.2.0 ZIPs. It improves build transparency; it does **not** claim that VBA32 has withdrawn the report or that RecompLauncher has approved the listing.

- The C# launcher is built from this tag's public source on a fresh GitHub-hosted Windows runner using pinned .NET SDK 9.0.320. Two separate builds must produce the same SHA256.
- Explicit product/publisher/file-version information and an `asInvoker` application manifest identify the executable and its normal-user privilege level. No obfuscator, executable packer or self-signed trust certificate is added.
- The full and update ZIPs include `BUILD-PROVENANCE.json`, per-file hashes and the prepared-install `recomplauncher.json` at the ZIP root. Release assets include `SHA256SUMS.txt` and GitHub artifact attestations.
- English, Turkish, Brazilian Portuguese, language import, controller mappings, boss gestures and Discord Rich Presence remain available.
- The native Windows game executable, SDL3 and game/language assets are carried forward byte-for-byte from the hash-pinned PC 1.2.0 release. They are **not** rebuilt or presented as source-built by this workflow. Android releases are separate.

**New installation:** extract `MGS_Touch_Patriots_PC_v1.2.1.zip` and run `Metal Gear Solid Touch.exe`.

**Existing installation:** extract `MGS_Touch_Patriots_PC_v1.2.1_Guncelleme.zip` over the existing game folder. Neither archive contains personal settings or save files.

RecompLauncher can start the prepared package directly and edit the existing 19 settings / 12 keyboard bindings. Listing approval and antivirus verdicts remain with RecompLauncher and the scanner vendors. See [build evidence and verification](https://github.com/TheAti1/metal-gear-solid-touch-patriots/blob/main/docs/WINDOWS-RELEASE-SECURITY.md).
