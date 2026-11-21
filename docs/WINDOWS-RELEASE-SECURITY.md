# Windows release evidence and antivirus review

## Reported PC 1.2.0 detection

RecompLauncher reported one of 74 VirusTotal engines, VBA32, with label `Downloader.MSIL.gen.rexp`. Those are the reporter's results, not an independent current VirusTotal scan by this project.

| Archive | SHA256 |
|---|---|
| PC 1.2.0 full | `1093a5cea12de2c0a9e64f7b4d8620b051ce614edd4f8c5066f5b13d041f4bd5` |
| PC 1.2.0 update | `59995e3d0651d26a5a452e49c3f67e71548f38c4f1f1199aa8054cbe9b895f45` |

Both archives contain the same three executable binaries (including nested archives checked for executables):

| File | SHA256 |
|---|---|
| Patriots C# launcher 1.2.0 | `00f7c9f54650ae5498b598682b73ffa9728831332249b6e91bee2eebe728de15` |
| Native game | `807ce36865ccc7915fbaeca7169df20c433844f1beac82f97c81d86f9b421bba` |
| SDL3 | `2b4b128d8d510cc2d442693cf848c050d700d43dc667afe9e5fd82b0570d667e` |

The MSIL label suggests the C# launcher is a review candidate, but without the vendor's inner-file report the flagged member is not confirmed. Its published source has no HTTP/file-download or update-install code. Discord presence uses local named pipes; explicit website/author buttons open a browser. Language import processes local JSON/ZIP files. Tests can copy the launcher into an isolated temporary directory only when the corresponding `--test-*` command is explicitly requested.

The original launcher passed a local Microsoft Defender custom scan (signature 1.463.399.0). This is one scanner's result and does not establish a VBA32 or VirusTotal clearance.

## PC 1.2.1 build provenance

The [Windows release workflow](../.github/workflows/release-pc.yml) builds the launcher from the checked-out source, runs the actual language/Unicode/Discord IPC/Preferences tests, compares two deterministic compiler outputs, packages the hash-verified 1.2.0 base and generates GitHub artifact attestations. Actions are pinned to commit SHAs.

`BUILD-PROVENANCE.json` records the exact source commit, workflow URL, launcher hash, base hash, unchanged native hashes and scanner status. The release ZIPs have root manifests and per-file hashes; no user settings or saves are copied. ZIP paths are checked for traversal, duplicate names and symlinks.

This workflow does **not** rebuild the recovered native game module: its inputs are absent from the public source repository. The native EXE and SDL3 are retained byte-for-byte. It does not alter gameplay, localization, input or save formats.

With the GitHub CLI, verify downloaded archives against the repository's attestations:

```sh
gh attestation verify MGS_Touch_Patriots_PC_v1.2.1.zip --repo TheAti1/metal-gear-solid-touch-patriots
gh attestation verify MGS_Touch_Patriots_PC_v1.2.1_Guncelleme.zip --repo TheAti1/metal-gear-solid-touch-patriots
```

On Windows, compare local file hashes with `SHA256SUMS.txt` using `Get-FileHash -Algorithm SHA256`. The attached `github-attestation.jsonl` is also available for verification.

## Remaining review

GitHub provenance establishes where a build came from; it is **not** Windows Authenticode code signing, a malware scan or listing approval. The launcher remains unsigned because no trusted code-signing certificate is configured.

Only the scanner vendor can change its detection. VirusTotal recommends rescanning and then contacting the detecting vendor with the report links: [official false-positive procedure and contact list](https://docs.virustotal.com/docs/false-positive-contacts). RecompLauncher can independently rescan PC 1.2.1 and review the public workflow/attestations. No zero-detection result is claimed here.
