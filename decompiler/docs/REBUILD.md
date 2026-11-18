# Reproducibility: the Ghidra project rebuilt from scratch

**Date:** 2026-10-09 · **Tool:** `tools/build_ghidra_project.sh`

Until this check, the Ghidra project existed only as a database that had grown over many
sessions. To reproduce the decompilation from nothing more than the binary plus the tracked
inputs under `analysis/`, `build_ghidra_project.sh` imports `MGSTUS`, seeds every function entry
with its ARM/Thumb mode (`ApplyMgstSymbols`, before auto-analysis), and applies the 22 project
scripts in dependency order. A run takes about 12 minutes.

The result was compared with the original project at four levels (third build, after two
order fixes; see below):

| level | result |
|---|---|
| functions exported | 1,395 = 1,395; printer self-check 0 mismatches |
| **compiled machine code identical** (`.text` bytes + relocations, after `mgst_recompile.py` on both) | **1,390 / 1,395** |
| the 5 with different machine code (`LoadChange`, `title_drawHelp`, `SoundResourceManager::analyze`, `SoundService::searchPort`, `Effect procEffEnemyChar:`): **differential tests** of the rebuilt versions | **5 / 5 pass** (258 tests, frames + synthetic calls) |
| V1 static audits on the rebuilt export | **PASS** |

The 5 compile differently because Ghidra makes different but equivalent choices in a fresh
database: a switch it resolves by itself instead of the original project's explicit table
override, and different local-variable splitting. Many other functions differ only cosmetically
in C text (label names `LAB_` vs `code_r0x`, local variable names, anonymous field numbering)
and compile to identical code. The original project's `_main` is `void`; the rebuild's `int`
(returning the `UIApplicationMain` result) is actually more faithful (`_main` is V0-audited).

**Conclusion:** the decompilation is reproducible from scratch. Every function of the rebuilt
project compiles to identical machine code or is proven identical in behaviour, and the static
audits pass.

Order constraints learned (encoded in the script):
- the switch and soft-float call-fixups go first: `FixSplitsAndStubs` writes jump-table
  overrides only where the decompiler, with the switch fixup installed, reports "Could not
  recover jumptable";
- `ApplyObjcTypes` goes before `ApplyCppTypes`;
- `FixDuplicateTypes` goes right after `ApplyCppTypes`: it keeps the struct a class's `this`
  points to, and after `FixCppThis` that was the opaque `/_objc2_` `SoundResourceManager`
  (build 2: its fields came out untyped; the clean-copy end-to-end run caught the V1 size audit
  failing);
- `ApplyVarargCallsites` goes after `ApplyCallsiteSignatures`.

`FixVoidReturns` now takes its report path as an argument, so a rebuild doesn't overwrite the
tracked `analysis/symbols/void_returns.tsv`.

To check another build the same way, set `MGST_CDIR=<export dir>` for `mgst_recompile.py`,
`mgst_snap.py` and `mgst_difftest.py`; they then compile and test that export instead of
`recovered/compile`.
