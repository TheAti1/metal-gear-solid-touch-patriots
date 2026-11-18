# Patches to Ghidra's decompiler: licence

[Ghidra](https://github.com/NationalSecurityAgency/ghidra) is licensed under the **Apache
License, Version 2.0**. These two patches modify files of its native decompiler
(`Ghidra/Features/Decompiler/src/decompile/cpp/`):

| patch | modified files | change |
|---|---|---|
| `subflow-exact.patch` | `subflow.hh`, `subflow.cc` | narrow double arithmetic to float only when at most one rounding operation is involved and constants are exact |
| `printc-float-nonassociative.patch` | `printc.hh`, `printc.cc` | treat float `+` and `*` as non-associative when printing |

As modifications of Apache-2.0 files, these patches are provided under the **Apache License,
Version 2.0**. `tools/ghidra_overlay.sh` applies them to a local copy of a Ghidra installation;
the original installation is never modified, and no Ghidra code is redistributed here.
